"""Reproducible cold/warm/full-caller latency audit; no policy or oracle inputs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
from time import perf_counter
import uuid

import numpy as np

from benchmark_gpu import synthetic_scene
from photon.development import load_scenes, science_hash
from photon.gaussian import Gaussian
from photon.gpu import CudaRustRunner, render_gaussian_batch


def stats(samples):
    return {"n":len(samples), "median_ms":float(np.median(samples)),
            "p95_ms":float(np.percentile(samples,95)), "samples_ms":samples}


def timed(call):
    start = perf_counter()
    value = call()
    return value, (perf_counter()-start)*1000


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--repeats",type=int,default=15)
    parser.add_argument("--cold-repeats",type=int,default=5)
    args = parser.parse_args()
    if args.output.exists() or args.repeats < 10 or args.cold_repeats < 3:
        parser.error("Use a new output, at least10 warm and3 cold repetitions")
    root = Path(__file__).resolve().parents[1]
    args.output.mkdir(parents=True)
    report = {"science_code_sha256":science_hash(),"build":json.loads((root/".tools/photon-gpu/build.json").read_text()),
              "benchmark_script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "cpu_platform":platform.platform(),"cpu_processor":platform.processor(),
              "python":platform.python_version(),"numpy":np.__version__,"seed":42,
              "conditions":"active Windows laptop / already-running WSL2; no clock locking or exclusive GPU",
              "cold_definition":"fresh native process, context and unique empty cuTile disk cache per sample; OS/driver/WSL VM not reset",
              "warm_definition":"worker startup and one same-geometry warmup excluded; each production request re-packs, copies, allocates, renders once, reads, repairs and cleans up",
              "p95_definition":"NumPy linear sample percentile; small cold n is exploratory, not a stable tail guarantee",
              "gpu_plus_transfers_definition":"synchronized H2D + output allocation/fill + single render host dispatch/sync + D2H; excludes IPC/JIT preparation and CPU repair",
              "kernel_definition":"CUDA events around resident warmed graph replay, end event synchronized; not an application speedup",
              "scheduler_scope":"renderer only; AdaptivePolicy.decide and observe remain CPU for every backend",
              "thread_environment":{k:os.environ.get(k) for k in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS")},
              "cases":[]}
    report["nvidia_smi"] = subprocess.check_output(["nvidia-smi","--query-gpu=name,driver_version,memory.total,compute_cap","--format=csv"],text=True).strip()
    def save():
        (args.output/"latency.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    # Isolate WSL launch without CUDA initialization or bulk transfer.
    ping = CudaRustRunner()
    command,env = ping.command("--ping")
    report["wsl_native_ping"] = stats([timed(lambda:subprocess.run(command,env=env,capture_output=True,check=True))[1] for _ in range(args.repeats)])
    report["wsl_true"] = stats([timed(lambda:subprocess.run(["wsl","-d",os.environ.get("PHOTON_WSL_DISTRO","Ubuntu-22.04"),"--exec","/bin/true"],capture_output=True,check=True))[1] for _ in range(args.repeats)])
    real = load_scenes(root/"runs/mskcc-phase3-refinement/paced_robust/held_scenes.npz")[260]
    # Same dimensionality and +/- physical-axis perturbations used by predict().
    ensemble = [real]
    for axis in range(3):
        for direction in (-1,1):
            offset = np.zeros(3); offset[axis] = direction*.2/(.75,.15,.15)[axis]
            ensemble.append([Gaussian(g.center+offset,g.covariance,g.amplitude) for g in real])
    cases = [(f"synthetic-G{g}-B1",(64,64),[synthetic_scene(g)]) for g in (1,10,100,1000,10000)]
    cases += [("synthetic-G100-B7",(64,64),[synthetic_scene(100,42+i) for i in range(7)]),
              ("real-s1-t260-B1",(41,512,512),[real]),("real-s1-t260-B7",(41,512,512),ensemble)]
    components = ("parse_ms","context_ms","h2d_wall_ms","output_allocation_ms","jit_prepare_wall_ms",
                  "first_launch_after_compile_wall_ms","d2h_wall_ms","output_write_ms","native_request_wall_ms",
                  "python_pack_ms","python_input_write_ms","python_output_read_validate_ms","python_cleanup_ms",
                  "cpu_boundary_repair_ms","python_subprocess_wall_ms")
    for label,shape,scenes in cases:
        print("Benchmarking "+label,flush=True)
        reference = render_gaussian_batch(shape,scenes).pixels
        max_error = 0.
        def checked(runner, repeats=0):
            nonlocal max_error
            actual,ms = timed(lambda:runner.render(shape,scenes,repeats=repeats))
            np.testing.assert_allclose(actual.pixels,reference,rtol=2e-4,atol=2e-5)
            max_error = max(max_error,float(np.max(abs(actual.pixels-reference))))
            return ms, actual.metadata
        cpu = [timed(lambda:render_gaussian_batch(shape,scenes))[1] for _ in range(args.repeats)]
        cold = [checked(CudaRustRunner(cache_namespace="cold-"+uuid.uuid4().hex)) for _ in range(args.cold_repeats)]
        disk_runner = CudaRustRunner(cache_namespace="disk-"+uuid.uuid4().hex)
        checked(disk_runner)  # seed disk cache, but no persistent context
        one_shot = [checked(disk_runner) for _ in range(args.repeats)]
        with CudaRustRunner(persistent=True,cache_namespace=disk_runner.cache_namespace) as worker:
            first_ms, first_metadata = checked(worker)
            warm = [checked(worker) for _ in range(args.repeats)]
            _,profile = checked(worker,repeats=args.repeats)
            startup = worker.worker_startup_ms
        gpu_transfer = [sum(m[k] for k in ("h2d_wall_ms","output_allocation_ms","first_launch_after_compile_wall_ms","d2h_wall_ms")) for _,m in warm]
        case = {"label":label,"shape":shape,"batch":len(scenes),"gaussian_counts":[len(s) for s in scenes],
                "cpu_warm":stats(cpu),"cold_fresh_jit_full":stats([ms for ms,_ in cold]),
                "one_shot_disk_cache_full":stats([ms for ms,_ in one_shot]),
                "worker_warm_full":stats([ms for ms,_ in warm]),"gpu_plus_transfers":stats(gpu_transfer),
                "warm_kernel":stats(profile["warm_cuda_event_ms"]),
                "worker_startup_ms":startup,"worker_first_request_full_ms":first_ms,
                "worker_first_request_metadata":first_metadata,
                "cold_metadata":[m for _,m in cold],"one_shot_metadata":[m for _,m in one_shot],"worker_metadata":[m for _,m in warm],
                "worker_components":{k:stats([m[k] for _,m in warm]) for k in components},
                "one_shot_components":{k:stats([m[k] for _,m in one_shot]) for k in components},
                "max_absolute_error":max_error,"worker_e2e_speedup_vs_cpu":float(np.median(cpu)/np.median([ms for ms,_ in warm]))}
        # Batching comparison includes seven complete Python calls vs one batch.
        if label in ("synthetic-G100-B7","real-s1-t260-B7"):
            with CudaRustRunner(persistent=True) as worker:
                worker.render(shape,[scenes[0]])
                sequential = []
                for _ in range(args.repeats):
                    start = perf_counter()
                    for scene in scenes:
                        actual = worker.render(shape,[scene])
                    sequential.append((perf_counter()-start)*1000)
                case["worker_seven_sequential_full"] = stats(sequential)
        report["cases"].append(case); save()
        print(json.dumps({"case":label,"cpu":case["cpu_warm"],"worker":case["worker_warm_full"],"max_error":max_error}),flush=True)
    save()


if __name__=="__main__":
    main()
