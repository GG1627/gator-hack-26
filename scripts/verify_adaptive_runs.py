"""Independently inspect completed same-budget Phase 3 traces, not policy inputs."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=Path("runs/mskcc-phase3"))
    parser.add_argument("--output", type=Path, default=Path("runs/mskcc-phase3-verification.json"))
    parser.add_argument("--repeat", type=Path, help="Optional repeat root containing photon_adaptive/")
    parser.add_argument("--require-current-code", action="store_true", help="Reject historical runs from an earlier code version")
    args = parser.parse_args()
    names = ("fixed_interval", "seeded_random", "photon_adaptive", "image_change")
    reports, sources, budgets, versions = {}, set(), set(), set()
    for name in names:
        config = json.loads((args.runs/name/"config.json").read_text())
        rows = [json.loads(line) for line in (args.runs/name/"decisions.jsonl").read_text().splitlines()]
        metrics = json.loads((args.runs/name/"metrics.json").read_text())
        total, budget, indices = config["frame_count"], config["budget"], config["acquired_indices"]
        assert len(rows) == total and [row["t"] for row in rows] == list(range(total))
        assert len(indices) == budget and indices[0] == 0 and len(set(indices)) == budget
        assert [row["t"] for row in rows if row["decision"] == "ACQUIRE"] == indices
        assert config["withheld_indices"] == [t for t in range(total) if t not in indices]
        assert metrics["acquisitions"] == budget and metrics["relative_exposure_proxy"] == budget/total
        assert metrics["event_coverage"] is None and metrics["reconstruction_mse"] is None
        assert (args.runs/name/"timeline.txt").read_text().strip() == "".join("|" if t in indices else "." for t in range(total))
        before, last = budget, None
        for row in rows:
            assert row["remaining_budget_before"] == before
            if name in ("photon_adaptive", "image_change"):
                assert row["last_acquired_index_before"] == last
                assert last is None or row["gap"] == row["t"] - last
                assert np.isfinite(row["score"]) and row["predicted_risk"] == row["score"]
                assert row["reason"]
                c = config["controller_config"]
                score = c["gap_weight"] * row["gap_pressure"]
                if name == "photon_adaptive":
                    score += c["uncertainty_weight"] * row["uncertainty_score"] + c["motion_weight"] * row["motion_score"] + c["event_weight"] * row["event_interest"]
                else:
                    score += c["change_weight"] * row["change_score"]
                assert abs(score - row["score"]) < 1e-12
                assert row["can_acquire"] if row["decision"] == "ACQUIRE" else row["can_skip"]
            if row["decision"] == "ACQUIRE":
                before -= 1
                last = row["t"]
            assert row["remaining_budget_after"] == before >= 0
            assert row["last_acquired_index"] == last
        gaps = np.diff(indices).tolist()
        if name in ("photon_adaptive", "image_change"):
            c = config["controller_config"]
            assert all(c["min_gap"] <= gap <= c["max_gap"] for gap in gaps)
            assert total-1-indices[-1] <= c["max_gap"]
        reports[name] = {"acquisitions": budget, "gap_histogram": dict(sorted(Counter(gaps).items())),
                         "terminal_age": total-1-indices[-1], "reason_counts": dict(Counter(row["reason"] for row in rows)),
                         "acquired_indices": indices}
        sources.add(config["sequence_sha256"])
        budgets.add(budget)
        versions.add(config["photon_code_sha256"])
    assert len(sources) == len(budgets) == len(versions) == 1
    assert len(reports["photon_adaptive"]["gap_histogram"]) > 1, "Phase3 demo must show nonuniform sampling"
    code_hash = hashlib.sha256()
    for path in sorted(Path(__file__).resolve().parents[1].joinpath("services/science/photon").glob("*.py")):
        code_hash.update(path.name.encode())
        code_hash.update(path.read_bytes())
    matches_current = versions == {code_hash.hexdigest()}
    if args.require_current_code:
        assert matches_current, "Run used an earlier science-code version"
    repeated_files = {}
    if args.repeat is not None:
        for filename in ("config.json", "decisions.jsonl", "metrics.json", "timeline.txt", "observed.png", "state.json"):
            original = (args.runs/"photon_adaptive"/filename).read_bytes()
            assert original == (args.repeat/"photon_adaptive"/filename).read_bytes(), filename
            repeated_files[filename] = hashlib.sha256(original).hexdigest()
    result = {"verified": True, "source_sha256": next(iter(sources)), "science_code_sha256": next(iter(versions)),
              "matches_current_science_code": matches_current, "byte_identical_repeat_files_sha256": repeated_files,
              "scope": "trace/budget/score/spacing verification only; no event or reconstruction advantage measured", "policies": reports}
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
