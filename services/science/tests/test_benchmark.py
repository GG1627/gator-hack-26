from copy import deepcopy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import xml.etree.ElementTree as ET

import numpy as np
import pytest

from photon.benchmark import (BUDGETS, METHODS, protocol_definition, make_policy,
                              summarize_group, validate_trace, verify_statistics)
from photon.data import SequenceMetadata
from photon.development import evaluate_development, load_closed_run, record_development_run


def fixture():
    frames = [np.full((8, 8), t % 17, dtype=np.uint16) for t in range(270)]
    reads = []
    seq = SimpleNamespace(metadata=SequenceMetadata("controlled", "fixture", 270, (8,8), "uint16",
                          source="synthetic", voxel_size_xyz_um=(1.,1.)), fingerprint="controlled", provenance={},
                          read=lambda t: (reads.append(t) or frames[t]))
    return seq, frames, reads


@pytest.fixture(scope="module")
def completed(tmp_path_factory):
    root = tmp_path_factory.mktemp("benchmark")
    seq, frames, reads = fixture()
    runs, configs, traces = [], {}, {}
    for method in METHODS:
        policy, seed = make_policy(method)
        reads.clear()
        run = record_development_run(seq, policy, 27, seed, method, root/method, scope="controlled fixture")
        assert reads == list(run.record.acquired_indices)  # no truth, annotations or extra reads
        runs.append(run)
        configs[method] = json.loads((root/method/"config.json").read_text())
        traces[method] = run.record.decisions
    protocol = protocol_definition()
    summary, rows = evaluate_development(runs)
    summary = summarize_group(summary, rows, runs, None, protocol)
    return root, seq, frames, runs, configs, traces, protocol, summary, rows


def test_frozen_budgets_feasible_and_seeded_baselines_are_exact():
    metadata = fixture()[0].metadata
    assert protocol_definition() == protocol_definition()
    for budget in BUDGETS:
        indices = {}
        for method in METHODS:
            p, seed = make_policy(method)
            p.reset(metadata, budget, seed)  # adaptive feasibility checked before images
            if method.startswith("random_") or method == "fixed":
                indices[method] = p.indices
                q, seed = make_policy(method)
                q.reset(metadata, budget, seed)
                assert q.indices == p.indices and len(p.indices) == budget and 0 in p.indices
        assert len({tuple(sorted(indices[m])) for m in indices if m.startswith("random_")}) == 3
    with pytest.raises(ValueError, match="infeasible"):
        make_policy("photon")[0].reset(metadata, 2, 42)


def test_missing_annotations_pairwise_sets_and_independent_accounting(completed):
    _, _, _, runs, configs, traces, protocol, summary, rows = completed
    assert verify_statistics(summary, rows, configs, traces, None, protocol)
    assert all(row["photon_minus_fixed_raw_hold_mse"] > 0 for row in summary["failure_analysis"]["largest_raw_hold_losses"])
    assert all(row["photon_minus_fixed_raw_hold_mse"] < 0 for row in summary["failure_analysis"]["largest_raw_hold_wins"])
    for name in METHODS:
        result = summary["variants"][name]
        assert result["event"]["event_coverage"] is None and result["event"]["reason"]
        assert result["acquisitions"] == 27
        expected = sorted(set(runs[0].forecasts) & set(next(r for r in runs if r.label == name).forecasts))
        assert result["matched_fixed_indices"] == expected
        assert result["matched_fixed"]["raw_hold"]["frames"] == len(expected)
        assert result["relative_exposure_proxy"] == 0.1


def test_source_scene_recomputation_is_exact_without_policy_calls(completed, monkeypatch):
    root, seq, _, runs, _, _, protocol, summary, rows = completed
    def forbidden(*args, **kwargs):
        raise AssertionError("Policy must never execute during evaluation")
    monkeypatch.setattr("photon.policy.ScheduledPolicy.decide", forbidden)
    monkeypatch.setattr("photon.adaptive.AdaptivePolicy.decide", forbidden)
    loaded = [load_closed_run(seq, root/name) for name in METHODS]
    again, again_rows = evaluate_development(loaded)
    assert summarize_group(again, again_rows, loaded, None, protocol) == summary
    assert again_rows == rows


def test_independent_verifier_rejects_tampering_and_budget_unfairness(completed):
    _, _, _, _, configs, traces, protocol, summary, rows = completed
    bad = deepcopy(summary)
    bad["variants"]["photon"]["matched_fixed"]["raw_hold"]["mse"] += 0.01
    with pytest.raises(ValueError, match="accounting"):
        verify_statistics(bad, rows, configs, traces, None, protocol)
    bad_configs = deepcopy(configs)
    bad_configs["random_7"]["budget"] += 1
    with pytest.raises(ValueError):
        verify_statistics(summary, rows, bad_configs, traces, None, protocol)
    bad_trace = deepcopy(list(traces["photon"]))
    bad_trace[1]["remaining_budget_after"] -= 1
    with pytest.raises(ValueError, match="Budget/history"):
        validate_trace(configs["photon"], bad_trace, 270)
    bad_rows = deepcopy(rows)
    bad_rows["photon"][0]["t"] = 0
    with pytest.raises(ValueError, match="targets"):
        verify_statistics(summary, bad_rows, configs, traces, None, protocol)


