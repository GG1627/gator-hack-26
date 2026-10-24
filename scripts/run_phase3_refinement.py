"""Bounded s1-only development ablation. All policies close before scoring."""
import argparse
import hashlib
import json
from pathlib import Path

from photon.adaptive import AdaptivePolicy, controller_variant
from photon.data import load_sequence
from photon.development import (evaluate_development, load_closed_run, record_development_run,
                                science_hash, select_variant)
from photon.policy import ScheduledPolicy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sequence", type=Path, default=Path("data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1"))
    parser.add_argument("--output", type=Path, default=Path("runs/mskcc-phase3-refinement"))
    parser.add_argument("--recompute", action="store_true", help="Recompute all metrics from saved causal geometry and source")
    parser.add_argument("--require-current-code", action="store_true", help="Require recorded code hash when recomputing historical geometry")
    args = parser.parse_args()
    sequence = load_sequence(args.sequence, dataset_id="MSKCC-CONFOCAL")
    if sequence.metadata.sequence_id != "mskcc_confocal_s1" or sequence.metadata.split != "development":
        parser.error("This development experiment is restricted to s1")
    names = ("fixed", "original", "paced", "robust", "paced_robust")
    protocol_path = Path(__file__).resolve().parents[1]/"docs/phase3-refinement-plan.md"
    if args.recompute:
        protocol = json.loads((args.output/"protocol.json").read_text())
        if args.require_current_code and protocol["science_code_sha256"] != science_hash():
            parser.error("Recompute requires the recorded science-code version")
        runs = [load_closed_run(sequence, args.output/name) for name in names]
    else:
        if args.output.exists():
            parser.error("Output exists; choose a new directory")
        protocol = {"scope": "exploratory development, no s2/s3", "budget": 54, "seed": 42,
                    "event_tolerance_frames": 1, "foreground_threshold": 0.1,
                    "variants": {name: (None if name == "fixed" else controller_variant(name).__dict__) for name in names},
                    "source_sha256": sequence.fingerprint, "science_code_sha256": science_hash(),
                    "protocol_sha256": hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
                    "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    "selection_rule": "more events than original and common raw-hold MSE <= original; max coverage, min raw-hold MSE, then name"}
        args.output.mkdir(parents=True)
        (args.output/"protocol.json").write_text(json.dumps(protocol, indent=2), encoding="utf-8")
        runs = []
        for name in names:
            policy = ScheduledPolicy("fixed_interval") if name == "fixed" else AdaptivePolicy(config=controller_variant(name))
            runs.append(record_development_run(sequence, policy, 54, 42, name, args.output/name))
        # The legacy implementation must preserve the original scientific trace.
        historical = Path("runs/mskcc-phase3/photon_adaptive/config.json")
        if historical.exists():
            assert list(runs[1].record.acquired_indices) == json.loads(historical.read_text())["acquired_indices"]
        print("All five acquisition runs closed. Only now revealing truth and lineage labels.", flush=True)
    summary, rows = evaluate_development(runs, annotation_path=args.sequence/"tracks/tracks_mamut.xml",
                                         event_tolerance=protocol["event_tolerance_frames"],
                                         foreground_threshold=protocol["foreground_threshold"])
    summary["selected_variant"] = select_variant(summary)
    if args.recompute:
        original = json.loads((args.output/"summary.json").read_text())
        if summary != original:
            raise ValueError("Full source/scene recomputation differs from saved metrics")
        for name in names:
            stored = [json.loads(line) for line in (args.output/name/"evaluation.jsonl").read_text().splitlines()]
            if stored != rows[name]:
                raise ValueError(f"Per-frame recomputation differs: {name}")
        (args.output/"recomputation.json").write_text(json.dumps({"verified": True, "all_summary_and_per_frame_values_exact": True,
                                                                  "recorded_science_code_sha256": protocol["science_code_sha256"],
                                                                  "current_science_code_sha256": science_hash(),
                                                                  "matches_recorded_code": protocol["science_code_sha256"] == science_hash()}, indent=2), encoding="utf-8")
    else:
        (args.output/"summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        for name in names:
            (args.output/name/"metrics.json").write_text(json.dumps(summary["variants"][name], indent=2), encoding="utf-8")
            (args.output/name/"evaluation.jsonl").write_text("".join(json.dumps(row)+"\n" for row in rows[name]), encoding="utf-8")
    print(f"Selected development variant: {summary['selected_variant']}; common withheld targets: {len(summary['common_withheld_indices'])}")
    for name, result in summary["variants"].items():
        print(json.dumps({"variant": name, "first_half_captures": result["captures_in_first_half"],
                          "event_coverage": result["event"]["event_coverage"],
                          "common_mse": {estimator: value["mse"] for estimator, value in result["common_withheld"].items()}}))


if __name__ == "__main__":
    main()
