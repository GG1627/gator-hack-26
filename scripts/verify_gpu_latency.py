"""Independently verify latency accounting, provenance and causal audit evidence."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from photon.development import science_hash
from photon.gpu import CudaRustRunner


def verify_stats(value):
    if isinstance(value,dict):
        if "samples_ms" in value:
            samples=value["samples_ms"]
            assert value["n"]==len(samples) and len(samples)>0
            assert np.isfinite(samples).all() and min(samples)>=0
            np.testing.assert_allclose(value["median_ms"],np.median(samples),rtol=1e-12)
            np.testing.assert_allclose(value["p95_ms"],np.percentile(samples,95),rtol=1e-12)
        for child in value.values(): verify_stats(child)
    elif isinstance(value,list):
        for child in value: verify_stats(child)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=Path("runs/cuda-latency-audit"))
    args=p.parse_args()
    matrix=json.loads((args.root/"matrix/latency.json").read_text())
    adaptive=json.loads((args.root/"adaptive/adaptive-latency.json").read_text())
    ablation=json.loads((args.root/"io-ablation.json").read_text())
    crossover=json.loads((args.root/"crossover.json").read_text())
    binary=hashlib.sha256(CudaRustRunner().binary.read_bytes()).hexdigest()
    sources=hashlib.sha256()
    crate=Path("crates/photon-gpu")
    for path in sorted(crate.rglob("*.rs")):
        sources.update(path.relative_to(crate).as_posix().encode());sources.update(path.read_bytes())
    for report in (matrix,adaptive,ablation,crossover):
        verify_stats(report)
        assert report["science_code_sha256"]==science_hash()
        assert report["build"]["binary_sha256"]==binary
        assert report["build"]["rust_source_sha256"]==sources.hexdigest()
    assert len(matrix["cases"])==8
    for case in matrix["cases"]:
        assert case["max_absolute_error"]<=2e-5
        assert case["cold_fresh_jit_full"]["n"]>=3
        assert all(m["jit_backend_compiles"]>0 for m in case["cold_metadata"])
        assert case["cpu_warm"]["n"]>=10 and case["warm_kernel"]["n"]>=10
        for m in case["worker_metadata"]:
            assert m["transport"]=="persistent-worker"
            assert m["jit_backend_compiles"]==0 and m["jit_disk_hits"]==0
            assert m["native_request_wall_ms"]>=m["output_write_ms"]
            assert m["python_batch_end_to_end_ms"]>=m["python_subprocess_wall_ms"]
        expected=[sum(m[k] for k in ("h2d_wall_ms","output_allocation_ms","first_launch_after_compile_wall_ms","d2h_wall_ms")) for m in case["worker_metadata"]]
        np.testing.assert_array_equal(case["gpu_plus_transfers"]["samples_ms"],expected)
        np.testing.assert_allclose(case["worker_e2e_speedup_vs_cpu"],case["cpu_warm"]["median_ms"]/case["worker_warm_full"]["median_ms"])
    assert adaptive["same_acquisitions_decisions_and_state_as_cpu"] and len(adaptive["acquired_indices"])==54
    original=Path("runs/mskcc-phase3-refined/photon_adaptive")
    assert json.loads((args.root/"adaptive/state.json").read_text())==json.loads((original/"state.json").read_text())
    trace=[json.loads(line) for line in (args.root/"adaptive/decisions.jsonl").read_text().splitlines()]
    old_trace=[json.loads(line) for line in (original/"decisions.jsonl").read_text().splitlines()]
    assert len(trace)==len(old_trace)==270
    for actual,old in zip(trace,old_trace): assert all(actual[k]==old[k] for k in actual)
    assert not adaptive["annotations_accessed"] and adaptive["probe_predictions_do_not_mutate_state"]
    assert len(adaptive["prediction_probes"])==6
    for probe in adaptive["prediction_probes"]:
        assert max(probe["based_on_indices"])<probe["t"]
        assert probe["max_pixel_error"]<=2e-5 and probe["max_uncertainty_error"]<=3e-5
    assert ablation["packing_10000"]["packed_values_bit_identical"]
    assert len(crossover["cases"])==6
    assert all(c["max_absolute_error"]<=2e-5 and c["cpu"]["n"]>=10 for c in crossover["cases"])
    result={"verified":True,"cases":8,"causal_prediction_probes":6,"science_sha256":science_hash(),"binary_sha256":binary,
            "note":"Recomputes stats/accounting and checks recorded parity/provenance; executable numerical tests separately rerun GPU outputs."}
    (args.root/"verification.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
