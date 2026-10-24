from dataclasses import replace
from types import SimpleNamespace
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from photon.adaptive import AdaptivePolicy, ControllerConfig, controller_variant
from photon.data import SequenceMetadata
from photon.development import (aggregate_errors, evaluate_development, event_coverage, image_error,
                                load_closed_run, record_development_run, select_variant)
from photon.gaussian import Gaussian, render_gaussians
from photon.oracle import ReplayOracle
from photon.policy import ScheduledPolicy
from photon.replay import RunRecord
from photon.schemas import ObservedFrame
from photon.tracking import Track


def fixture(total=13):
    frames = [render_gaussians((25, 25), [Gaussian(np.array([12., 8.+t/3]), np.eye(2)*4, 0.8)], truncate=8)
              for t in range(total)]
    reads = []
    sequence = SimpleNamespace(metadata=SequenceMetadata("fixture", "01", total, (25, 25), "float32",
                               source="synthetic", voxel_size_xyz_um=(1., 1.)),
                               fingerprint="controlled", provenance={}, read=lambda t: (reads.append(t) or frames[t]))
    return sequence, frames, reads


@pytest.mark.parametrize("variant", ["paced", "robust", "paced_robust"])
def test_refined_presets_keep_causal_traces_and_exact_budget(tmp_path, variant):
    sequence, frames, reads = fixture()
    config = controller_variant(variant, min_gap=1, max_gap=5)
    a = record_development_run(sequence, AdaptivePolicy(config=config), 4, 42, variant, tmp_path/"a")
    assert reads == list(a.record.acquired_indices)
    for t in set(range(len(frames)))-set(a.record.acquired_indices):
        frames[t] = np.random.default_rng(t).uniform(0, 1, frames[t].shape).astype(np.float32)
    reads.clear()
    b = record_development_run(sequence, AdaptivePolicy(config=config), 4, 42, variant, tmp_path/"b")
    assert a.record.decisions == b.record.decisions
    assert reads == list(b.record.acquired_indices)
    for t in a.forecasts:
        np.testing.assert_array_equal(render_gaussians(sequence.metadata.shape, a.forecasts[t]),
                                      render_gaussians(sequence.metadata.shape, b.forecasts[t]))
    for row in a.record.decisions:
        if row["decision"] == "ACQUIRE" and row["pacing_override_for_feasibility"]:
            assert not row["can_skip"]
        elif row["decision"] == "ACQUIRE":
            assert row["remaining_budget_after"] >= 4-row["pacing_allowance"]


def test_pacing_preserves_budget_at_extremes_and_yields_to_hard_constraints():
    overridden = False
    for total in (1, 2, 8, 17):
        for budget in range(1, total+1):
            for minimum, maximum in ((1, 1), (1, 5), (2, 5)):
                for threshold in (0.001, 1e6):
                    p = AdaptivePolicy("image_change", config=ControllerConfig(min_gap=minimum, max_gap=maximum,
                                       pacing_lead=0, threshold=threshold))
                    sequence, frames, _ = fixture(total)
                    try:
                        p.reset(sequence.metadata, budget, 0)
                    except ValueError as exc:
                        assert "infeasible" in str(exc)
                        continue
                    history = []
                    for t, pixels in enumerate(frames):
                        if p.decide(t, tuple(history)):
                            overridden |= p.last_decision["pacing_override_for_feasibility"]
                            if p.last_decision["pacing_override_for_feasibility"]:
                                assert not p.last_decision["can_skip"]
                            frame = ObservedFrame(t, pixels, "synthetic")
                            p.observe(frame)
                            history.append(frame)
                    assert len(history) == budget
                    assert total-1-history[-1].index <= maximum
    assert overridden


def test_robust_aggregation_dilutes_single_elongation_and_high_speed_tail(monkeypatch):
    sequence, frames, _ = fixture()
    scores = {}
    for mode in ("legacy", "robust"):
        p = AdaptivePolicy(config=ControllerConfig(feature_aggregation=mode))
        p.reset(sequence.metadata, 4, 0)
        tracks = {}
        for i in range(8):
            g = Gaussian(np.array([10., 10.]), np.diag([1., 16.]) if i == 7 else np.eye(2)*4, 1)
            tracks[i] = Track(i, g, np.array([20. if i >= 5 else 1., 0.]), 0, 2)
        p.model.tracks = tracks
        p.model.observation_log = [{"events": []}]
        monkeypatch.setattr(p.model, "observe", lambda frame: None)
        assert p.decide(0, ())
        p.observe(ObservedFrame(0, frames[0], "synthetic"))
        scores[mode] = (p.morphology_hint, p.speed_um_per_frame)
    assert scores["legacy"] == (1., 20.)
    assert scores["robust"] == (0.125, 1.)
    for kwargs in ({"pacing_lead": True}, {"pacing_lead": -1}, {"feature_aggregation": "unknown"}):
        with pytest.raises(ValueError):
            ControllerConfig(**kwargs)


def test_event_coverage_counts_simultaneous_events_and_boundaries_without_fabrication():
    annotation = {"available": True, "all_requested_frames_have_annotations": True, "division_times": [2, 2, 5, 7]}
    result = event_coverage([0, 3, 6], annotation, 1)
    assert result["covered_events"] == result["events"] == 4 and result["event_coverage"] == 1
    assert event_coverage([0, 3, 6], annotation, 0)["covered_events"] == 0
    assert event_coverage([0], None, 1)["event_coverage"] is None
    assert event_coverage([0], {**annotation, "division_times": []}, 1)["event_coverage"] is None
    with pytest.raises(ValueError):
        event_coverage([0], {**annotation, "all_requested_frames_have_annotations": False}, 1)
    with pytest.raises(ValueError):
        event_coverage([0], annotation, True)


