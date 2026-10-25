"""Registered s1-only full causal acquisition ablation, outside frozen Phase5."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib.util
from importlib.metadata import version
from itertools import combinations
import json
import os
from pathlib import Path
import sys
import traceback
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

import photon.adaptive as canonical_adaptive
from photon.data import load_sequence
from photon.development import aggregate_errors, evaluate_development, record_development_run, science_hash
from photon.policy import ScheduledPolicy
from experiments.perception.watershed import WatershedConfig
from scripts.probe_perception_forecasts import candidate_tracking_module


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+"\n",encoding="utf-8")


def check_phase5():
    spec=importlib.util.spec_from_file_location("perception_frozen_check",ROOT/"scripts/run_phase5.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.check_registration(ROOT/"runs/phase5")


def make_candidate_policy(config=None,progress=None):
    """Reuse controller source in a private namespace; canonical globals stay intact."""
    name="photon._perception_ablation_adaptive"
    spec=importlib.util.spec_from_file_location(name,canonical_adaptive.__file__)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    module.GaussianSceneModel=candidate_tracking_module().GaussianSceneModel
    class ReportingPolicy(module.AdaptivePolicy):
        def observe(self,frame):
            super().observe(frame)
            if progress is not None: progress(frame.index,len(self.indices))
    return ReportingPolicy(config=config or canonical_adaptive.controller_variant("paced_robust"))


def pairwise_scores(rows):
    result={}
    for left,right in combinations(rows,2):
        left_rows={row["t"]:row for row in rows[left]}
        right_rows={row["t"]:row for row in rows[right]}
        targets=sorted(left_rows.keys() & right_rows.keys())
        result[f"{left}_vs_{right}"]={"indices":targets,"frames":len(targets),
            "methods":{name:{estimator:aggregate_errors([lookup[t]["errors"][estimator] for t in targets])
                               for estimator in ("raw_hold","gaussian_hold","gaussian_forecast")}
                       for name,lookup in [(left,left_rows),(right,right_rows)]}}
    return result


def verify_accounting(summary,rows,frame_count,budget):
    for name,value in summary["variants"].items():
        acquired=value["acquired_indices"]
        targets=[row["t"] for row in rows[name]]
        if len(acquired)!=budget or acquired[0]!=0 or len(set(acquired))!=budget:
            raise ValueError(f"Invalid acquisition budget: {name}")
        if sorted(targets)!=sorted(set(range(frame_count))-set(acquired)):
            raise ValueError(f"Wrong withheld target ledger: {name}")
        for estimator,aggregate in value["own_withheld"].items():
            recomputed=aggregate_errors([row["errors"][estimator] for row in rows[name]])
            if aggregate!=recomputed: raise ValueError(f"Scalar accounting mismatch: {name}/{estimator}")


class Transcript:
    def __init__(self,stream,path): self.stream,self.file=stream,Path(path).open("w",encoding="utf-8")
    def write(self,value): self.stream.write(value);self.file.write(value);return len(value)
    def flush(self): self.stream.flush();self.file.flush()


def run(output):
    phase5,phase5_hash=check_phase5()
    status_path=output/"status.json"
    def status(stage,**extra):
        write_json(status_path,{"state":"running","pid":os.getpid(),"stage":stage,
                                "updated_at":datetime.now(timezone.utc).isoformat(),**extra})
    status("validate_development_sequence")
    if os.name=="nt":
        import ctypes
        from ctypes import wintypes
        kernel=ctypes.windll.kernel32
        kernel.GetCurrentProcess.restype=wintypes.HANDLE
        kernel.SetPriorityClass.argtypes=[wintypes.HANDLE,wintypes.DWORD]
        kernel.SetPriorityClass.restype=wintypes.BOOL
        if not kernel.SetPriorityClass(kernel.GetCurrentProcess(),0x4000):
            raise OSError("Could not lower experiment process priority")
    sequence=load_sequence(ROOT/"data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1",dataset_id="MSKCC-CONFOCAL")
    if sequence.metadata.sequence_id!="mskcc_confocal_s1" or sequence.metadata.split!="development":
        raise ValueError("Only the s1 development sequence is allowed")
    names=("fixed","adaptive","watershed");budget=54;seed=42
    source_paths=[ROOT/path for path in phase5["implementation_hashes"]]
    source_paths += [Path(__file__),ROOT/"scripts/probe_perception_forecasts.py",
        ROOT/"experiments/__init__.py",ROOT/"experiments/perception/__init__.py",
        ROOT/"experiments/perception/watershed.py",ROOT/"docs/PERCEPTION_ABLATION_PLAN.md",
        ROOT/"tests/test_perception_ablation.py"]
    hashes={str(p.relative_to(ROOT)).replace("\\","/"):digest(p) for p in source_paths}
    protocol={"scope":"registered exploratory s1 development, not held-out evidence", "names":names,
        "frame_count":270,"budget":budget,"seed":seed,"event_tolerance_frames":1,"foreground_threshold":.1,
        "controller":asdict(canonical_adaptive.controller_variant("paced_robust")),"watershed":asdict(WatershedConfig()),
        "sequence_sha256":sequence.fingerprint,"base_science_sha256":science_hash(),"source_sha256":hashes,
        "phase5_protocol_sha256":phase5_hash,"versions":{name:version(name) for name in ["numpy","scipy","scikit-image","lazy-loader"]},
        "python":sys.version,"numerical_threads":{"OMP_NUM_THREADS":os.getenv("OMP_NUM_THREADS"),
            "OPENBLAS_NUM_THREADS":os.getenv("OPENBLAS_NUM_THREADS")},"windows_priority":"below_normal" if os.name=="nt" else "default",
        "decision_rule":"more covered divisions than adaptive and pairwise-common raw-hold MSE no higher; report fixed comparator regardless"}
    write_json(output/"protocol.json",protocol)
    with zipfile.ZipFile(output/"source.zip","w",zipfile.ZIP_DEFLATED) as archive:
        for path in source_paths: archive.write(path,path.relative_to(ROOT))
        archive.write(output/"protocol.json","experiment-protocol.json")
    write_json(output/"registration.json",{"protocol_sha256":digest(output/"protocol.json"),"source_zip_sha256":digest(output/"source.zip"),"outcomes_computed_at_registration":False})
    print("Registered detector-only comparison. Starting causal acquisition; no target/label scoring.",flush=True)
    runs=[]
    for name in names:
        status("acquisition",variant=name,acquisitions=0)
        if name=="fixed": policy=ScheduledPolicy("fixed_interval")
        elif name=="adaptive": policy=canonical_adaptive.AdaptivePolicy(config=canonical_adaptive.controller_variant("paced_robust"))
        else: policy=make_candidate_policy(progress=lambda t,n:status("acquisition",variant="watershed",source_frame=t,acquisitions=n))
        run=record_development_run(sequence,policy,budget,seed,name,output/name)
        config_path=output/name/"config.json";config=json.loads(config_path.read_text())
        config.update(experiment_protocol_sha256=digest(output/"protocol.json"),
            experimental_source_sha256=hashes,perception="watershed" if name=="watershed" else "thresholded_components")
        if name=="watershed":
            config["model_version"]="experimental-watershed-moment-v1"
            state_path=output/name/"state.json";state=json.loads(state_path.read_text());state["model_version"]=config["model_version"];write_json(state_path,state)
        write_json(config_path,config);runs.append(run)
    historical=json.loads((ROOT/"runs/mskcc-phase3-refined/photon_adaptive/config.json").read_text())
    if list(runs[1].record.acquired_indices)!=historical["acquired_indices"]:
        raise ValueError("Original adaptive controller does not reproduce saved deployed s1 schedule")
    check_phase5()
    print("All three runs closed at equal budgets; original adaptive trace reproduced. Now revealing offline evidence.",flush=True)
    status("offline_evaluation",all_acquisition_runs_closed=True)
    summary,rows=evaluate_development(runs,annotation_path=ROOT/"data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1/tracks/tracks_mamut.xml")
    verify_accounting(summary,rows,270,budget)
    summary["pairwise_common"]=pairwise_scores(rows)
    pair=summary["pairwise_common"]["adaptive_vs_watershed"]["methods"]
    more_events=summary["variants"]["watershed"]["event"]["covered_events"]>summary["variants"]["adaptive"]["event"]["covered_events"]
    no_worse_raw=pair["watershed"]["raw_hold"]["mse"]<=pair["adaptive"]["raw_hold"]["mse"]
    summary["development_gate"]={"more_events_than_original_adaptive":more_events,"no_worse_pairwise_raw_hold_mse":no_worse_raw,
        "criterion_met":more_events and no_worse_raw,"automatic_production_promotion":False}
    summary["protocol_sha256"]=digest(output/"protocol.json")
    summary["verification"]="first-pass image scores; scalar accounting checked; independent full rerender pending"
    registration=json.loads((output/"registration.json").read_text())
    if digest(output/"protocol.json")!=registration["protocol_sha256"] or digest(output/"source.zip")!=registration["source_zip_sha256"]:
        raise ValueError("Experiment registration changed")
    if any(digest(ROOT/path)!=expected for path,expected in hashes.items()):
        raise ValueError("Registered experiment source changed during execution")
    check_phase5()
    for name in names:
        write_json(output/name/"metrics.json",summary["variants"][name])
        (output/name/"evaluation.jsonl").write_text("".join(json.dumps(row)+"\n" for row in rows[name]),encoding="utf-8")
    write_json(output/"summary.json",summary)
    check_phase5()
    write_json(status_path,{"state":"complete","pid":os.getpid(),"stage":"first_pass_complete",
        "updated_at":datetime.now(timezone.utc).isoformat(),"independent_rerender_verified":False})
    for name,value in summary["variants"].items():
        print(json.dumps({"variant":name,"covered_events":value["event"]["covered_events"],
            "events":value["event"]["events"],"own_raw_hold_mse":value["own_withheld"]["raw_hold"]["mse"],
            "common_raw_hold_mse":value["common_withheld"]["raw_hold"]["mse"]}),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--output",type=Path,default=ROOT/"runs/perception-controller-ablation")
    args=parser.parse_args();output=args.output.resolve()
    if output.exists(): parser.error("Output exists. Inspect its live process/status; never duplicate a running experiment.")
    output.mkdir(parents=True)
    transcript=Transcript(sys.stdout,output/"run.log");original=sys.stdout;sys.stdout=transcript
    try: run(output)
    except BaseException as error:
        write_json(output/"status.json",{"state":"failed","pid":os.getpid(),"error":str(error),"updated_at":datetime.now(timezone.utc).isoformat()})
        traceback.print_exc(file=sys.stdout);raise
    finally: sys.stdout=original;transcript.flush();transcript.file.close()


if __name__=="__main__": main()
