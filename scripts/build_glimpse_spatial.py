"""Display-only 3D exports from existing CLOSED Phase 5 runs; no fitting/scoring.

Gaussian records preserve the saved model in physical XYZ micrometers. Point
samples preserve original acquired voxel coordinates, using a fixed signal
threshold and deterministic spatial subsampling. Original artifacts are read-only.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import tifffile

from build_phase6_assets import ROOT, read, sha, validate_run, write
from photon.development import load_scenes


def physical_gaussian(component, spacing_xyz):
    spacing = np.asarray(spacing_xyz, dtype=np.float64)
    center = np.asarray(component.center)[::-1] * spacing
    covariance = np.asarray(component.covariance)[::-1, ::-1] * np.outer(spacing, spacing)
    values, basis = np.linalg.eigh(covariance)
    if basis.shape != (3, 3) or np.min(values) <= 0:
        raise ValueError("Expected positive definite 3D covariance")
    if np.linalg.det(basis) < 0:
        basis[:, 0] *= -1
    return {"center": center.tolist(), "covariance": covariance.reshape(-1).tolist(),
            "radii": np.sqrt(values).tolist(), "basis": basis.reshape(-1).tolist(),
            "amplitude": float(component.amplitude)}


def sample_voxels(raw, normalization, *, step=(1, 3, 3), threshold=0.2, cap=12000):
    if raw.ndim != 3 or max(raw.shape) > 65535 or cap < 1:
        raise ValueError("Unsupported source shape or point cap")
    signal = np.clip((raw[::step[0], ::step[1], ::step[2]].astype(np.float32)
                      - normalization["background"]) / normalization["scale"], 0, 1)
    indices = np.argwhere(signal >= threshold)
    eligible = len(indices)
    if len(indices) > cap:
        indices = indices[np.linspace(0, len(indices) - 1, cap, dtype=np.int64)]
    points = np.empty((len(indices), 4), dtype="<u2")
    points[:, :3] = (indices * np.asarray(step))[:, ::-1]
    points[:, 3] = np.rint(signal[tuple(indices.T)] * 65535).astype(np.uint16)
    return points, eligible


def build(run_root, data_root, demo_root):
    output = demo_root / "spatial"
    if output.exists():
        raise ValueError(f"Output exists; use a new demo directory: {output}")
    manifest = read(demo_root / "manifest.json")
    protocol = read(run_root / "protocol.json")
    if manifest["protocol_sha256"] != sha(run_root / "protocol.json"):
        raise ValueError("Display and scientific protocol hashes differ")
    for name, expected in protocol["implementation_hashes"].items():
        if sha(ROOT / name) != expected:
            raise ValueError(f"Frozen source changed: {name}")
    validated = {}
    for condition in manifest["conditions"]:
        key = condition["key"]
        config, trace = validate_run(run_root / key / "photon")
        exported = read(demo_root / condition["replay"])
        if exported["methods"]["photon"]["config"] != config:
            raise ValueError("Replay export does not match original closed run")
        validated[key] = config
    output.mkdir(parents=True)
    ledger = {"version": 1, "scope": "display only; no policy, fitting or scoring executed",
              "protocol_sha256": manifest["protocol_sha256"],
              "point_format": "little-endian uint16 [x_voxel,y_voxel,z_voxel,signal_0_to_65535]",
              "sample_step_zyx": [1, 3, 3], "signal_threshold": 0.2, "max_points": 12000,
              "sampling": "lexicographic ZYX fixed grid; evenly spaced eligible indices when capped",
              "conditions": {}, "sequences": {}, "files": {}}
    for key, config in validated.items():
        folder = run_root / key / "photon"
        fits = load_scenes(folder / "held_scenes.npz")
        forecasts = load_scenes(folder / "forecasts.npz")
        acquired = set(config["acquired_indices"])
        if set(fits) != acquired or set(forecasts) != set(range(config["frame_count"])) - acquired:
            raise ValueError("Saved scenes disagree with acquisition trace")
        scenes = []
        for t in range(config["frame_count"]):
            measured = t in fits
            source_t = max(i for i in acquired if i <= t)
            scene = fits[t] if measured else forecasts[t]
            scenes.append({"t": t, "source_t": source_t, "kind": "fit" if measured else "forecast",
                           "gaussians": [physical_gaussian(g, config["voxel_size_xyz_um"]) for g in scene]})
        relative = f"{key}/gaussians.json"
        write(output / relative, {"version": 1, "units": "XYZ micrometers", "sequence_id": config["sequence_id"],
                                  "shape_zyx": config["shape"], "spacing_xyz_um": config["voxel_size_xyz_um"],
                                  "source_sha256": {name: sha(folder / name) for name in ("config.json", "held_scenes.npz", "forecasts.npz", "decisions.jsonl")},
                                  "frames": scenes})
        ledger["conditions"][key] = relative
        ledger["files"][relative] = sha(output / relative)
        print(f"Exported saved Gaussian geometry: {key}", flush=True)
    for sid in sorted({config["sequence_id"] for config in validated.values()}):
        config = next(config for config in validated.values() if config["sequence_id"] == sid)
        for other in validated.values():
            if other["sequence_id"] == sid and any(other[field] != config[field] for field in ("normalization", "shape", "sequence_sha256", "voxel_size_xyz_um")):
                raise ValueError("Conditions disagree on source calibration or geometry")
        source_hashes = read(demo_root / "sources" / f"{sid}-volume-hashes.json")
        folder = output / sid / "points"
        folder.mkdir(parents=True)
        counts = []
        for t in range(config["frame_count"]):
            source = data_root / sid / "images" / f"{sid}_t{t:03d}.tif"
            if sha(source) != source_hashes[source.name]:
                raise ValueError(f"Source volume hash differs: {source}")
            raw = tifffile.imread(source)
            if list(raw.shape) != config["shape"] or str(raw.dtype) != config["dtype"]:
                raise ValueError("Source shape/dtype differs")
            points, eligible = sample_voxels(raw, config["normalization"])
            destination = folder / f"{t}.bin"
            destination.write_bytes(points.tobytes())
            relative = destination.relative_to(output).as_posix()
            ledger["files"][relative] = sha(destination)
            counts.append({"t": t, "points": len(points), "eligible": eligible})
            if t % 50 == 0:
                print(f"{sid}: sampled source volume {t}/{config['frame_count']-1}", flush=True)
        ledger["sequences"][sid] = {"spacing_xyz_um": config["voxel_size_xyz_um"], "counts": counts}
    for name, expected in protocol["implementation_hashes"].items():
        if sha(ROOT / name) != expected:
            raise ValueError(f"Frozen source changed during display export: {name}")
    write(output / "manifest.json", ledger)
    print(f"Spatial display export complete: {len(ledger['files'])} files", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=ROOT / "runs/phase5")
    parser.add_argument("--data", type=Path, default=ROOT / "data/mskcc-audit/mskcc-confocal")
    parser.add_argument("--demo", type=Path, default=ROOT / "apps/web/public/demo")
    args = parser.parse_args()
    build(args.runs.resolve(), args.data.resolve(), args.demo.resolve())
