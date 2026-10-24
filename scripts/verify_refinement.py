"""Independent trace/metric accounting for the bounded development comparison."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def source_probes(root, sequence_path, protocol):
    from photon.data import load_sequence
    from photon.development import load_scenes
    from photon.gaussian import IntensityCalibration, render_gaussians
    sequence = load_sequence(sequence_path, dataset_id="MSKCC-CONFOCAL")
    assert sequence.fingerprint == protocol["source_sha256"]
    names = tuple(protocol["variants"])
    configs = {name: json.loads((root/name/"config.json").read_text()) for name in names}
    targets = sorted(set.intersection(*(set(range(sequence.metadata.frame_count))-set(config["acquired_indices"])
                                        for config in configs.values())))
    probes = sorted({targets[0], targets[len(targets)//2], targets[-1]})
    calibration = IntensityCalibration.from_image(sequence.read(0))
    result = {"source_sha256": sequence.fingerprint, "indices": probes, "variants": {}, "scene_archive_sha256": {}}
    for name in names:
        folder = root/name
        assert calibration.to_dict() == configs[name]["normalization"]
        forecasts, held = load_scenes(folder/"forecasts.npz"), load_scenes(folder/"held_scenes.npz")
        result["scene_archive_sha256"][name] = {filename: hashlib.sha256((folder/filename).read_bytes()).hexdigest()
                                                 for filename in ("forecasts.npz", "held_scenes.npz")}
        result["variants"][name] = {}
        for t in probes:
            truth = calibration.normalize(sequence.read(t))
            last = max(index for index in held if index < t)
            estimates = {"gaussian_forecast": render_gaussians(sequence.metadata.shape, forecasts[t]),
                         "gaussian_hold": render_gaussians(sequence.metadata.shape, held[last]),
                         "raw_hold": calibration.normalize(sequence.read(last))}
            errors = {}
            roi = truth > protocol["foreground_threshold"]
            for estimator, pixels in estimates.items():
                error = pixels.astype(np.float64)-truth
                errors[estimator] = {"squared_error_sum": float(np.sum(error**2)), "absolute_error_sum": float(np.sum(abs(error))),
                                     "voxel_count": truth.size, "foreground_squared_error_sum": float(np.sum(error[roi]**2)),
                                     "foreground_absolute_error_sum": float(np.sum(abs(error[roi]))), "foreground_voxel_count": int(roi.sum())}
            result["variants"][name][str(t)] = errors
            print(f"Source/scene probe prepared: {name} t={t}", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=Path("runs/mskcc-phase3-refinement"))
    parser.add_argument("--sequence", type=Path, help="Also independently rerender first/middle/last common targets from source")
    parser.add_argument("--prepare-probes", action="store_true", help="Prepare source probes after runs close, before summary is ready")
    parser.add_argument("--source-probes", type=Path, help="Compare previously prepared source probes without rerendering")
    args = parser.parse_args()
    protocol = json.loads((args.run/"protocol.json").read_text())
    if args.prepare_probes:
        if args.sequence is None:
            parser.error("Preparing probes requires --sequence")
        # These files are exported only after successful oracle closure.
        for name in protocol["variants"]:
            assert (args.run/name/"forecasts.npz").exists() and (args.run/name/"state.json").exists()
        prepared = source_probes(args.run, args.sequence, protocol)
        (args.run/"source-probes.json").write_text(json.dumps(prepared, indent=2), encoding="utf-8")
        return
    summary = json.loads((args.run/"summary.json").read_text())
    common = set(summary["common_withheld_indices"])
    hashes = {}
    withheld = []
    for name, result in summary["variants"].items():
        folder = args.run/name
        config = json.loads((folder/"config.json").read_text())
        decisions = [json.loads(line) for line in (folder/"decisions.jsonl").read_text().splitlines()]
        rows = [json.loads(line) for line in (folder/"evaluation.jsonl").read_text().splitlines()]
        total, budget = config["frame_count"], config["budget"]
        indices = [row["t"] for row in decisions if row["decision"] == "ACQUIRE"]
        assert len(indices) == budget == protocol["budget"] == result["acquisitions"]
        assert indices == config["acquired_indices"] == result["acquired_indices"] and indices[0] == 0
        assert config["sequence_sha256"] == protocol["source_sha256"]
        assert config["photon_code_sha256"] == protocol["science_code_sha256"]
        assert config["normalization"] == summary["normalization"]
        assert result["captures_in_first_half"] == sum(t < total//2 for t in indices)
        targets = set(range(total))-set(indices)
        withheld.append(targets)
        assert [row["t"] for row in rows] == sorted(targets)
        count = 0
        for row in decisions:
            assert row["remaining_budget_before"] == budget-count
            count += row["decision"] == "ACQUIRE"
            assert row["remaining_budget_after"] == budget-count >= 0
            if name != "fixed":
                assert row["last_acquired_index_before"] is None or row["last_acquired_index_before"] < row["t"]
                if row["decision"] == "ACQUIRE" and not row["pacing_permits_acquire"]:
                    assert row["pacing_override_for_feasibility"] and not row["can_skip"]
                if row["decision"] == "ACQUIRE" and not row["pacing_override_for_feasibility"]:
                    assert count <= row["pacing_allowance"]
        if name != "fixed":
            c = config["controller_config"]
            assert all(c["min_gap"] <= gap <= c["max_gap"] for gap in np.diff(indices))
            assert total-1-indices[-1] <= c["max_gap"]
        for scope, selected in (("own_withheld", rows), ("common_withheld", [row for row in rows if row["t"] in common])):
            for estimator, expected in result[scope].items():
                assert expected["frames"] == len(selected)
                columns = {key: sum(row["errors"][estimator][key] for row in selected)
                           for key in selected[0]["errors"][estimator]}
                for key, value in columns.items():
                    assert expected[key] == value
                for prefix in ("", "foreground_"):
                    n = columns[prefix+"voxel_count"]
                    for metric, source in (("mse", "squared_error_sum"), ("mae", "absolute_error_sum")):
                        actual = columns[prefix+source]/n if n else None
                        assert expected[prefix+metric] == actual
        event = result["event"]
        if event["event_coverage"] is not None:
            assert event["event_coverage"] == event["covered_events"]/event["events"]
        hashes[name] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(folder.iterdir()) if path.is_file()}
    assert common == set.intersection(*withheld)
    if (args.run/"event-check.json").exists():
        independent_events = json.loads((args.run/"event-check.json").read_text())
        for name, result in summary["variants"].items():
            for key, value in independent_events[name].items():
                assert result["event"][key] == value
    original = summary["variants"]["original"]
    candidates = []
    for name in ("paced", "robust", "paced_robust"):
        value = summary["variants"][name]
        coverage, mse = value["event"]["event_coverage"], value["common_withheld"]["raw_hold"]["mse"]
        if (coverage is not None and original["event"]["event_coverage"] is not None
                and coverage > original["event"]["event_coverage"] and mse <= original["common_withheld"]["raw_hold"]["mse"]):
            candidates.append((-coverage, mse, name))
    assert summary["selected_variant"] == (sorted(candidates)[0][2] if candidates else "original")
    probes = []
    if args.sequence is not None or args.source_probes is not None:
        prepared = (json.loads(args.source_probes.read_text()) if args.source_probes is not None
                    else source_probes(args.run, args.sequence, protocol))
        assert prepared["source_sha256"] == protocol["source_sha256"]
        targets = sorted(common)
        probes = prepared["indices"]
        assert probes == sorted({targets[0], targets[len(targets)//2], targets[-1]})
        for name in summary["variants"]:
            folder = args.run/name
            for filename, digest in prepared["scene_archive_sha256"][name].items():
                assert hashlib.sha256((folder/filename).read_bytes()).hexdigest() == digest
            rows = {row["t"]: row for row in (json.loads(line) for line in (folder/"evaluation.jsonl").read_text().splitlines())}
            for t in probes:
                assert prepared["variants"][name][str(t)] == rows[t]["errors"], (name, t)
                print(f"Source/scene error check: {name} t={t} exact", flush=True)
    report = {"verified": True, "common_target_count": len(common),
              "checks": ["same source/code/calibration and exact budgets", "causal trace chronology",
                         "gap/terminal constraints and pacing/overrides", "exact common target intersection",
                         "independent per-frame error aggregation", "event ratio arithmetic", "predeclared adoption rule"],
              "independent_event_check_compared": (args.run/"event-check.json").exists(),
              "source_scene_probe_indices": probes,
              "scope": "all-frame metric accounting plus exact source/scene probes; full rerender available with run_phase3_refinement.py --recompute",
              "artifact_sha256": hashes}
    (args.run/"verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "artifact_sha256"}, indent=2))


if __name__ == "__main__":
    main()
