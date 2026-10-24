"""Independent accounting and saved real-prediction checks for Phase4 evidence."""
import argparse
import hashlib
import json
from pathlib import Path
from statistics import median

import numpy as np
import tifffile

from photon.development import load_scenes, science_hash
from photon.gaussian import IntensityCalibration, render_gaussians


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark",type=Path,default=Path("runs/phase4-benchmark-verified"))
    parser.add_argument("--gpu-run",type=Path,default=Path("runs/phase4-real-gpu-verified"))
    parser.add_argument("--fallback-run",type=Path,default=Path("runs/phase4-real-cpu-fallback-verified"))
    parser.add_argument("--sequence",type=Path,default=Path("data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1"))
    args = parser.parse_args()
    benchmark = json.loads((args.benchmark/"benchmark.json").read_text())
    assert len(benchmark["cases"])==5
    counts = {tuple(case["gaussian_counts"]) for case in benchmark["cases"]}
    assert {(1,),(100,),(10000,),(100,)*6}.issubset(counts)
    binary = Path(".tools/photon-gpu/photon-gpu")
    assert hashlib.sha256(binary.read_bytes()).hexdigest()==benchmark["build"]["binary_sha256"]
    for case in benchmark["cases"]:
        profile = case["profiled_batch_metadata"]
        assert profile["backend"]=="cuda-rust" and profile["kernel_executed"]
        assert case["cpu_reference_median_ms"]==median(case["cpu_reference_ms"])
        assert case["warm_device_interval_median_ms"]==median(profile["warm_cuda_event_ms"])
        assert case["single_render_caller_median_ms"]==median(case["single_render_caller_ms"])
        assert case["caller_speedup_vs_cpu"]==case["cpu_reference_median_ms"]/case["single_render_caller_median_ms"]
        assert case["max_absolute_error"]<2e-5
        for call in case["single_render_metadata"]:
            assert call["warm_cuda_event_ms"]==[] and call["graph_capture_ms"]==0
            assert call["binary_sha256"]==benchmark["build"]["binary_sha256"]
    assert (args.benchmark/"timings.png").exists()
    runs = []
    for folder,backend in ((args.gpu_run,"cuda-rust"),(args.fallback_run,"cpu")):
        result = json.loads((folder/"comparison.json").read_text())
        assert result["actual_backend"]==backend and result["acquisitions"]==54
        assert result["same_acquisitions_decisions_and_state_as_cpu_run"]
        config = json.loads((folder/"replay/config.json").read_text())
        scenes = load_scenes(folder/"replay/forecasts.npz")
        calibration = IntensityCalibration(**config["normalization"])
        for row in result["targets"]:
            t = row["t"]
            with np.load(folder/f"prediction-{t}.npz",allow_pickle=False) as saved:
                pixels = saved["pixels"]
                assert str(saved["kind"])=="PREDICTED" and str(saved["backend"])==backend
                assert saved["based_on_indices"].tolist()==[i for i in result["acquired_indices"] if i<t]
            assert pixels.shape==tuple(config["shape"]) and pixels.dtype==np.float32
            assert np.isfinite(pixels).all() and pixels.min()>=0 and pixels.max()<=1
            cpu = render_gaussians(tuple(config["shape"]),scenes[t])
            np.testing.assert_allclose(pixels,cpu,rtol=2e-4,atol=2e-5)
            assert float(np.max(abs(pixels-cpu)))==row["max_absolute_pixel_error"]
            raw = tifffile.imread(args.sequence/"images"/f"mskcc_confocal_s1_t{t:03d}.tif")
            truth = calibration.normalize(raw)
            delta = pixels.astype(np.float64)-truth
            assert float(np.sum(delta*delta))/delta.size==row["selected_backend_metrics"]["mse"]
        if backend=="cpu":
            assert result["render_metadata"]["fallback_reason"] and not result["render_metadata"]["kernel_executed"]
        runs.append(result)
    assert runs[0]["acquired_indices"]==runs[1]["acquired_indices"]
    assert runs[0]["source_sha256"]==runs[1]["source_sha256"]
    assert runs[0]["science_code_sha256"]==runs[1]["science_code_sha256"]==benchmark["science_code_sha256"]==science_hash()
    for filename in ("decisions.jsonl","state.json"):
        assert (args.gpu_run/"replay"/filename).read_bytes()==(args.fallback_run/"replay"/filename).read_bytes()
    report = {"verified":True,"benchmark_cases":5,"gpu_and_fallback_acquisitions":54,
              "real_targets":[row["t"] for row in runs[0]["targets"]],
              "max_real_absolute_pixel_error":max(row["max_absolute_pixel_error"] for row in runs[0]["targets"]),
              "same_decisions_and_state":True,"real_source_error_metrics_recomputed":True,
              "all_measured_caller_speedups_below_one":all(case["caller_speedup_vs_cpu"]<1 for case in benchmark["cases"]),
              "science_code_sha256":science_hash(),"binary_sha256":benchmark["build"]["binary_sha256"]}
    Path("runs/phase4-verification.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
