"""Measured CPU/CUDA Rust renderer comparison; no fabricated speedups."""
import argparse
import json
import os
from pathlib import Path
import platform
from statistics import median
import subprocess
from time import perf_counter
import uuid

import matplotlib
matplotlib.use("Agg")
import numpy as np
from plot_gpu_benchmark import plot_benchmark

from photon.development import load_scenes, science_hash
from photon.gaussian import Gaussian
from photon.gpu import CudaRustRunner, render_gaussian_batch


def synthetic_scene(count, seed=42):
    rng = np.random.default_rng(seed)
    result = []
    for _ in range(count):
        a = rng.normal(size=(2,2))*0.25
        covariance = a@a.T+np.diag(rng.uniform(.4,3.,2))
        result.append(Gaussian(rng.uniform(0,63,2),covariance,float(rng.uniform(.2,.8)/max(1,np.sqrt(count)))))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=Path("runs/phase4-benchmark"))
    parser.add_argument("--repeats",type=int,default=5)
    args = parser.parse_args()
    if args.output.exists() or not 3 <= args.repeats <= 20:
        parser.error("Choose a new output and repeats in [3,20]")
    root = Path(__file__).resolve().parents[1]
    build = json.loads((root/".tools/photon-gpu/build.json").read_text())
    if build["profile"] != "release":
        parser.error("Benchmark requires a release build: scripts/build_gpu.py")
    args.output.mkdir(parents=True)
    runner = CudaRustRunner(cache_namespace="bench-"+uuid.uuid4().hex)
    cases = [(f"G={g}, B=1",(64,64),[synthetic_scene(g)]) for g in (1,100,10000)]
    cases.append(("G=100, B=6",(64,64),[synthetic_scene(100,42+i) for i in range(6)]))
    archive = root/"runs/mskcc-phase3-refinement/paced_robust/held_scenes.npz"
    if not archive.exists():
        parser.error("Real observed-state archive missing; run the Phase3 refinement first")
    real = load_scenes(archive)[260]
    cases.append((f"Real t260: G={len(real)}, B=1",(41,512,512),[real]))
    report = {"science_code_sha256":science_hash(),"build":build,"seed":42,"cpu_platform":platform.platform(),
              "cpu_processor":platform.processor(),"python":platform.python_version(),"numpy":np.__version__,
              "matplotlib":matplotlib.__version__,
              "thread_environment":{key:os.environ.get(key) for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS")},
              "tolerance":{"rtol":2e-4,"atol":2e-5},"conditions":"active Windows laptop via WSL2; no clock locking or GPU exclusivity",
              "protocol":"CPU warmups then repeated full reference; warmed CUDA graph event intervals; separate single-render Python caller calls including all overhead",
              "cache_namespace":runner.cache_namespace,"cases":[]}
    try:
        report["nvidia_smi"] = subprocess.check_output(["nvidia-smi","--query-gpu=name,driver_version,memory.total,compute_cap","--format=csv"],text=True).strip()
    except (OSError,subprocess.CalledProcessError):
        report["nvidia_smi"] = None
    for label,shape,scenes in cases:
        print(f"Benchmarking {label}, shape={shape}",flush=True)
        reference = render_gaussian_batch(shape,scenes)
        cpu_ms = []
        for _ in range(args.repeats):
            start = perf_counter()
            render_gaussian_batch(shape,scenes)
            cpu_ms.append((perf_counter()-start)*1000)
        profiled = runner.render(shape,scenes,repeats=args.repeats)
        np.testing.assert_allclose(profiled.pixels,reference.pixels,rtol=2e-4,atol=2e-5)
        caller_ms, calls = [], []
        for _ in range(3):
            start = perf_counter()
            actual = runner.render(shape,scenes,repeats=0)
            caller_ms.append((perf_counter()-start)*1000)
            np.testing.assert_allclose(actual.pixels,reference.pixels,rtol=2e-4,atol=2e-5)
            calls.append(actual.metadata)
        event_median = median(profiled.metadata["warm_cuda_event_ms"])
        case = {"label":label,"shape":shape,"batch":len(scenes),"gaussian_counts":[len(scene) for scene in scenes],
                "cpu_reference_ms":cpu_ms,"cpu_reference_median_ms":median(cpu_ms),
                "warm_device_interval_median_ms":event_median,
                "single_render_caller_ms":caller_ms,"single_render_caller_median_ms":median(caller_ms),
                "caller_speedup_vs_cpu":median(cpu_ms)/median(caller_ms),
                "device_interval_ratio_vs_full_cpu_reference":median(cpu_ms)/event_median,
                "max_absolute_error":float(np.max(abs(profiled.pixels-reference.pixels))),
                "profiled_batch_metadata":profiled.metadata,"single_render_metadata":calls}
        report["cases"].append(case)
        (args.output/"benchmark.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
        print(json.dumps({key:case[key] for key in ("label","cpu_reference_median_ms","warm_device_interval_median_ms",
                                                    "single_render_caller_median_ms","caller_speedup_vs_cpu","max_absolute_error")}),flush=True)
    plot_benchmark(report,args.output/"timings.png")


if __name__=="__main__":
    main()
