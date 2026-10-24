"""Validate, freeze, acquire and evaluate PHOTON's held-out matrix, in order."""
import argparse
from dataclasses import asdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time
import zipfile
import zlib

from photon.annotations import audit_mamut
from photon.benchmark import (BUDGETS, METHODS, SEQUENCES, SCOPE, file_hash, make_policy,
                              protocol_definition, summarize_group, validate_trace,
                              verify_statistics, write_json)
from photon.data import load_sequence
from photon.development import evaluate_development, load_closed_run, record_development_run, science_hash


ROOT = Path(__file__).resolve().parents[1]


def files_to_freeze():
    return sorted([*ROOT.glob("services/science/photon/*.py"), *ROOT.glob("services/science/tests/*.py"), ROOT/"scripts/run_phase5.py",
                   ROOT/"scripts/report_phase5.py", ROOT/"scripts/inspect_phase5_failures.py", ROOT/"docs/phase5-protocol.md",
                   ROOT/"scripts/download_mskcc.py", ROOT/"scripts/audit_mskcc_dataset.py",
                   ROOT/"PHOTON_SPEC.md", ROOT/"AGENTS.md",
                   ROOT/"requirements-dev.lock", ROOT/"pyproject.toml"])


def implementation_hashes():
    return {str(path.relative_to(ROOT)).replace("\\", "/"): file_hash(path) for path in files_to_freeze()}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_data(data, output):
    # Integrity/metadata QA only: no event outcomes or pixel-derived tuning.
    inventory = {row["name"]: row for row in read_json(ROOT/"runs/mskcc-audit/inventory.json")}
    evidence = {}
    for sid in SEQUENCES:
        folder = data/sid
        manifest = read_json(folder/"download-manifest.json")
        if manifest["selected_frame_count"] != 270 or manifest["source_frame_indices"] != [0, 269]:
            raise ValueError("Incomplete window manifest")
        sequence = load_sequence(folder, dataset_id="MSKCC-CONFOCAL")
        image_bytes = 0
        for path in [*sequence.paths, folder/"tracks/tracks.txt", folder/"tracks/tracks_mamut.xml"]:
            member = "mskcc-confocal/"+str(path.relative_to(data)).replace("\\", "/")
            row = inventory[member]
            payload = path.read_bytes()
            if len(payload) != row["bytes"] or f"{zlib.crc32(payload):08x}" != row["crc32"]:
                raise ValueError(f"Source ZIP CRC mismatch: {path}")
            if path.suffix == ".tif":
                image_bytes += len(payload)
        evidence[sid] = {"metadata": asdict(sequence.metadata), "image_bytes": image_bytes,
                         "sequence_sha256": sequence.fingerprint,
                         "annotation_sha256": file_hash(folder/"tracks/tracks_mamut.xml"),
                         "download_manifest_sha256": file_hash(folder/"download-manifest.json"),
                         "crc_verified_images": 270, "all_volumes_decoded": True,
                         "full_archive_md5_verified": False}
        print(f"Validated {sid}: 270 decoded volumes, CRC/source hashes; no scoring", flush=True)
    write_json(output, {"validated_at": datetime.now().astimezone().isoformat(), "sequences": evidence})


