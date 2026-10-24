"""Real causal replay plus native GPU rendering parity; annotations stay closed."""
import argparse
import json
from pathlib import Path

import numpy as np

from photon.adaptive import AdaptivePolicy
from photon.data import load_sequence
from photon.development import image_error, record_development_run, science_hash
from photon.gpu import CudaRustRunner, render_gaussian_batch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sequence",type=Path,default=Path("data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1"))
    parser.add_argument("--output",type=Path,default=Path("runs/phase4-real"))
    parser.add_argument("--backend",choices=["cpu","cuda-rust","auto"],default="cuda-rust")
    parser.add_argument("--persistent",action="store_true",help="Reuse a CUDA context/JIT cache; useful across repeated render calls")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output exists; choose a new directory")
    sequence = load_sequence(args.sequence,dataset_id="MSKCC-CONFOCAL")
    if sequence.metadata.sequence_id!="mskcc_confocal_s1":
        parser.error("Phase4 validation uses development s1 only")
    run = record_development_run(sequence,AdaptivePolicy(),54,42,"phase4",args.output/"replay")
    # Geometry was frozen at decision time from past acquisitions. GPU receives
    # those descriptors and public shape only, not images, oracle or annotations.
    targets = [1,134,268]
    scenes = [run.forecasts[t] for t in targets]
    cpu = render_gaussian_batch(sequence.metadata.shape,scenes,backend="cpu")
    with CudaRustRunner(persistent=args.persistent) as runner:
        rendered = render_gaussian_batch(sequence.metadata.shape,scenes,backend=args.backend,runner=runner)
    np.testing.assert_allclose(rendered.pixels,cpu.pixels,rtol=2e-4,atol=2e-5)
    historical = Path("runs/mskcc-phase3-refined/photon_adaptive")
    cpu_config = json.loads((historical/"config.json").read_text())
    assert cpu_config["sequence_sha256"]==sequence.fingerprint
    assert list(run.record.acquired_indices)==cpu_config["acquired_indices"]
    for filename in ("decisions.jsonl","state.json"):
        assert (args.output/"replay"/filename).read_bytes()==(historical/filename).read_bytes(),filename
    errors = []
    for b,t in enumerate(targets):
        history = tuple(index for index in run.record.acquired_indices if index<t)
        truth = run.calibration.normalize(run.oracle.read_evaluation_after_run(run.record,t).pixels)
        roi = truth > .1
        cpu_metrics = image_error(cpu.pixels[b],truth,roi)
        gpu_metrics = image_error(rendered.pixels[b],truth,roi)
        for metrics in (cpu_metrics,gpu_metrics):
            metrics["mse"] = metrics["squared_error_sum"]/metrics["voxel_count"]
            metrics["mae"] = metrics["absolute_error_sum"]/metrics["voxel_count"]
        errors.append({"t":t,"cpu_metrics":cpu_metrics,"selected_backend_metrics":gpu_metrics,
                       "max_absolute_pixel_error":float(np.max(abs(cpu.pixels[b]-rendered.pixels[b])))})
        np.savez_compressed(args.output/f"prediction-{t}.npz",pixels=rendered.pixels[b],kind="PREDICTED",
                            based_on_indices=history,backend=rendered.metadata["backend"])
    summary = {"source_sha256":sequence.fingerprint,"science_code_sha256":science_hash(),
               "requested_backend":args.backend,"actual_backend":rendered.metadata["backend"],"render_metadata":rendered.metadata,
               "cpu_render_metadata":cpu.metadata,"acquisitions":len(run.record.acquired_indices),
               "relative_exposure_proxy":len(run.record.acquired_indices)/sequence.metadata.frame_count,
               "event_coverage":None,"event_coverage_reason":"Phase4 rendering validation; annotations are not opened",
               "acquired_indices":run.record.acquired_indices,"same_acquisitions_decisions_and_state_as_cpu_run":True,
               "targets":errors,"parity_tolerance":{"rtol":2e-4,"atol":2e-5},
               "scope":"CPU scientific decisions unchanged; GPU accelerates rendering of causally frozen states; post-hoc errors only; no annotations accessed"}
    (args.output/"comparison.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps({"backend":summary["actual_backend"],"acquisitions":summary["acquisitions"],
                      "pixel_errors":[row["max_absolute_pixel_error"] for row in errors]},indent=2),flush=True)


if __name__=="__main__":
    main()
