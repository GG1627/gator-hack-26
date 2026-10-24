"""Trusted driver, generated artifacts and measured-frame contact sheet."""
from dataclasses import asdict, dataclass
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform

import numpy as np
from PIL import Image, ImageDraw

from photon import __version__
from photon.oracle import ReplayOracle


@dataclass(frozen=True)
class RunRecord:
    policy: str
    seed: int
    budget: int
    acquired_indices: tuple[int, ...]
    decisions: tuple[dict, ...]


def run_replay(sequence, policy, budget, seed, output):
    output = Path(output)
    if output.exists():
        raise ValueError(f"Run output exists: {output}")
    oracle = ReplayOracle(sequence, budget)
    metadata = oracle.public_metadata()
    policy.reset(metadata, budget, seed)
    history, decisions = [], []
    for t in range(metadata.frame_count):
        oracle.advance(t)
        acquire = policy.decide(t, tuple(history))
        detail = dict(getattr(policy, "last_decision", None) or {})
        if type(acquire) is not bool:
            raise ValueError("Policy decision must be bool")
        if t == 0 and not acquire:
            raise ValueError("Initial frame must be acquired within budget")
        before = budget - len(history)
        if acquire:
            frame = oracle.acquire(t)
            history.append(frame)
            policy.observe(frame)
            if policy.name in ("photon_adaptive", "image_change") and (len(history) == 1 or len(history) % 10 == 0):
                print(f"{policy.name}: acquired t={t}, {len(history)}/{budget}; {detail.get('reason')}", flush=True)
        decisions.append({"t": t, "decision": "ACQUIRE" if acquire else "SKIP",
                          "remaining_budget_before": before, "remaining_budget_after": budget-len(history),
                          "last_acquired_index": history[-1].index,
                          "reason": "precommitted baseline schedule", **detail})
    indices = oracle.finish()
    record = RunRecord(policy.name, seed, budget, indices, tuple(decisions))
    metrics = oracle.evaluate_after_run(record)
    if policy.name in ("photon_adaptive", "image_change"):
        metrics["metric_reasons"]["reconstruction_mse"] = "Phase 3 scheduling run; withheld-image scoring deferred to Phase 5"
    output.mkdir(parents=True)
    code_hash = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob("*.py")):
        code_hash.update(path.name.encode())
        code_hash.update(path.read_bytes())
    config = {**asdict(metadata), "policy": policy.name, "seed": seed, "budget": budget,
              "replay_mode":"retrospective_source_time_replay",
              "budget_semantics": "exactly B including frame 0", "acquired_indices": list(indices),
              "withheld_indices": [t for t in range(metadata.frame_count) if t not in indices],
              "policy_version": "baseline-v1", "model_version": None, "photon_version": __version__,
              "sequence_sha256": sequence.fingerprint, "python": platform.python_version(),
              "numpy_version": np.__version__, "provenance": getattr(sequence,"provenance",{}),
              "scipy_version": version("scipy"),
              "photon_code_sha256": code_hash.hexdigest(),
              "hardware": {"kernel_backend": "cpu", "gpu": None},
              "fixed_rounding": "floor(k*(T-1)/(B-1)); B=1 -> [0]"}
    if hasattr(policy, "configuration"):
        policy_config = policy.configuration()
        state = policy_config.pop("state_after_run", None)
        config.update(policy_config)
        if state is not None:
            (output / "state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    (output / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    (output / "decisions.jsonl").write_text("".join(json.dumps(d)+"\n" for d in decisions), encoding="utf-8")
    (output / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    timeline = "".join("|" if t in indices else "." for t in range(metadata.frame_count))
    (output / "timeline.txt").write_text(timeline + "\n", encoding="utf-8")
    # Only already-acquired pixels, no withheld reads; sample at most 8 for display.
    shown = history[::max(1, (len(history)+7)//8)]
    sheet = Image.new("RGB", (160 * len(shown), 184), "black")
    draw = ImageDraw.Draw(sheet)
    for i, frame in enumerate(shown):
        image = frame.pixels.max(axis=0) if frame.pixels.ndim == 3 else frame.pixels
        # Display-only per-acquired-frame scaling; never used by policy/metrics.
        lo, hi = float(image.min()), float(image.max())
        preview = ((image.astype(float)-lo) / max(hi-lo, 1) * 255).astype(np.uint8)
        thumb = Image.fromarray(preview).resize((160, 160))
        sheet.paste(thumb, (160*i, 24))
        label = "SYNTHETIC" if frame.source == "synthetic" else "MEASURED"
        draw.text((160*i+2, 4), f"{label} t={frame.index}", fill="white")
    sheet.save(output / "observed.png")
    print(f"{policy.name}: {len(indices)}/{metadata.frame_count} acquired; {list(indices)}\n{timeline}")
    return record
