"""Controlled output-buffer and Python-packing ablations on identical inputs."""
import argparse
import json
import os
from pathlib import Path
import sys
import types
import zipfile

import numpy as np
from benchmark_gpu_latency import stats, timed
from benchmark_gpu import synthetic_scene
from photon.development import load_scenes, science_hash
from photon.gpu import CudaRustRunner, pack_batch, render_gaussian_batch


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,required=True)
    args = p.parse_args()
    if args.output.exists(): p.error("Use a new output")
    root = Path(__file__).resolve().parents[1]
    report = {"science_code_sha256":science_hash(),"build":json.loads((root/".tools/photon-gpu/build.json").read_text()),"output_buffer_ablation":[]}
    real = load_scenes(root/"runs/mskcc-phase3-refinement/paced_robust/held_scenes.npz")[260]
    reference = render_gaussian_batch((41,512,512),[real]).pixels
    previous = os.environ.get("PHOTON_GPU_SMALL_WRITES")
    try:
        for small in (True,False):
            if small: os.environ["PHOTON_GPU_SMALL_WRITES"]="1"
            else: os.environ.pop("PHOTON_GPU_SMALL_WRITES",None)
            with CudaRustRunner(persistent=True) as worker:
                worker.render((41,512,512),[real])
                samples=[]; metadata=[]
                for _ in range(10):
                    actual,ms = timed(lambda:worker.render((41,512,512),[real]))
                    np.testing.assert_allclose(actual.pixels,reference,rtol=2e-4,atol=2e-5)
                    samples.append(ms); metadata.append(actual.metadata)
            report["output_buffer_ablation"].append({"small_writes":small,"full":stats(samples),"metadata":metadata})
    finally:
        if previous is None: os.environ.pop("PHOTON_GPU_SMALL_WRITES",None)
        else: os.environ["PHOTON_GPU_SMALL_WRITES"]=previous
    with zipfile.ZipFile(root/"runs/phase4-source-snapshot.zip") as archive:
        name = next(n for n in archive.namelist() if n.endswith("photon/gpu.py"))
        old = types.ModuleType("photon_gpu_before_worker")
        sys.modules[old.__name__]=old
        exec(compile(archive.read(name),name,"exec"),old.__dict__)
    scene = [synthetic_scene(10000)]
    _,_,current = pack_batch((64,64),scene)
    _,_,baseline = old.pack_batch((64,64),scene)
    np.testing.assert_array_equal(current,baseline)
    report["packing_10000"] = {"before":stats([timed(lambda:old.pack_batch((64,64),scene))[1] for _ in range(10)]),
                               "after":stats([timed(lambda:pack_batch((64,64),scene))[1] for _ in range(10)]),"packed_values_bit_identical":True}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"buffers":[{"small":r["small_writes"],"median_ms":r["full"]["median_ms"]} for r in report["output_buffer_ablation"]],"packing":report["packing_10000"]}),flush=True)


if __name__=="__main__": main()
