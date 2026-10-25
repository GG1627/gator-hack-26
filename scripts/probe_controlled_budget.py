"""Predeclared 32-versus-40 image probe. No algorithm or demo asset changes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.controlled.benchmark import ControlledSequence, FixedPolicy, make_clip, run_closed, score
from experiments.controlled.event_focus import EventFocusPolicy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    deadline = start + 120
    sources = [Path(__file__), ROOT / "docs/CONTROLLED_BUDGET_PROBE.md",
               *sorted((ROOT / "experiments/controlled").glob("*.py"))]
    protocol = {
        "scope": "synthetic only; separate unequal-budget comparison",
        "development_seeds": [7, 42], "prospective_seeds": list(range(301, 307)),
        "conditions": ["precursor", "abrupt", "quiet"], "frames": 240,
        "adaptive_budget": 32, "fixed_budgets": [32, 40], "fixed_phase": 0,
        "tolerance_frames": 1, "hard_limit_seconds": 120,
        "source_sha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
    }
    (args.output / "protocol.json").write_text(json.dumps(protocol, indent=2), encoding="utf-8")
    rows = []
    status = "complete"
    try:
        for seed in [*protocol["development_seeds"], *protocol["prospective_seeds"]]:
            for condition in protocol["conditions"]:
                clip, events, _ = make_clip(seed, condition)
                sequence = ControlledSequence(clip)
                closed = [("adaptive32", run_closed(sequence, EventFocusPolicy(), 32, seed, deadline)),
                          ("fixed32", run_closed(sequence, FixedPolicy(0), 32, seed, deadline)),
                          ("fixed40", run_closed(sequence, FixedPolicy(0), 40, seed, deadline))]
                for name, record in closed:
                    indices = record["acquired_indices"]
                    assert len(indices) == record["budget"] and indices[0] == 0
                    if name == "adaptive32":
                        assert all(2 <= b-a <= 12 for a, b in zip(indices, indices[1:]))
                        assert 239-indices[-1] <= 12
                    rows.append({"seed": seed, "condition": condition, "name": name,
                                 "split": "development" if seed in protocol["development_seeds"] else "prospective",
                                 "sequence_sha256": sequence.fingerprint, "events": events,
                                 "run": record, "metrics": score(record, clip, events)})
                print(f"{seed}/{condition}: " + ", ".join(f"{r['name']} {r['metrics']['covered_events']}/{len(events)}" for r in rows[-3:]), flush=True)
    except TimeoutError:
        status = "time_limit_partial"
    result = {"status": status, "elapsed_seconds": time.monotonic()-start, "protocol": protocol, "rows": rows}
    (args.output / "summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"{status}: {len(rows)} comparisons in {result['elapsed_seconds']:.1f}s", flush=True)
    return 0 if status == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