def test_errors_and_foreground_aggregation_match_direct_voxel_computation():
    truth = np.array([[0., 0.2], [0.6, 1.]], dtype=np.float32)
    predicted = np.array([[0.1, 0.3], [0.4, 0.9]], dtype=np.float32)
    row = image_error(predicted, truth, truth > 0.1)
    result = aggregate_errors([row, row])
    error = predicted.astype(float)-truth
    assert result["mse"] == pytest.approx(np.mean(error**2), abs=1e-15)
    assert result["mae"] == pytest.approx(np.mean(abs(error)), abs=1e-15)
    assert result["foreground_mse"] == pytest.approx(np.mean(error[truth > 0.1]**2), abs=1e-15)
    assert result["voxel_count"] == 8 and result["foreground_voxel_count"] == 6
    assert aggregate_errors([])["mse"] is None


def test_every_oracle_must_close_before_truth_or_annotation_access(tmp_path):
    sequence, _, reads = fixture()
    a = record_development_run(sequence, ScheduledPolicy("fixed_interval"), 4, 42, "fixed", tmp_path/"fixed")
    open_oracle = ReplayOracle(sequence, 4)
    b = replace(a, label="open", oracle=open_oracle)
    reads.clear()
    with pytest.raises(ValueError, match="completed"):
        evaluate_development([a, b], annotation_path=tmp_path/"invalid_missing.xml")
    assert not reads
    with pytest.raises(ValueError, match="completed"):
        open_oracle.read_evaluation_after_run(RunRecord("test", 0, 4, (), ()), 2)
    assert not reads


def test_saved_scenes_recompute_same_metrics_and_never_rerun_policy(tmp_path):
    sequence, _, reads = fixture()
    a = record_development_run(sequence, ScheduledPolicy("fixed_interval"), 4, 42, "fixed", tmp_path/"fixed")
    b = record_development_run(sequence, AdaptivePolicy(config=controller_variant("paced_robust", min_gap=1, max_gap=5)),
                               4, 42, "refined", tmp_path/"refined")
    assert set(a.forecasts) == set(range(13))-set(a.record.acquired_indices)
    reads.clear()
    summary, rows = evaluate_development([a, b])
    assert reads == [0, *range(13)]
    assert summary["variants"]["fixed"]["event"]["event_coverage"] is None
    common = set(a.forecasts) & set(b.forecasts)
    assert summary["common_withheld_indices"] == sorted(common)
    saved = [load_closed_run(sequence, tmp_path/name) for name in ("fixed", "refined")]
    assert evaluate_development(saved) == (summary, rows)
    for result in summary["variants"].values():
        assert result["common_withheld"]["raw_hold"]["frames"] == len(common)


def test_predeclared_selection_rejects_tradeoff_or_missing_labels():
    def result(coverage, mse):
        return {"event": {"event_coverage": coverage}, "common_withheld": {"raw_hold": {"mse": mse}}}
    variants = {"original": result(.5, .1), "paced": result(.6, .09),
                "robust": result(.9, .11), "paced_robust": result(.7, .08)}
    assert select_variant({"variants": variants}) == "paced_robust"
    variants["original"] = result(None, .1)
    assert select_variant({"variants": variants}) == "original"


def test_refined_default_keeps_response_to_observed_presplit_cue():
    from test_adaptive import clip, drive, policy
    config = controller_variant("paced_robust", min_gap=2, max_gap=10, uncertainty_weight=0, motion_weight=0,
                                event_weight=1, gap_weight=0.4, threshold=0.35)
    stable, _ = drive(policy(config), clip(40), 10)
    event, _ = drive(policy(config), clip(40, elongate=True), 10)
    assert sum(8 < t <= 16 for t in event) > sum(8 < t <= 16 for t in stable)
    assert AdaptivePolicy().config == controller_variant("paced_robust")
    assert AdaptivePolicy("image_change").config == ControllerConfig()


def test_cli_defaults_to_selected_variant_and_preserves_original_preset(tmp_path):
    import tifffile
    sequence, frames, _ = fixture()
    folder = tmp_path/"sequence"
    folder.mkdir()
    for t, pixels in enumerate(frames):
        tifffile.imwrite(folder/f"t{t:03d}.tif", (pixels*4095).astype(np.uint16))
    root = Path(__file__).resolve().parents[3]
    for variant in ("default", "original"):
        args = [sys.executable, str(root/"scripts/run_experiment.py"), "--sequence", str(folder),
                "--dataset-id", "fixture", "--source", "synthetic", "--policy", "photon_adaptive",
                "--budget", "4", "--min-gap", "1", "--max-gap", "5", "--output", str(tmp_path/variant)]
        if variant == "original":
            args += ["--controller-variant", variant]
        completed = subprocess.run(args, capture_output=True, text=True)
        assert completed.returncode == 0, completed.stderr
        result = json.loads((tmp_path/variant/"photon_adaptive/config.json").read_text())
        assert result["controller_config"]["pacing_lead"] == (2 if variant == "default" else None)
        assert result["controller_config"]["feature_aggregation"] == ("robust" if variant == "default" else "legacy")
        assert len(result["acquired_indices"]) == 4