def test_future_pixel_perturbation_leaves_benchmark_trajectory_unchanged(tmp_path):
    seq, frames, reads = fixture()
    p, seed = make_policy("photon")
    a = record_development_run(seq, p, 27, seed, "photon", tmp_path/"a")
    for t in a.forecasts:
        frames[t] = np.random.default_rng(t).integers(0, 65535, (8,8), dtype=np.uint16)
    reads.clear()
    p, seed = make_policy("photon")
    b = record_development_run(seq, p, 27, seed, "photon", tmp_path/"b")
    assert a.record == b.record
    assert reads == list(a.record.acquired_indices)
    assert (tmp_path/"a/forecasts.npz").read_bytes() == (tmp_path/"b/forecasts.npz").read_bytes()


def test_annotation_failures_have_independent_expected_event_identities(completed):
    _, _, _, runs, _, _, protocol, summary, rows = completed
    times = [1, 1, 7, 13, 100, 269]
    events = [{"mother_id": i, "mother_frame": t-1, "daughter_frame": t, "daughter_ids": [i+10,i+20]} for i,t in enumerate(times)]
    annotation = {"available": True, "all_requested_frames_have_annotations": True, "division_times": times, "events": events}
    from photon.development import event_coverage
    result = deepcopy(summary)
    for run in runs:
        result["variants"][run.label]["event"] = event_coverage(run.record.acquired_indices, annotation, 1)
    result = summarize_group(result, rows, runs, annotation, protocol)
    for key, a, b in (("fixed_only_events", True, False), ("photon_only_events", False, True), ("missed_by_both_events", False, False)):
        expected = [e for e in events if (min(abs(e["daughter_frame"]-t) for t in runs[0].record.acquired_indices)<=1) == a
                    and (min(abs(e["daughter_frame"]-t) for t in runs[1].record.acquired_indices)<=1) == b]
        assert result["failure_analysis"][key] == expected


def test_frozen_registration_rejects_modified_implementation(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location("phase5_runner", root/"scripts/run_phase5.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    protocol_path = tmp_path/"protocol.json"
    protocol_path.write_text(json.dumps({"implementation_hashes": {"changed": "old"}, "science_code_sha256": "old"}))
    (tmp_path/"registration.json").write_text(json.dumps({"protocol_sha256": module.file_hash(protocol_path)}))
    with pytest.raises(ValueError, match="implementation changed"):
        module.check_registration(tmp_path)
    protocol_path.write_text("{}")
    with pytest.raises(ValueError, match="protocol changed"):
        module.check_registration(tmp_path)


def test_all_staged_gates_and_report_on_controlled_matrix(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location("phase5_stages", root/"scripts/run_phase5.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sequences, evidence = {}, {}
    for sid in module.SEQUENCES:
        folder = tmp_path/"data"/sid/"tracks"
        folder.mkdir(parents=True)
        xml = ET.Element("TrackMate")
        model = ET.SubElement(xml, "Model")
        spots = ET.SubElement(model, "AllSpots")
        for t in range(270):
            group = ET.SubElement(spots, "SpotsInFrame")
            ET.SubElement(group, "Spot", ID=str(t), FRAME=str(t))
        ET.SubElement(spots.find("SpotsInFrame"), "Spot", ID="999", FRAME="1")
        track = ET.SubElement(ET.SubElement(model, "AllTracks"), "Track")
        ET.SubElement(track, "Edge", SPOT_SOURCE_ID="0", SPOT_TARGET_ID="1")
        ET.SubElement(track, "Edge", SPOT_SOURCE_ID="0", SPOT_TARGET_ID="999")
        ET.ElementTree(xml).write(folder/"tracks_mamut.xml")
        sequences[sid] = fixture()
        evidence[sid] = {"sequence_sha256": "controlled", "annotation_sha256": module.file_hash(folder/"tracks_mamut.xml")}
    args = SimpleNamespace(output=tmp_path/"runs", data=tmp_path/"data", validation=tmp_path/"validation.json", recompute=False)
    module.write_json(args.validation, {"sequences": evidence})
    module.freeze(args)
    monkeypatch.setattr(module, "load_checked_sequence", lambda data, protocol, sid: sequences[sid][0])
    module.acquire(args)
    assert json.loads((args.output/"all-trajectories-closed.json").read_text())["closed_runs"] == 36
    for _, _, reads in sequences.values():
        assert len(reads) == sum(BUDGETS)*len(METHODS)  # every read paid for
    module.evaluate(args)
    module.verify(args)
    args.recompute = True
    module.evaluate(args)
    assert json.loads((args.output/"recomputation.json").read_text())["all_source_metrics_exact"]
    report_spec = importlib.util.spec_from_file_location("phase5_report", root/"scripts/report_phase5.py")
    report = importlib.util.module_from_spec(report_spec)
    report_spec.loader.exec_module(report)
    report.build_report(args.output)
    assert json.loads((args.output/"report-verification.json").read_text())["cards"] == 36
    assert (args.output/"comparison.png").stat().st_size > 0
    missing = tmp_path/"missing-annotation-report"
    missing.mkdir()
    no_labels = json.loads((args.output/"benchmark.json").read_text())
    for group in no_labels["groups"].values():
        group["comparison"]["photon_minus_fixed_event_coverage"] = None
        for result in group["variants"].values():
            result["event"] = {"event_coverage": None, "reason": "No annotations available"}
    module.write_json(missing/"benchmark.json", no_labels)
    report.build_report(missing)
    assert "not available" in (missing/"report.md").read_text()
    assert all(card["event"]["event_coverage"] is None for card in json.loads((missing/"cards.json").read_text())["cards"])
    # Closed acquisition artifacts remain protected even after metrics exist.
    config_path = args.output/module.SEQUENCES[0]/"b27/fixed/config.json"
    config_path.write_text(config_path.read_text()+" ")
    with pytest.raises(ValueError, match="artifact changed"):
        module.verify(args)
