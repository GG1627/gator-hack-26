"""Time the actual causal CPU controller and optional CPU/GPU prediction path."""
import argparse
import hashlib
import json
from pathlib import Path
from time import perf_counter

import numpy as np

from benchmark_gpu_latency import stats, timed
from photon.adaptive import AdaptivePolicy
from photon.data import load_sequence
from photon.development import science_hash
from photon.gpu import CudaRustRunner
from photon.oracle import ReplayOracle
from photon.replay import RunRecord


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--repeats",type=int,default=15)
    args=p.parse_args()
    if args.output.exists() or args.repeats<10: p.error("Choose a new output and at least10 repetitions")
    args.output.mkdir(parents=True)
    source=Path("data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1")
    sequence=load_sequence(source,dataset_id="MSKCC-CONFOCAL")
    oracle=ReplayOracle(sequence,54)
    policy=AdaptivePolicy(); policy.reset(oracle.public_metadata(),54,42)
    history=[]; decisions=[]; decide_samples=[]; observe_samples=[]; read_samples=[]; probes=[]
    targets={1,134,268}
    with CudaRustRunner(persistent=True) as worker:
        for t in range(sequence.metadata.frame_count):
            oracle.advance(t)
            # Replay the exact same decision input repeatedly. Restore only the
            # fields decide mutates, then commit the final identical action.
            previous=(policy.clock,policy.pending,policy.last_decision)
            samples=[]; outcomes=[]
            for _ in range(args.repeats):
                policy.clock,policy.pending,policy.last_decision=previous
                action,ms=timed(lambda:policy.decide(t,tuple(history)))
                samples.append(ms); outcomes.append(action)
            assert len(set(outcomes))==1
            decide_samples.extend(samples)
            decisions.append({"t":t,"decision":"ACQUIRE" if action else "SKIP",**policy.last_decision})
            if action:
                frame,ms=timed(lambda:oracle.acquire(t)); read_samples.append(ms)
                _,ms=timed(lambda:policy.observe(frame)); observe_samples.append(ms)
                history.append(frame)
            if t in targets:
                assert not action and all(f.index<t for f in history)
                before=json.dumps(policy.model.state_dict(),sort_keys=True)
                for uncertainty in (False,True):
                    cpu_reference=policy.model.predict(t,include_uncertainty_map=uncertainty)
                    first_gpu,first_ms=timed(lambda:policy.model.predict(t,include_uncertainty_map=uncertainty,backend="cuda-rust",runner=worker))
                    cpu_ms=[]; gpu_ms=[]; error=0.; uncertainty_error=0.; native=[]
                    for _ in range(args.repeats):
                        # Alternate order to reduce consistent CPU/GPU order bias.
                        order=("cpu","cuda-rust") if _%2==0 else ("cuda-rust","cpu")
                        for backend in order:
                            prediction,ms=timed(lambda:policy.model.predict(t,include_uncertainty_map=uncertainty,backend=backend,runner=worker))
                            (cpu_ms if backend=="cpu" else gpu_ms).append(ms)
                            assert prediction.based_on_indices==cpu_reference.based_on_indices
                            if backend=="cuda-rust":
                                np.testing.assert_allclose(prediction.pixels,cpu_reference.pixels,rtol=2e-4,atol=2e-5)
                                error=max(error,float(np.max(abs(prediction.pixels-cpu_reference.pixels))))
                                if uncertainty:
                                    np.testing.assert_allclose(prediction.uncertainty_map,cpu_reference.uncertainty_map,rtol=3e-4,atol=3e-5)
                                    uncertainty_error=max(uncertainty_error,float(np.max(abs(prediction.uncertainty_map-cpu_reference.uncertainty_map))))
                                native.append(prediction.backend_metadata)
                    probes.append({"t":t,"uncertainty_map":uncertainty,"tracks":len(policy.model.tracks),
                                   "based_on_indices":list(cpu_reference.based_on_indices),"cpu_predict_full":stats(cpu_ms),
                                   "worker_predict_full":stats(gpu_ms),"first_gpu_predict_ms":first_ms,
                                   "max_pixel_error":error,"max_uncertainty_error":uncertainty_error,"gpu_metadata":native})
                assert before==json.dumps(policy.model.state_dict(),sort_keys=True)
                print(f"Causal probe {t} complete, acquired {len(history)}/54",flush=True)
    record=RunRecord(policy.name,42,54,oracle.finish(),tuple(decisions))
    oracle.evaluate_after_run(record)
    historical=Path("runs/mskcc-phase3-refined/photon_adaptive")
    old=json.loads((historical/"config.json").read_text())
    assert list(record.acquired_indices)==old["acquired_indices"]
    assert policy.model.state_dict()==json.loads((historical/"state.json").read_text())
    old_decisions=[json.loads(line) for line in (historical/"decisions.jsonl").read_text().splitlines()]
    for actual,old_row in zip(decisions,old_decisions):
        assert all(actual[key]==old_row[key] for key in actual)
    report={"science_code_sha256":science_hash(),"build":json.loads(Path(".tools/photon-gpu/build.json").read_text()),
            "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "source_sha256":sequence.fingerprint,"acquired_indices":record.acquired_indices,
            "same_acquisitions_decisions_and_state_as_cpu":True,
            "actual_controller_backend":"cpu in both modes; no CUDA scoring implementation exists or is added",
            "decision_cpu":stats(decide_samples),"observe_cpu":stats(observe_samples),"acquisition_io":stats(read_samples),
            "timing_scope":"decision samples repeat each of270 causal states; observe/I/O samples span54 captures; prediction CPU/GPU repeat same frozen state15 times by default. No whole-experiment speedup inferred.",
            "annotations_accessed":False,"probe_predictions_do_not_mutate_state":True,"prediction_probes":probes}
    (args.output/"state.json").write_text(json.dumps(policy.model.state_dict(),indent=2),encoding="utf-8")
    (args.output/"decisions.jsonl").write_text("".join(json.dumps(row)+"\n" for row in decisions),encoding="utf-8")
    (args.output/"adaptive-latency.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"decide":report["decision_cpu"]["median_ms"],"acquisitions":len(record.acquired_indices),"probes":len(probes)}),flush=True)


if __name__=="__main__":main()