def freeze(args):
    if args.output.exists():
        raise ValueError("Freeze output exists; never overwrite a registered protocol")
    data = read_json(args.validation)
    if tuple(data["sequences"]) != SEQUENCES:
        raise ValueError("Both held-out windows must validate before freezing")
    protocol = {**protocol_definition(), "frozen_at": datetime.now().astimezone().isoformat(),
                "science_code_sha256": science_hash(), "implementation_hashes": implementation_hashes(),
                "data_validation": data, "validation_file_sha256": file_hash(args.validation),
                "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "git_status_at_freeze": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
                "python": platform.python_version(), "platform": platform.platform(), "backend": "cpu"}
    args.output.mkdir(parents=True)
    write_json(args.output/"protocol.json", protocol)
    with zipfile.ZipFile(args.output/"frozen-source.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files_to_freeze():
            archive.write(path, str(path.relative_to(ROOT)))
        archive.write(args.output/"protocol.json", "protocol.json")
    with zipfile.ZipFile(args.output/"frozen-source.zip") as archive:
        if archive.testzip() is not None:
            raise ValueError("Source snapshot CRC failure")
    write_json(args.output/"registration.json", {"protocol_sha256": file_hash(args.output/"protocol.json"),
               "source_snapshot_sha256": file_hash(args.output/"frozen-source.zip"), "outcomes_inspected": False})
    print("Protocol frozen. No held-out outcome has been computed.", flush=True)


def check_registration(output):
    protocol = read_json(output/"protocol.json")
    registration = read_json(output/"registration.json")
    if file_hash(output/"protocol.json") != registration["protocol_sha256"]:
        raise ValueError("Frozen protocol changed")
    if implementation_hashes() != protocol["implementation_hashes"] or science_hash() != protocol["science_code_sha256"]:
        raise ValueError("Frozen implementation changed; do not silently modify held-out evaluation")
    if file_hash(output/"frozen-source.zip") != registration["source_snapshot_sha256"]:
        raise ValueError("Source archive changed")
    return protocol, registration["protocol_sha256"]


def group_folders(output):
    for sid in SEQUENCES:
        for budget in BUDGETS:
            yield sid, budget, output/sid/f"b{budget}"


def load_checked_sequence(data, protocol, sid):
    sequence = load_sequence(data/sid, dataset_id="MSKCC-CONFOCAL")
    if sequence.fingerprint != protocol["data_validation"]["sequences"][sid]["sequence_sha256"]:
        raise ValueError("Source changed since protocol freeze")
    return sequence


def acquire(args):
    protocol, protocol_hash = check_registration(args.output)
    sequences = {sid: load_checked_sequence(args.data, protocol, sid) for sid in SEQUENCES}
    for sid, budget, group in group_folders(args.output):
        sequence = sequences[sid]
        group.mkdir(parents=True, exist_ok=True)
        for method in METHODS:
            folder = group/method
            marker = folder/"closed.json"
            if folder.exists():
                if not marker.exists():
                    raise ValueError(f"Partial run requires inspection; not silently reused: {folder}")
                config = read_json(folder/"config.json")
                if config["protocol_sha256"] != protocol_hash:
                    raise ValueError("Run belongs to another protocol")
                check_closed(folder)
                validate_trace(config, [json.loads(line) for line in (folder/"decisions.jsonl").read_text().splitlines()], 270)
                load_closed_run(sequence, folder)
                print(f"Reusing completed immutable trajectory {folder}", flush=True)
                continue
            policy, seed = make_policy(method)
            start = time.perf_counter()
            run = record_development_run(sequence, policy, budget, seed, method, folder, scope=SCOPE)
            config = read_json(folder/"config.json")
            config.update(protocol_sha256=protocol_hash, budget_semantics=protocol["budget_semantics"],
                          replay_mode="retrospective_source_time_replay",
                          baseline_gap_caveat=protocol["baseline_constraints"])
            # image_change uses a separate common reconstruction model, even though
            # its acquisition policy deliberately has no Gaussian state.
            config["reconstruction_model_version"] = "causal-moment-gaussian-v1"
            config["reconstruction_fit_config"] = protocol["fit_config"]
            config["reconstruction_tracking_config"] = protocol["tracking_config"]
            write_json(folder/"config.json", config)
            validate_trace(config, run.record.decisions, 270)
            write_json(marker, {"closed": True, "elapsed_seconds": time.perf_counter()-start,
                               "files": {path.name: file_hash(path) for path in folder.iterdir() if path.is_file()}})
            del run, policy
    write_json(args.output/"all-trajectories-closed.json", {"closed_runs": len(SEQUENCES)*len(BUDGETS)*len(METHODS),
               "protocol_sha256": protocol_hash, "completed_at": datetime.now().astimezone().isoformat()})
    print("All 36 trajectories closed. Acquisition stage never opened labels or withheld images.", flush=True)


def check_closed(folder):
    closed = read_json(folder/"closed.json")
    if not closed["closed"]:
        raise ValueError("Run is not closed")
    for name, expected in closed["files"].items():
        if file_hash(folder/name) != expected:
            raise ValueError(f"Causal artifact changed after closure: {folder/name}")


def evaluate(args):
    protocol, protocol_hash = check_registration(args.output)
    closure = read_json(args.output/"all-trajectories-closed.json")
    if closure["closed_runs"] != 36 or closure["protocol_sha256"] != protocol_hash:
        raise ValueError("Every matrix trajectory must close before scoring")
    for _, _, group in group_folders(args.output):
        for method in METHODS:
            check_closed(group/method)
    sequences = {sid: load_checked_sequence(args.data, protocol, sid) for sid in SEQUENCES}
    benchmark = {"scope": SCOPE, "protocol_sha256": protocol_hash,
                 "protocol": protocol, "groups": {}}
    for sid, budget, group in group_folders(args.output):
        summary_path = group/"summary.json"
        if summary_path.exists() and not args.recompute:
            print(f"Reusing scored group {sid}/b{budget}; verify checks its ledger", flush=True)
            benchmark["groups"][f"{sid}/b{budget}"] = read_json(summary_path)
            continue
        runs = [load_closed_run(sequences[sid], group/method) for method in METHODS]
        annotation_path = args.data/sid/"tracks/tracks_mamut.xml"
        if file_hash(annotation_path) != protocol["data_validation"]["sequences"][sid]["annotation_sha256"]:
            raise ValueError("Annotation source changed")
        summary, rows = evaluate_development(runs, annotation_path=annotation_path,
                    event_tolerance=protocol["event_tolerance_frames"], foreground_threshold=protocol["foreground_threshold"])
        summary = summarize_group(summary, rows, runs, audit_mamut(annotation_path, 270), protocol)
        if args.recompute:
            if summary != read_json(summary_path):
                raise ValueError(f"Full source recomputation differs: {group}")
            for method in METHODS:
                stored = [json.loads(line) for line in (group/method/"evaluation.jsonl").read_text().splitlines()]
                if rows[method] != stored:
                    raise ValueError(f"Per-frame source recomputation differs: {group/method}")
            write_json(group/"recomputation.json", {"verified": True, "all_source_voxels_and_saved_scenes_recomputed": True,
                       "all_per_frame_statistics_exact": True, "protocol_sha256": protocol_hash})
        else:
            for method in METHODS:
                (group/method/"evaluation.jsonl").write_text("".join(json.dumps(row, allow_nan=False)+"\n" for row in rows[method]), encoding="utf-8")
                write_json(group/method/"metrics.json", summary["variants"][method])
            write_json(summary_path, summary)
        benchmark["groups"][f"{sid}/b{budget}"] = summary
        print(f"Scored {sid}/b{budget}: {summary['comparison']}", flush=True)
    if args.recompute:
        if benchmark != read_json(args.output/"benchmark.json"):
            raise ValueError("Trusted benchmark differs from full recomputation")
        write_json(args.output/"recomputation.json", {"verified": True, "groups": 6, "runs": 36,
                   "all_source_metrics_exact": True, "protocol_sha256": protocol_hash})
    else:
        write_json(args.output/"benchmark.json", benchmark)


def verify(args):
    protocol, protocol_hash = check_registration(args.output)
    benchmark = read_json(args.output/"benchmark.json")
    if benchmark["protocol_sha256"] != protocol_hash or benchmark["protocol"] != protocol:
        raise ValueError("Benchmark protocol mismatch")
    for sid, budget, group in group_folders(args.output):
        summary = read_json(group/"summary.json")
        if summary != benchmark["groups"][f"{sid}/b{budget}"] or summary["budget"] != budget:
            raise ValueError("Trusted benchmark/group mismatch")
        rows, configs, traces = {}, {}, {}
        for method in METHODS:
            folder = group/method
            check_closed(folder)
            configs[method] = read_json(folder/"config.json")
            traces[method] = [json.loads(line) for line in (folder/"decisions.jsonl").read_text().splitlines()]
            rows[method] = [json.loads(line) for line in (folder/"evaluation.jsonl").read_text().splitlines()]
            if read_json(folder/"metrics.json") != summary["variants"][method]:
                raise ValueError("Per-run metrics disagree with benchmark")
            expected_timeline = "".join("|" if t in configs[method]["acquired_indices"] else "." for t in range(270))+"\n"
            if (folder/"timeline.txt").read_text() != expected_timeline:
                raise ValueError("Timeline mismatch")
        annotation_path = args.data/sid/"tracks/tracks_mamut.xml"
        if file_hash(annotation_path) != protocol["data_validation"]["sequences"][sid]["annotation_sha256"]:
            raise ValueError("Annotation source changed")
        verify_statistics(summary, rows, configs, traces, audit_mamut(annotation_path, 270), protocol)
    write_json(args.output/"verification.json", {"verified": True, "groups": 6, "runs": 36,
               "exact_budget_event_target_and_metric_accounting": True, "all_closed_artifact_hashes_match": True,
               "protocol_sha256": protocol_hash, "note": "Scalar ledger verification; see recomputation.json for full source rerender evidence"})
    print("All 36 run ledgers, target sets, event counts, aggregates and exports verified.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("validate-data", "freeze", "acquire", "evaluate", "verify"))
    parser.add_argument("--data", type=Path, default=ROOT/"data/mskcc-audit/mskcc-confocal")
    parser.add_argument("--output", type=Path, default=ROOT/"runs/phase5")
    parser.add_argument("--validation", type=Path, default=ROOT/"runs/phase5-data-validation.json")
    parser.add_argument("--recompute", action="store_true", help="Evaluate saved scenes against every source target again, require exact metrics")
    args = parser.parse_args()
    if args.stage == "validate-data":
        validate_data(args.data, args.validation)
    else:
        {"freeze": freeze, "acquire": acquire, "evaluate": evaluate, "verify": verify}[args.stage](args)


if __name__ == "__main__":
    main()
