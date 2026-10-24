"""Offline checks of a completed Phase 2 preview; never used by a controller."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import tifffile

from photon.gaussian import IntensityCalibration


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=Path("runs/mskcc-phase2"))
    parser.add_argument("--sequence", type=Path, default=Path("data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1"))
    parser.add_argument("--output", type=Path, default=Path("runs/mskcc-phase2-verification.json"))
    parser.add_argument("--require-current-code", action="store_true", help="Reject historical runs from an earlier code version")
    args = parser.parse_args()
    config = json.loads((args.run / "config.json").read_text())
    metrics = json.loads((args.run / "metrics.json").read_text())
    state = json.loads((args.run / "state.json").read_text())
    decisions = [json.loads(line) for line in (args.run / "decisions.jsonl").read_text().splitlines()]
    indices = config["acquired_indices"]
    assert len(decisions) == config["frame_count"]
    assert [d["t"] for d in decisions] == list(range(config["frame_count"]))
    assert [d["t"] for d in decisions if d["decision"] == "ACQUIRE"] == indices
    assert len(indices) == config["budget"] and indices[0] == 0 and max(indices) < config["target"]
    assert state["acquired_indices"] == indices
    for observation in state["observations"]:
        assert observation["t"] in indices
    with np.load(args.run / "prediction.npz", allow_pickle=False) as saved:
        predicted = saved["pixels"]
        disagreement = saved["uncertainty_map"]
        assert str(saved["kind"]) == "PREDICTED"
        assert saved["based_on_indices"].tolist() == indices
        assert np.isfinite(saved["uncertainty_um"]) and saved["uncertainty_um"] >= 0
    with np.load(args.run / "evaluation_truth.npz", allow_pickle=False) as saved:
        truth = saved["pixels"]
        assert str(saved["kind"]) == "GROUND TRUTH (EVAL ONLY)"
    for array in (predicted, truth, disagreement):
        assert array.shape == tuple(config["shape"]) and array.dtype == np.float32
        assert np.isfinite(array).all() and array.min() >= 0 and array.max() <= 1

    def source(t):
        return tifffile.imread(args.sequence / "images" / f"{config['sequence_id']}_t{t:03d}.tif")

    calibration = IntensityCalibration.from_image(source(indices[0]))
    assert calibration.to_dict() == state["normalization"] == metrics["normalization"]
    np.testing.assert_array_equal(truth, calibration.normalize(source(config["target"])))
    baseline = calibration.normalize(source(indices[-1]))
    error = predicted.astype(np.float64) - truth
    held_error = baseline.astype(np.float64) - truth
    roi = np.maximum(np.maximum(predicted, truth), baseline) > metrics["foreground_threshold"]
    recomputed = {
        "reconstruction_mse": float(np.mean(error ** 2)),
        "reconstruction_mae": float(np.mean(np.abs(error))),
        "hold_last_mse": float(np.mean(held_error ** 2)),
        "foreground_roi_voxels": int(roi.sum()),
        "foreground_roi_mse": float(np.mean(error[roi] ** 2)) if roi.any() else None,
        "hold_last_foreground_roi_mse": float(np.mean(held_error[roi] ** 2)) if roi.any() else None,
    }
    for key, value in recomputed.items():
        assert metrics[key] == value, key
    code_hash = hashlib.sha256()
    for path in sorted(Path(__file__).resolve().parents[1].joinpath("services/science/photon").glob("*.py")):
        code_hash.update(path.name.encode())
        code_hash.update(path.read_bytes())
    matches_current = config["photon_code_sha256"] == code_hash.hexdigest()
    if args.require_current_code:
        assert matches_current, "Run used an earlier science-code version"
    report = {"verified": True, "run": str(args.run), "checks": [
        "270-step trace and exact acquisition count", "prediction uses only pre-target acquisitions",
        "finite normalized 3D prediction/disagreement and distinct evaluation tag",
        "saved truth equals source target under first-acquisition calibration",
        "whole-volume and common-ROI metrics independently recomputed"],
        "metrics": recomputed, "source_sha256_recorded": config["sequence_sha256"],
        "science_code_sha256": config["photon_code_sha256"], "matches_current_science_code": matches_current,
        "limitations": "Offline artifact checks complement causal read-spy tests; do not prove isolation of hostile code."}
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
