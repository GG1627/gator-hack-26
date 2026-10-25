"""Verify registered inputs/closed ledgers; optionally rerender from saved scenes."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from photon.annotations import audit_mamut
from photon.data import load_sequence
from photon.development import aggregate_errors, evaluate_development, event_coverage, load_closed_run
from scripts.run_perception_ablation import check_phase5, digest, pairwise_scores, verify_accounting, write_json

ANNOTATIONS=ROOT/"data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1/tracks/tracks_mamut.xml"


def register_labels(output):
    """Supplementary label provenance while acquisition is active; no label parsing."""
    status=json.loads((output/"status.json").read_text())
    if status.get("state")!="running" or status.get("stage")!="acquisition":
        raise ValueError("Supplementary label registration requires the acquisition stage")
    path=output/"label-registration.json"
    if path.exists(): raise ValueError("Label registration already exists")
    prior=ROOT/"runs/perception-count-audit/summary.json"
    prior_hashes=json.loads(prior.read_text())["source_sha256"]
    expected=next(value for key,value in prior_hashes.items() if Path(key).resolve()==ANNOTATIONS)
    actual=digest(ANNOTATIONS)
    if actual!=expected: raise ValueError("Annotations changed since the earlier development count audit")
    write_json(path,{"registered_at":datetime.now(timezone.utc).isoformat(),"experiment_status_at_registration":status,
        "annotation_sha256":actual,"prior_audit":str(prior.relative_to(ROOT)),"prior_audit_sha256":digest(prior),
        "scope":"supplement before this experiment's offline evaluation; annotations hashed, not parsed",
        "note":"Original protocol did not include the s1 XML byte hash; its source path was fixed in the runner."})
    print("Supplementary annotation hash registered during acquisition; matches earlier pre-experiment audit.",flush=True)


def verify_registry(output):
    registration=json.loads((output/"registration.json").read_text())
    if digest(output/"protocol.json")!=registration["protocol_sha256"]:
        raise ValueError("Protocol hash mismatch")
    if digest(output/"source.zip")!=registration["source_zip_sha256"]:
        raise ValueError("Source archive hash mismatch")
    protocol=json.loads((output/"protocol.json").read_text())
    import hashlib
    with zipfile.ZipFile(output/"source.zip") as archive:
        if archive.testzip() is not None: raise ValueError("Source archive CRC failure")
        for path,expected in protocol["source_sha256"].items():
            if digest(ROOT/path)!=expected or hashlib.sha256(archive.read(path)).hexdigest()!=expected:
                raise ValueError(f"Registered source differs: {path}")
    return protocol


def verify(output,full=False):
    status=json.loads((output/"status.json").read_text())
    if status.get("state")!="complete": raise ValueError("Acquisition and first-pass scoring must finish before verification")
    protocol=verify_registry(output);check_phase5()
    label_registration=json.loads((output/"label-registration.json").read_text())
    if digest(ANNOTATIONS)!=label_registration["annotation_sha256"]:
        raise ValueError("Annotation source differs from the acquisition-stage supplement")
    summary=json.loads((output/"summary.json").read_text())
    if summary["protocol_sha256"]!=digest(output/"protocol.json"): raise ValueError("Summary protocol differs")
    rows={};artifacts={}
    for name in protocol["names"]:
        folder=output/name;config=json.loads((folder/"config.json").read_text())
        trace=[json.loads(line) for line in (folder/"decisions.jsonl").read_text().splitlines()]
        if any(config[key]!=protocol[key] for key in ("budget","seed","frame_count")):
            raise ValueError("Run configuration differs from registered budget/seed/window")
        if config["experimental_source_sha256"]!=protocol["source_sha256"] or config["photon_code_sha256"]!=protocol["base_science_sha256"]:
            raise ValueError("Run implementation provenance differs")
        if name!="fixed" and config["controller_config"]!=protocol["controller"]:
            raise ValueError("Controller settings changed between detector variants")
        if config["sequence_sha256"]!=protocol["sequence_sha256"] or config["experiment_protocol_sha256"]!=summary["protocol_sha256"]:
            raise ValueError("Run source or protocol differs")
        if len(trace)!=protocol["frame_count"] or [row["t"] for row in trace]!=list(range(protocol["frame_count"])):
            raise ValueError("Incomplete source clock")
        captured=[];remaining=protocol["budget"]
        for row in trace:
            if row["decision"] not in ("ACQUIRE","SKIP") or row["remaining_budget_before"]!=remaining:
                raise ValueError("Invalid action or budget-before ledger")
            if row["decision"]=="ACQUIRE": captured.append(row["t"]);remaining-=1
            if not captured or row["last_acquired_index"]!=captured[-1] or row["remaining_budget_after"]!=remaining:
                raise ValueError("Invalid causal last-observation or budget-after ledger")
        if remaining!=0 or captured!=config["acquired_indices"] or captured!=summary["variants"][name]["acquired_indices"]:
            raise ValueError("Closed acquisition ledgers disagree")
        if name=="fixed":
            expected=[k*(protocol["frame_count"]-1)//(protocol["budget"]-1) for k in range(protocol["budget"])]
            if captured!=expected: raise ValueError("Fixed schedule differs")
        else:
            gaps=[b-a for a,b in zip(captured,captured[1:])]
            if min(gaps)<protocol["controller"]["min_gap"] or max(gaps)>protocol["controller"]["max_gap"] or protocol["frame_count"]-1-captured[-1]>protocol["controller"]["max_gap"]:
                raise ValueError("Adaptive gap constraints violated")
        rows[name]=[json.loads(line) for line in (folder/"evaluation.jsonl").read_text().splitlines()]
        if json.loads((folder/"metrics.json").read_text())!=summary["variants"][name]: raise ValueError("Run metrics differ")
        for path in folder.iterdir():
            if path.is_file(): artifacts[str(path.relative_to(output))]=digest(path)
    verify_accounting(summary,rows,protocol["frame_count"],protocol["budget"])
    common=sorted(set.intersection(*(set(row["t"] for row in values) for values in rows.values())))
    if common!=summary["common_withheld_indices"] or pairwise_scores(rows)!=summary["pairwise_common"]:
        raise ValueError("Common or pairwise target accounting differs")
    annotation=audit_mamut(ANNOTATIONS,protocol["frame_count"])
    for name,values in rows.items():
        metrics=summary["variants"][name]
        if any(row["common_target"]!=(row["t"] in common) for row in values):
            raise ValueError("Per-frame common-target flag differs")
        if event_coverage(metrics["acquired_indices"],annotation,protocol["event_tolerance_frames"])!=metrics["event"]:
            raise ValueError("Annotated event coverage differs")
        for estimator,expected in metrics["common_withheld"].items():
            if aggregate_errors([row["errors"][estimator] for row in values if row["t"] in common])!=expected:
                raise ValueError("Three-way common score differs")
    result={"verified":True,"scope":"source/closed-ledger/target/event/scalar verification",
        "independent_full_rerender":False,"protocol_sha256":digest(output/"protocol.json"),
        "annotation_sha256":digest(ANNOTATIONS),"closed_artifact_sha256":artifacts,
        "summary_sha256":digest(output/"summary.json"),"verified_at":datetime.now(timezone.utc).isoformat()}
    if full:
        sequence=load_sequence(ANNOTATIONS.parent.parent,dataset_id="MSKCC-CONFOCAL")
        runs=[load_closed_run(sequence,output/name) for name in protocol["names"]]
        recomputed,recomputed_rows=evaluate_development(runs,annotation_path=ANNOTATIONS,
            event_tolerance=protocol["event_tolerance_frames"],foreground_threshold=protocol["foreground_threshold"])
        if any(summary[key]!=value for key,value in recomputed.items()) or recomputed_rows!=rows:
            raise ValueError("Full source/geometry recomputation differs")
        result["independent_full_rerender"]=True
    write_json(output/("recomputation.json" if full else "verification.json"),result)
    print(json.dumps(result|{"closed_artifact_sha256":f"{len(artifacts)} sealed files"},indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=ROOT/"runs/perception-controller-ablation")
    parser.add_argument("--register-labels",action="store_true")
    parser.add_argument("--full-recompute",action="store_true")
    args=parser.parse_args()
    if args.register_labels: register_labels(args.output.resolve())
    else: verify(args.output.resolve(),args.full_recompute)


if __name__=="__main__": main()
