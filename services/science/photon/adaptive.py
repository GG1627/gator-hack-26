"""Causal, exact-budget acquisition with integer-horizon gap feasibility.

The score is an engineering heuristic, not expected information gain or a
calibrated event probability. Only observe() receives acquired image content.
"""
from dataclasses import asdict, dataclass

import numpy as np

from photon.gaussian import GaussianFitConfig, IntensityCalibration
from photon.schemas import ObservedFrame
from photon.tracking import GaussianSceneModel, TrackingConfig


DEFAULT_CONTROLLER_VARIANT = "paced_robust"


@dataclass(frozen=True)
class ControllerConfig:
    min_gap: int = 2
    max_gap: int = 12
    uncertainty_scale_um: float = 0.75
    motion_scale_um: float = 1.0
    event_memory_frames: float = 6.0
    elongation_onset: float = 1.8
    elongation_full: float = 3.0
    uncertainty_weight: float = 0.4
    motion_weight: float = 0.25
    event_weight: float = 0.55
    gap_weight: float = 0.8
    threshold: float = 1.0
    change_scale: float = 0.02
    change_weight: float = 0.55
    feature_aggregation: str = "legacy"
    pacing_lead: int | None = None

    def __post_init__(self):
        if any(isinstance(x, bool) or not isinstance(x, int) for x in (self.min_gap, self.max_gap)) or not 1 <= self.min_gap <= self.max_gap:
            raise ValueError("Gaps must be integers with 1 <= min_gap <= max_gap")
        if self.feature_aggregation not in ("legacy", "robust"):
            raise ValueError("Unknown feature aggregation")
        if self.pacing_lead is not None and (isinstance(self.pacing_lead, bool) or not isinstance(self.pacing_lead, int) or self.pacing_lead < 0):
            raise ValueError("Pacing lead must be a nonnegative integer or None")
        values = [v for k, v in asdict(self).items() if k not in ("min_gap", "max_gap", "feature_aggregation", "pacing_lead")]
        if not np.isfinite(values).all() or min(values) < 0:
            raise ValueError("Controller parameters must be finite and nonnegative")
        if min(self.uncertainty_scale_um, self.motion_scale_um, self.event_memory_frames, self.threshold, self.change_scale) <= 0:
            raise ValueError("Controller scales and threshold must be positive")
        if not 1 <= self.elongation_onset < self.elongation_full:
            raise ValueError("Elongation thresholds must increase from at least 1")


def controller_variant(name, **kwargs):
    """Fixed development presets; no target/annotation-dependent configuration."""
    variants = {"original": {}, "paced": {"pacing_lead": 2},
                "robust": {"feature_aggregation": "robust"},
                "paced_robust": {"pacing_lead": 2, "feature_aggregation": "robust"}}
    if name not in variants:
        raise ValueError("Unknown controller variant")
    return ControllerConfig(**kwargs, **variants[name])


def feasible_completion(total, last, remaining, earliest_next, min_gap, max_gap):
    """Can exactly remaining captures cover integer horizon end=total-1?

    All inter-capture gaps are in [min_gap,max_gap]. The terminal uncovered
    age must be <= max_gap (no required final capture). First future capture q
    must lie in the intersection derived below. Integer intervals are contiguous,
    so nonempty intersection is necessary and sufficient, not a greedy estimate.
    """
    end = total - 1
    if remaining < 0 or last > end or earliest_next > total:
        return False
    if remaining == 0:
        return end - last <= max_gap
    lower = max(last + min_gap, earliest_next, end - remaining * max_gap)
    upper = min(last + max_gap, end - (remaining - 1) * min_gap)
    return lower <= upper


