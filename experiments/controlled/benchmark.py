"""Controlled forward model and trusted evaluation, separate from policy code.

Synthetic nuclei elongate before splitting, or split without warning. This is
an observability experiment, not a validated model of biological division.
"""
import hashlib
import time
from dataclasses import asdict

import numpy as np

from photon.adaptive import AdaptivePolicy
from photon.data import SequenceMetadata
from photon.gaussian import GaussianFitConfig
from photon.oracle import ReplayOracle
from photon.replay import RunRecord
from experiments.controlled.event_focus import EventFocusPolicy

FRAMES = 240
TOLERANCE = 1


def make_clip(seed, condition):
    if condition not in ("precursor", "abrupt", "quiet"):
        raise ValueError("Unknown controlled condition")
    rng = np.random.default_rng(seed)
    events = rng.integers(50, 211, size=4).tolist() if condition != "quiet" else []
    angles = rng.uniform(0, np.pi, size=4)
    yy, xx = np.mgrid[:64, :64]
    clip = np.zeros((FRAMES, 64, 64), dtype=np.float32)
    geometry = []
    for t in range(FRAMES):
        scene = []
        for i, (cy, cx) in enumerate(((18,18),(18,46),(46,18),(46,46))):
            cy, cx = cy + .35*np.sin(t/31+i), cx + .35*np.cos(t/37+i)
            c, s = np.cos(angles[i]), np.sin(angles[i])
            event = events[i] if events else FRAMES+100
            precursor = max(0., min(1., (t-(event-24))/24)) if condition == "precursor" else 0.
            ratio = 1 + 1.9*precursor
            positions = [(cy, cx)] if t < event else [(cy-3.8*s,cx-3.8*c),(cy+3.8*s,cx+3.8*c)]
            for y, x in positions:
                major, minor, amplitude = (1.35*ratio, 1.35, .78/ratio) if t < event else (1.1,1.1,.58)
                u, v = (xx-x)*c+(yy-y)*s, -(xx-x)*s+(yy-y)*c
                clip[t] += amplitude*np.exp(-.5*((u/major)**2+(v/minor)**2))
                scene.append({"y":float(y),"x":float(x),"major":float(major),"minor":float(minor),
                              "angle":float(angles[i]),"amplitude":float(amplitude)})
        clip[t] = np.clip(clip[t] + rng.normal(0,.003,(64,64)),0,1)
        geometry.append(scene)
    return clip, events, geometry


class ControlledSequence:
    def __init__(self, clip):
        self._clip = clip
        # No condition, event time or seed is exposed in public metadata.
        self.metadata = SequenceMetadata("controlled", "synthetic", len(clip), clip.shape[1:], "float32",
                                         source="synthetic", split="controlled", voxel_size_xyz_um=(1.,1.))
        self.fingerprint = hashlib.sha256(clip.tobytes()).hexdigest()

    def read(self, t):
        return self._clip[t]


class FixedPolicy:
    def __init__(self, phase):
        self.phase, self.name = phase, f"fixed_{phase:g}"

    def reset(self, metadata, budget, seed):
        step = (metadata.frame_count-1)/(budget-1)
        self.indices = {0, metadata.frame_count-1, *(int(np.floor((k+self.phase)*step)) for k in range(1,budget-1))}
        if len(self.indices) != budget:
            raise ValueError("Fixed schedule did not preserve budget")

    def decide(self, t, history):
        return t in self.indices

    def observe(self, frame):
        pass


def run_closed(sequence, policy, budget, seed, deadline):
    oracle = ReplayOracle(sequence, budget)
    policy.reset(oracle.public_metadata(), budget, seed)
    history, decisions = [], []
    for t in range(sequence.metadata.frame_count):
        if time.monotonic() > deadline:
            raise TimeoutError("Two-minute benchmark limit reached")
        oracle.advance(t)
        take = policy.decide(t, tuple(history))
        if type(take) is not bool:
            raise ValueError("Policy returned a nonboolean decision")
        detail = dict(getattr(policy, "last_decision", {}) or {})
        decisions.append({**detail,"t":t,"decision":"ACQUIRE" if take else "SKIP"})
        if take:
            frame = oracle.acquire(t)
            history.append(frame)
            policy.observe(frame)
    indices = oracle.finish()
    record = RunRecord(policy.name, seed, budget, indices, tuple(decisions))
    oracle.evaluate_after_run(record)
    return asdict(record)


def score(record, clip, events):
    indices = np.array(record["acquired_indices"])
    distances = [int(np.min(np.abs(indices-e))) for e in events]
    previous = indices[np.searchsorted(indices, np.arange(len(clip)), side="right")-1]
    return {"covered_events":sum(d<=TOLERANCE for d in distances),"events":len(events),
            "event_coverage":sum(d<=TOLERANCE for d in distances)/len(events) if events else None,
            "event_distances":distances,"max_age":int(np.max(np.arange(len(clip))-previous)),
            "hold_mse_all_frames":float(np.mean((clip[previous].astype(np.float64)-clip)**2))}


def policies():
    return [*(FixedPolicy(p) for p in (0.,1/3,2/3)),
            AdaptivePolicy(fit_config=GaussianFitConfig(min_voxels=8)), EventFocusPolicy()]
