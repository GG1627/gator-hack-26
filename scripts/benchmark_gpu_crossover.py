"""Refine the warmed full-caller crossover for synthetic 64x64 rendering."""
import argparse
import json
from pathlib import Path

import numpy as np
from benchmark_gpu import synthetic_scene
from benchmark_gpu_latency import stats,timed
from photon.development import science_hash
from photon.gpu import CudaRustRunner,render_gaussian_batch


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--repeats",type=int,default=15)
    args=p.parse_args()
    if args.output.exists() or args.repeats<10:p.error("New output and >=10 repetitions required")
    report={"science_code_sha256":science_hash(),"build":json.loads(Path(".tools/photon-gpu/build.json").read_text()),
            "scope":"Synthetic 64x64 rendering only. Warm context/JIT; all per-request transport, packing, repair and cleanup included. No acquisition-controller speedup inferred.","cases":[]}
    with CudaRustRunner(persistent=True) as worker:
        for g,b in ((200,1),(300,1),(400,1),(600,1),(100,2),(100,4)):
            scenes=[synthetic_scene(g,42+i) for i in range(b)]
            reference=render_gaussian_batch((64,64),scenes).pixels
            worker.render((64,64),scenes)
            cpu=[];gpu=[];error=0.
            for i in range(args.repeats):
                for backend in (("cpu","cuda-rust") if i%2==0 else ("cuda-rust","cpu")):
                    actual,ms=timed(lambda:render_gaussian_batch((64,64),scenes,backend=backend,runner=worker))
                    (cpu if backend=="cpu" else gpu).append(ms)
                    np.testing.assert_allclose(actual.pixels,reference,rtol=2e-4,atol=2e-5)
                    error=max(error,float(np.max(abs(actual.pixels-reference))))
            report["cases"].append({"g":g,"batch":b,"cpu":stats(cpu),"worker_full":stats(gpu),"max_absolute_error":error})
            print(json.dumps({"g":g,"b":b,"cpu":np.median(cpu),"gpu":np.median(gpu)}),flush=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2),encoding="utf-8")


if __name__=="__main__":main()