class AdaptivePolicy:
    def __init__(self, name="photon_adaptive", *, config=None,
                 fit_config=GaussianFitConfig(), tracking_config=TrackingConfig()):
        if name not in ("photon_adaptive", "image_change"):
            raise ValueError("Unknown adaptive policy")
        self.name = name
        self.config = (controller_variant(DEFAULT_CONTROLLER_VARIANT) if config is None and name == "photon_adaptive"
                       else ControllerConfig() if config is None else config)
        self.fit_config, self.tracking_config = fit_config, tracking_config

    def reset(self, metadata, budget, seed):
        total = metadata.frame_count
        if isinstance(budget, bool) or not isinstance(budget, int) or not 1 <= budget <= total:
            raise ValueError("Budget must be an integer in [1, frame_count]")
        c = self.config
        if not feasible_completion(total, 0, budget - 1, 1, c.min_gap, c.max_gap):
            raise ValueError("Exact budget is infeasible for min_gap/max_gap including terminal coverage")
        spacing = metadata.voxel_size_xyz_um
        if spacing is None and metadata.source != "synthetic":
            raise ValueError("Physical voxel spacing is required for adaptive microscopy replay")
        self.spacing = tuple(reversed(spacing)) if spacing is not None else (1.0,) * len(metadata.shape)
        self.model = (GaussianSceneModel(self.spacing, fit_config=self.fit_config, tracking_config=self.tracking_config)
                      if self.name == "photon_adaptive" else None)
        self.metadata, self.budget, self.seed = metadata, budget, seed
        self.indices, self.clock, self.pending = [], -1, None
        self.last_decision = None
        self.calibration = self.last_signal = None
        self.change_rate = 0.0
        self.morphology_hint = self.split_hint = self.speed_um_per_frame = 0.0

    def _components(self, t):
        c = self.config
        last = self.indices[-1] if self.indices else None
        gap = t - last if last is not None else 0
        remaining = self.budget - len(self.indices)
        desired_gap = ((self.metadata.frame_count - 1 - last) / remaining
                       if last is not None and remaining else None)
        gap_pressure = gap / max(1.0, desired_gap) if desired_gap is not None else 0.0
        uncertainty = self.model.position_uncertainty(t) if self.model is not None and last is not None else None
        uncertainty_score = min(1.0, uncertainty / c.uncertainty_scale_um) if uncertainty is not None else 0.0
        motion_score = min(1.0, self.speed_um_per_frame * gap / c.motion_scale_um)
        event_interest = max(self.morphology_hint, self.split_hint) * float(np.exp(-gap / c.event_memory_frames))
        change_score = min(1.0, self.change_rate * gap / c.change_scale)
        allowance = (self.budget if c.pacing_lead is None else
                     min(self.budget, 1 + (self.budget-1)*t // max(1, self.metadata.frame_count-1) + c.pacing_lead))
        if self.name == "photon_adaptive":
            score = c.uncertainty_weight * uncertainty_score + c.motion_weight * motion_score + c.event_weight * event_interest + c.gap_weight * gap_pressure
        else:
            score = c.change_weight * change_score + c.gap_weight * gap_pressure
        return {"last_acquired_index_before": last, "gap": gap, "desired_gap": desired_gap,
                "score": float(score), "threshold": c.threshold, "uncertainty_um": uncertainty,
                "uncertainty_score": uncertainty_score, "motion_score": motion_score,
                "event_interest": event_interest, "event_interest_kind": "observed morphology/split hint, not a probability",
                "gap_pressure": gap_pressure, "change_score": change_score,
                "predicted_risk": float(score), "risk_kind": "uncalibrated acquisition priority",
                "active_tracks": len(self.model.tracks) if self.model is not None else None,
                "morphology_hint": self.morphology_hint, "split_hint": self.split_hint,
                "speed_um_per_frame": self.speed_um_per_frame,
                "pacing_allowance": allowance, "pacing_permits_acquire": len(self.indices) < allowance}

    def decide(self, t, past_observations):
        if self.pending is not None or isinstance(t, bool) or not isinstance(t, int) or t != self.clock + 1 or t >= self.metadata.frame_count:
            raise ValueError("Decisions must advance by one; acquire pending observation first")
        if tuple(frame.index for frame in past_observations) != tuple(self.indices):
            raise ValueError("Policy observation history mismatch")
        self.clock = t
        info = self._components(t)
        remaining = self.budget - len(self.indices)
        c = self.config
        if t == 0:
            acquire, reason, can_acquire, can_skip = True, "mandatory_initial", True, False
        else:
            last = self.indices[-1]
            can_acquire = (remaining > 0 and c.min_gap <= t - last <= c.max_gap and
                           feasible_completion(self.metadata.frame_count, t, remaining - 1, t + 1, c.min_gap, c.max_gap))
            can_skip = feasible_completion(self.metadata.frame_count, last, remaining, t + 1, c.min_gap, c.max_gap)
            if not can_acquire and not can_skip:
                raise ValueError("No feasible action; acquisition state/constraints are inconsistent")
            if not can_skip:
                acquire = True
                reason = "max_gap_due" if t - last == c.max_gap else "exact_budget_deadline"
            elif not can_acquire:
                acquire = False
                reason = ("budget_exhausted" if remaining == 0 else "minimum_gap" if t - last < c.min_gap
                          else "reserve_for_future_coverage")
            else:
                high_priority = info["score"] >= c.threshold
                acquire = high_priority and info["pacing_permits_acquire"]
                reason = ("priority_threshold" if acquire else "budget_pacing" if high_priority
                          else "below_priority_threshold")
        pacing_override = acquire and not info["pacing_permits_acquire"]
        self.last_decision = {**info, "reason": reason, "can_acquire": bool(can_acquire), "can_skip": bool(can_skip),
                              "pacing_override_for_feasibility": bool(pacing_override)}
        if acquire:
            self.pending = t
        return bool(acquire)

    def observe(self, frame):
        if not isinstance(frame, ObservedFrame) or frame.kind != "MEASURED" or frame.index != self.pending:
            raise ValueError("Only the pending acquired observation may update the policy")
        if self.model is not None:
            self.model.observe(frame)
            tracks = list(self.model.tracks.values())
            speeds, elongation = [], []
            for track in tracks:
                physical_cov = track.gaussian.covariance * np.outer(self.spacing, self.spacing)
                eigenvalues = np.linalg.eigvalsh(physical_cov)
                ratio = float(np.sqrt(eigenvalues[-1] / eigenvalues[0]))
                elongation.append(float(np.clip((ratio - self.config.elongation_onset) /
                                                (self.config.elongation_full - self.config.elongation_onset), 0, 1)))
                if self.config.feature_aggregation == "legacy" or track.observations >= 2:
                    speeds.append(float(np.linalg.norm(track.velocity * self.spacing)))
            if self.config.feature_aggregation == "robust":
                self.morphology_hint = float(np.mean(elongation)) if elongation else 0.0
                self.speed_um_per_frame = float(np.median(speeds)) if speeds else 0.0
            else:
                self.morphology_hint = max(elongation, default=0.0)
                self.speed_um_per_frame = float(np.percentile(speeds, 75)) if speeds else 0.0
            events = self.model.observation_log[-1]["events"]
            splits = sum(e["kind"] == "candidate_split" for e in events)
            self.split_hint = min(1.0, splits / max(1, len(tracks) / 2))
        else:
            self.calibration = self.calibration or IntensityCalibration.from_image(frame.pixels)
            signal = self.calibration.normalize(frame.pixels)
            if self.last_signal is not None:
                self.change_rate = float(np.mean(np.abs(signal - self.last_signal))) / (frame.index - self.indices[-1])
            self.last_signal = signal
        self.indices.append(frame.index)
        self.pending = None

    def configuration(self):
        refined = self.config.feature_aggregation != "legacy" or self.config.pacing_lead is not None
        return {"policy_version": "causal-priority-v2" if refined else "causal-priority-v1", "controller_config": asdict(self.config),
                "seed_note": "deterministic; seed recorded but no RNG used",
                "gap_semantics": "inter-acquisition min/max; terminal age <= max_gap; initial capture included",
                "model_version": "causal-moment-gaussian-v1" if self.model is not None else None,
                "fit_config": asdict(self.fit_config) if self.model is not None else None,
                "tracking_config": asdict(self.tracking_config) if self.model is not None else None,
                "state_after_run": self.model.state_dict() if self.model is not None else None}
