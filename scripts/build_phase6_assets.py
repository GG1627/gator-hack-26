"""Export a static, offline viewer of CLOSED runs. Never run policies or score data.

Writes only the selected output directory. Evaluation JSON is separated from live
replay metadata. Full 3D saved forecasts use the unchanged CPU renderer before MIP.
PNG quantization is for display only; metric values are copied without recomputation.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image
import tifffile

from photon.annotations import audit_mamut
from photon.development import load_scenes
from photon.gaussian import IntensityCalibration, render_gaussians

ROOT = Path(__file__).resolve().parents[1]
METHODS = ("fixed", "photon", "image_change", "random_7", "random_42", "random_2026")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def validate_run(folder):
    closed = read(folder / "closed.json")
    if closed.get("closed") is not True:
        raise ValueError(f"Run is not closed: {folder}")
    for name, expected in closed["files"].items():
        if sha(folder / name) != expected:
            raise ValueError(f"Closed artifact hash differs: {folder / name}")
    config = read(folder / "config.json")
    trace = [json.loads(line) for line in (folder / "decisions.jsonl").read_text().splitlines()]
    if [row["t"] for row in trace] != list(range(config["frame_count"])):
        raise ValueError("Non-contiguous replay trace")
    indices = [row["t"] for row in trace if row["decision"] == "ACQUIRE"]
    if indices != config["acquired_indices"] or len(indices) != config["budget"] or indices[0] != 0:
        raise ValueError("Acquisition count/indices differ")
    return config, trace


def projection(signal):
    # Exact 3D renderer/normalization first; only visualization is projected.
    return np.rint(np.clip(signal.max(axis=0) if signal.ndim == 3 else signal, 0, 1) * 255).astype(np.uint8)


def build(run_root, data_root, output):
    if output.exists():
        raise ValueError(f"Output exists; choose a new directory or move the old export: {output}")
    protocol = read(run_root / "protocol.json")
    checkpoint = read(run_root / "checkpoint.json")
    frozen = {ROOT / name: value for name, value in protocol["implementation_hashes"].items()}
    for path, expected in frozen.items():
        if sha(path) != expected:
            raise ValueError(f"Frozen scientific source changed: {path}")
    # Validate every closed trace and approved metric hash BEFORE exporting any pixels.
    runs = {}
    for sid in protocol["evaluation_sequences"]:
        for budget in protocol["budgets"]:
            key = f"{sid}/b{budget}"
            runs[key] = {name: validate_run(run_root / key / name) for name in METHODS}
            first = runs[key]["fixed"][0]
            for config, _ in runs[key].values():
                if any(config[k] != first[k] for k in ("sequence_sha256", "budget", "frame_count", "normalization")):
                    raise ValueError("Comparison requires matching source/calibration/budget")
    approved = {item["condition"]: item for item in checkpoint["completed_image_conditions"]}
    for item in approved.values():
        for name, expected in item["artifact_sha256"].items():
            if sha(run_root / name) != expected:
                raise ValueError(f"Checkpoint metric artifact changed: {name}")
    event_audit = read(run_root / "event-audit.json")
    if event_audit["protocol_sha256"] != sha(run_root / "protocol.json"):
        raise ValueError("Event protocol mismatch")
    output.mkdir(parents=True)
    sources = {}

    def copy_source(path):
        relative = path.relative_to(ROOT).as_posix()
        destination = output / "sources" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        sources[relative] = sha(path)
        return f"sources/{relative}"

    for name in ("protocol.json", "checkpoint.json", "event-audit.json"):
        copy_source(run_root / name)
    manifest = {"version": 1, "status": "partial", "phase5_complete": False,
                "protocol_sha256": sha(run_root / "protocol.json"), "conditions": [],
                "display": "512px MIP of full 3D normalized signal, rounded to 8-bit; display only",
                "license": "CC BY 4.0", "doi": "10.5281/zenodo.6460303"}
    for sid in protocol["evaluation_sequences"]:
        config = runs[f"{sid}/b{protocol['budgets'][0]}"]["fixed"][0]
        calibration = IntensityCalibration(**config["normalization"])
        image_root = output / "images" / sid
        image_root.mkdir(parents=True)
        input_hashes = {}
        print(f"{sid}: projecting authentic source volumes", flush=True)
        for t in range(config["frame_count"]):
            path = data_root / sid / "images" / f"{sid}_t{t:03d}.tif"
            raw = tifffile.imread(path)
            if list(raw.shape) != config["shape"] or str(raw.dtype) != config["dtype"]:
                raise ValueError(f"Source dimensions/dtype differ: {path}")
            input_hashes[path.name] = sha(path)
            Image.fromarray(projection(calibration.normalize(raw))).save(image_root / f"{t}.png")
        write(output / "sources" / f"{sid}-volume-hashes.json", input_hashes)
        # Annotation import is strictly post-closure and is only exported in eval JSON.
        annotation_paths = list((data_root / sid / "tracks").glob("*.xml"))
        if len(annotation_paths) != 1:
            raise ValueError("Expected one canonical MaMuT graph")
        annotations = audit_mamut(annotation_paths[0], config["frame_count"])
        for budget in protocol["budgets"]:
            key = f"{sid}/b{budget}"
            condition_root = output / key
            condition_root.mkdir(parents=True)
            result = {"key": key, "sequence_id": sid, "budget": budget,
                      "frame_count": config["frame_count"], "frame_interval_minutes": config["frame_interval_minutes"],
                      "sequence_sha256": config["sequence_sha256"], "methods": {}, "shape": config["shape"],
                      "voxel_size_xyz_um": config["voxel_size_xyz_um"], "normalization": config["normalization"]}
            summary = read(run_root / key / "summary.json") if key in approved else None
            evaluation = {"status": "first-pass / source rerender pending" if summary else "pending / not computed",
                          "reason": None if summary else "Phase 5 image evaluation is paused; this condition has no completed image scores.",
                          "accounting": approved[key]["independent_accounting"] if summary else "not_run",
                          "division_times": annotations["division_times"], "methods": {}}
            for name, (cfg, trace) in runs[key].items():
                cfg_source = copy_source(run_root / key / name / "config.json")
                trace_source = copy_source(run_root / key / name / "decisions.jsonl")
                result["methods"][name] = {"config": cfg, "decisions": trace, "config_source": cfg_source, "trace_source": trace_source}
                event = event_audit["groups"][key][name]
                if event["events"] != annotations["binary_divisions"]:
                    raise ValueError("Event audit / canonical annotation mismatch")
                metrics = summary["variants"][name] if summary else None
                evaluation["methods"][name] = {"event": event, "metrics": metrics,
                    "metrics_source": copy_source(run_root / key / name / "metrics.json") if summary else None}
            # Only PHOTON needs a predictive display. Other methods hold their own last image.
            forecasts = load_scenes(run_root / key / "photon" / "forecasts.npz")
            expected = set(range(config["frame_count"])) - set(result["methods"]["photon"]["config"]["acquired_indices"])
            if set(forecasts) != expected:
                raise ValueError("Forecast archive does not match withheld times")
            prediction_root = condition_root / "predictions"
            prediction_root.mkdir()
            print(f"{key}: rendering {len(forecasts)} saved causal 3D forecasts (display export only)", flush=True)
            for t, scene in forecasts.items():
                rendered = render_gaussians(tuple(config["shape"]), scene)
                Image.fromarray(projection(rendered)).save(prediction_root / f"{t}.png")
            result["gaussian_counts"] = {str(t): len(scene) for t, scene in forecasts.items()}
            write(condition_root / "replay.json", result)
            write(condition_root / "evaluation.json", evaluation)
            manifest["conditions"].append({"key": key, "sequence_id": sid, "budget": budget,
                "replay": f"{key}/replay.json", "evaluation": f"{key}/evaluation.json"})
    benchmark_path = ROOT / "runs/phase4-benchmark-verified/benchmark.json"
    if benchmark_path.exists():
        benchmark = read(benchmark_path)
        manifest["gpu"] = {"source": copy_source(benchmark_path), "case": benchmark["cases"][-1],
                           "device": benchmark["nvidia_smi"], "note": "Historical Phase 4 single-render bridge; CPU remains default. Later persistent-worker audit is documented separately."}
    manifest["source_hashes"] = sources
    for path, expected in frozen.items():
        if sha(path) != expected:
            raise ValueError(f"Frozen scientific source changed during export: {path}")
    # Publish manifest LAST: an interrupted export never appears complete to the UI.
    write(output / "manifest.json", manifest)
    print(f"Exported {len(runs) * len(METHODS)} authentic closed runs to {output}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=ROOT / "runs/phase5")
    parser.add_argument("--data", type=Path, default=ROOT / "data/mskcc-audit/mskcc-confocal")
    parser.add_argument("--output", type=Path, default=ROOT / "apps/web/public/demo")
    args = parser.parse_args()
    build(args.runs.resolve(), args.data.resolve(), args.output.resolve())
