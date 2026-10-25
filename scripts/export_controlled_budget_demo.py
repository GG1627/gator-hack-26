"""Export the saved 32/40 comparison; never rerun or tune a controller."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.controlled.benchmark import make_clip, score
from photon.gaussian import GaussianFitConfig, IntensityCalibration, detect_and_fit, render_gaussians
from photon.gpu import CudaRustRunner
from scripts.export_controlled_demo import atlas

EVIDENCE = ROOT / "docs/evidence/controlled-budget32-v1"
METHODS = {"adaptive32": ("event_focus", 32), "fixed32": ("fixed_32", 32), "fixed40": ("fixed_0", 40)}


def load_verified_summary(source, verification):
    raw = gzip.decompress(source.read_bytes())
    checked = json.loads(verification.read_text(encoding="utf-8"))
    if checked.get("verified") is not True or hashlib.sha256(raw).hexdigest() != checked["summary_sha256"]:
        raise ValueError("Saved evidence hash/verification mismatch")
    summary = json.loads(raw)
    if summary["status"] != "complete" or len(summary["rows"]) != 72:
        raise ValueError("Incomplete lower-budget comparison")
    protocol = summary["protocol"]
    if protocol["prospective_seeds"] != list(range(301, 307)) or protocol["adaptive_budget"] != 32 or protocol["fixed_budgets"] != [32, 40]:
        raise ValueError("Unexpected registered comparison")
    for name, expected in protocol["source_sha256"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Registered source changed: {name}")
    return summary


def validate_rows(rows, clip, events):
    if len(rows) != 3 or {row["name"] for row in rows} != set(METHODS):
        raise ValueError("Missing/duplicate budget comparison")
    image_hash = hashlib.sha256(clip.tobytes()).hexdigest()
    for row in rows:
        method, budget = METHODS[row["name"]]
        record = row["run"]
        indices = record["acquired_indices"]
        if row["sequence_sha256"] != image_hash or row["events"] != events:
            raise ValueError("Source pixels/events changed")
        if record["budget"] != budget or len(indices) != budget or indices != sorted(set(indices)) or indices[0] != 0 or indices[-1] >= 240:
            raise ValueError("Invalid capture budget/schedule")
        if [d["t"] for d in record["decisions"]] != list(range(240)) or any(d["decision"] not in ("ACQUIRE", "SKIP") for d in record["decisions"]):
            raise ValueError("Invalid decision clock")
        if [d["t"] for d in record["decisions"] if d["decision"] == "ACQUIRE"] != indices:
            raise ValueError("Trace and captures differ")
        if method == "event_focus" and (any(not 2 <= b-a <= 12 for a, b in zip(indices, indices[1:])) or 239-indices[-1] > 12):
            raise ValueError("Adaptive gap constraint violated")
        if score(record, clip, events) != row["metrics"]:
            raise ValueError("Saved metric differs from source recomputation")


def export(output, cuda=False):
    start = time.monotonic()
    summary = load_verified_summary(EVIDENCE / "summary.json.gz", EVIDENCE / "verification.json")
    output.mkdir(parents=True, exist_ok=False)
    experiments, evidence, batches = [], [], []
    runner = CudaRustRunner(timeout=25, persistent=True) if cuda else None
    checked_rows = 0
    try:
        for seed in [*summary["protocol"]["development_seeds"], *summary["protocol"]["prospective_seeds"]]:
            for condition in summary["protocol"]["conditions"]:
                if time.monotonic()-start > 120:
                    raise TimeoutError("Two-minute export limit reached")
                clip, events, _ = make_clip(seed, condition)
                rows = [r for r in summary["rows"] if r["seed"] == seed and r["condition"] == condition]
                validate_rows(rows, clip, events)
                checked_rows += len(rows)
                if seed in summary["protocol"]["development_seeds"]:
                    continue
                key = f"{seed}-{condition}"
                acquired = sorted({i for row in rows for i in row["run"]["acquired_indices"]})
                observed = np.zeros_like(clip)
                observed[acquired] = clip[acquired]
                atlas(output / f"{key}-observed.png", observed)
                atlas(output / f"{key}-reference.png", clip)
                model_url = None
                if runner:
                    calibration = IntensityCalibration.from_image(clip[0])
                    scenes = [detect_and_fit(calibration.normalize(clip[t], clip=False), (1., 1.), calibration.noise_sigma, GaussianFitConfig(min_voxels=8))[0] for t in acquired]
                    modeled = np.zeros_like(clip)
                    for offset in range(0, len(scenes), 64):
                        if time.monotonic()-start > 120:
                            raise TimeoutError("Two-minute export limit reached")
                        batch = scenes[offset:offset+64]
                        result = runner.render((64, 64), batch)
                        error = float(np.max(np.abs(render_gaussians((64, 64), batch[0])-result.pixels[0])))
                        if not result.metadata.get("kernel_executed") or error > 2e-6:
                            raise ValueError("CUDA execution/parity check failed")
                        for index, pixels in enumerate(result.pixels):
                            modeled[acquired[offset+index]] = pixels
                        batches.append({"key": key, "scenes": len(batch), "cpu_sample_max_abs_error": error, "metadata": result.metadata})
                    atlas(output / f"{key}-model.png", modeled)
                    model_url = f"{key}-model.png"
                experiments.append({"key": key, "seed": seed, "condition": condition, "frame_count": 240, "budget": 32,
                                    "observed": f"{key}-observed.png", "model": model_url,
                                    "methods": {METHODS[r["name"]][0]: {"acquired_indices": r["run"]["acquired_indices"], "decisions": r["run"]["decisions"]} for r in rows}})
                evidence.append({"key": key, "events": events, "reference": f"{key}-reference.png", "metrics": {METHODS[r["name"]][0]: r["metrics"] for r in rows}})
                print(f"Verified/exported {key}", flush=True)
    finally:
        if runner:
            runner.close()
    manifest = {"version": 1, "scope": "Controlled synthetic unequal-budget comparison", "demo_seed": 304,
                "demo_selection": "Seed304 selected after evaluation as an illustrative successful precursor run; all six evaluation seeds retained.",
                "summary_sha256": json.loads((EVIDENCE / "verification.json").read_text())["summary_sha256"],
                "model_backend": "cuda-rust" if cuda else None, "experiments": experiments}
    (output / "evidence.json").write_text(json.dumps({"experiments": evidence}, separators=(",", ":")), encoding="utf-8")
    (output / "manifest.json").write_text(json.dumps(manifest, separators=(",", ":")), encoding="utf-8")
    verification = {"verified": True, "rows_checked": checked_rows, "all_metrics_recomputed": True,
                    "summary_sha256": manifest["summary_sha256"], "demo_selection": manifest["demo_selection"],
                    "export_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    "render_batches": batches, "elapsed_seconds": time.monotonic()-start,
                    "export_files_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir())}}
    (output / "export-verification.json").write_text(json.dumps(verification, indent=2), encoding="utf-8")
    print(f"PASS: {checked_rows} verified rows; {len(batches)} GPU batches; {verification['elapsed_seconds']:.1f}s", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "apps/web/public/demo/controlled/budget32")
    parser.add_argument("--cuda", action="store_true")
    args = parser.parse_args()
    export(args.output, args.cuda)
