"""Verify the tiny controlled ledger and export its recorded visual comparison.

No controller is rerun here. CUDA model renders use acquired images only and
are checked against the CPU renderer. Event/reference data is a separate file.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from experiments.controlled.benchmark import make_clip, score
from photon.gaussian import GaussianFitConfig, IntensityCalibration, detect_and_fit, render_gaussians
from photon.gpu import CudaRustRunner


def atlas(path, images):
    canvas=Image.new("L",(16*64,15*64))
    for t,image in enumerate(images):
        canvas.paste(Image.fromarray(np.uint8(np.clip(image,0,1)*255)),((t%16)*64,(t//16)*64))
    canvas.save(path)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,default=Path("runs/controlled-heldout-v1/summary.json"))
    parser.add_argument("--output",type=Path,default=Path("apps/web/public/demo/controlled"))
    parser.add_argument("--cuda",action="store_true")
    args=parser.parse_args()
    start=time.monotonic()
    summary=json.loads(args.input.read_text())
    if summary["status"]!="complete":
        raise ValueError("Incomplete benchmark cannot be exported")
    for name,expected in summary["protocol"]["source_sha256"].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:
            raise ValueError(f"Changed benchmark source: {name}")
    args.output.mkdir(parents=True,exist_ok=True)
    experiments=[]
    evidence=[]
    render_metadata=[]
    runner=CudaRustRunner(timeout=25,persistent=True) if args.cuda else None
    try:
        for seed in summary["protocol"]["seeds"]:
            for condition in summary["protocol"]["conditions"]:
                if time.monotonic()-start>120:
                    raise TimeoutError("Export exceeded two-minute limit")
                clip,events,_=make_clip(seed,condition)
                clip_hash=hashlib.sha256(clip.tobytes()).hexdigest()
                rows=[r for r in summary["rows"] if r["seed"]==seed and r["condition"]==condition]
                if len(rows)!=5:
                    raise ValueError("Missing comparison")
                for row in rows:
                    record=row["run"]
                    indices=record["acquired_indices"]
                    if row["sequence_sha256"]!=clip_hash or row["events"]!=events:
                        raise ValueError("Synthetic source/labels changed")
                    if len(indices)!=40 or indices!=sorted(set(indices)) or indices[0]!=0:
                        raise ValueError("Unequal/invalid budget")
                    if [d["t"] for d in record["decisions"] if d["decision"]=="ACQUIRE"]!=indices:
                        raise ValueError("Trace does not match acquisition history")
                    recomputed=score(record,clip,events)
                    for metric,value in recomputed.items():
                        if value!=row["metrics"][metric]:
                            raise ValueError(f"Metric mismatch: {metric}")
                key=f"{seed}-{condition}"
                # Atlas contains the union of actually acquired pixels; other cells stay blank.
                acquired=sorted(set(t for row in rows for t in row["run"]["acquired_indices"]))
                observed=np.zeros_like(clip)
                observed[acquired]=clip[acquired]
                atlas(args.output/f"{key}-observed.png",observed)
                # Reference is evaluation-only, requested by UI only after reveal.
                atlas(args.output/f"{key}-reference.png",clip)
                model_url=None
                if runner:
                    calibration=IntensityCalibration.from_image(clip[0])
                    scenes=[detect_and_fit(calibration.normalize(clip[t],clip=False),(1.,1.),
                                           calibration.noise_sigma,GaussianFitConfig(min_voxels=8))[0] for t in acquired]
                    modeled=np.zeros_like(clip)
                    for offset in range(0,len(scenes),64):
                        batch=scenes[offset:offset+64]
                        result=runner.render((64,64),batch)
                        if not result.metadata.get("kernel_executed"):
                            raise ValueError("CUDA kernel did not execute")
                        reference=render_gaussians((64,64),batch[0])
                        error=float(np.max(np.abs(reference-result.pixels[0])))
                        if error>2e-6:
                            raise ValueError(f"GPU/CPU mismatch {error}")
                        for i,pixels in enumerate(result.pixels):
                            modeled[acquired[offset+i]]=pixels
                        render_metadata.append({"key":key,"scenes":len(batch),"cpu_sample_max_abs_error":error,
                                                "metadata":result.metadata})
                    atlas(args.output/f"{key}-model.png",modeled)
                    model_url=f"{key}-model.png"
                experiments.append({"key":key,"seed":seed,"condition":condition,"frame_count":240,"budget":40,
                                    "observed":f"{key}-observed.png","model":model_url,
                                    "methods":{r["run"]["policy"]:{"acquired_indices":r["run"]["acquired_indices"],
                                                "decisions":r["run"]["decisions"]} for r in rows}})
                evidence.append({"key":key,"events":events,"reference":f"{key}-reference.png",
                                 "metrics":{r["run"]["policy"]:r["metrics"] for r in rows}})
                print(f"Verified/exported {key}",flush=True)
    finally:
        if runner:
            runner.close()
    manifest={"version":1,"scope":"Controlled synthetic experiment; not biological evidence",
              "summary_sha256":hashlib.sha256(args.input.read_bytes()).hexdigest(),
              "demo_seed":2026,"frame_count":240,"budget":40,"tolerance_frames":1,
              "experiments":experiments,"model_backend":"cuda-rust" if runner else None}
    (args.output/"manifest.json").write_text(json.dumps(manifest,separators=(",",":")))
    (args.output/"evidence.json").write_text(json.dumps({"experiments":evidence},separators=(",",":")))
    verification={"status":"pass","rows_checked":len(summary["rows"]),"source_hashes_checked":True,
                  "all_metrics_recomputed":True,"render_batches":render_metadata,
                  "elapsed_seconds":time.monotonic()-start,"summary_sha256":manifest["summary_sha256"]}
    (args.input.parent/"export-verification.json").write_text(json.dumps(verification,indent=2))
    print(f"PASS: {len(summary['rows'])} rows; {len(render_metadata)} GPU batches; {verification['elapsed_seconds']:.1f}s")


if __name__=="__main__":
    main()
