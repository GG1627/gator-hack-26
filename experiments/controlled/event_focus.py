"""Causal morphology-triggered bursts with exact-budget feasibility guards.

The controller sees acquired pixels only. Aspect ratio is an engineering cue,
not a calibrated division probability. No simulator timing enters the policy.
"""
import numpy as np

from photon.adaptive import feasible_completion
from photon.gaussian import GaussianFitConfig, IntensityCalibration, detect_and_fit
from photon.schemas import ObservedFrame


class EventFocusPolicy:
    name = "event_focus"

    def reset(self, metadata, budget, seed):
        self.total, self.budget = metadata.frame_count, budget
        if not feasible_completion(self.total, 0, budget - 1, 1, 2, 12):
            raise ValueError("Budget cannot satisfy gap constraints")
        self.indices, self.aspect, self.calibration = [], 1.0, None
        self.fit_config = GaussianFitConfig(min_voxels=8)

    def decide(self, t, history):
        if tuple(f.index for f in history) != tuple(self.indices):
            raise ValueError("History differs from acquired observations")
        gap = t - self.indices[-1] if self.indices else 0
        target_gap = 2 if self.aspect >= 2.35 else 4 if self.aspect >= 1.65 else 12
        reason = "quiet sentinel"
        if t == 0:
            acquire, reason = True, "initial observation"
        else:
            remaining = self.budget - len(self.indices)
            can_take = gap >= 2 and remaining > 0 and feasible_completion(
                self.total, t, remaining - 1, t + 1, 2, 12)
            can_wait = feasible_completion(self.total, self.indices[-1], remaining, t + 1, 2, 12)
            acquire = bool(can_take and (not can_wait or gap >= target_gap))
            if acquire:
                reason = "budget coverage guard" if not can_wait else "shape-triggered burst" if target_gap < 12 else reason
            else:
                reason = "wait; preserve observation budget"
        self.last_decision = {"t": t, "decision": "ACQUIRE" if acquire else "SKIP",
                              "reason": reason, "aspect": self.aspect, "target_gap": target_gap}
        return acquire

    def observe(self, frame):
        if not isinstance(frame, ObservedFrame):
            raise TypeError("Only acquired ObservedFrame objects may update the controller")
        if self.indices and frame.index <= self.indices[-1]:
            raise ValueError("Observation time must increase")
        if self.calibration is None:
            self.calibration = IntensityCalibration.from_image(frame.pixels)
        components, _ = detect_and_fit(self.calibration.normalize(frame.pixels, clip=False),
                                      np.ones(frame.pixels.ndim), self.calibration.noise_sigma, self.fit_config)
        self.aspect = max((float(np.sqrt(np.linalg.eigvalsh(g.covariance)[-1] /
                                        np.linalg.eigvalsh(g.covariance)[0])) for g in components), default=1.0)
        self.indices.append(frame.index)
