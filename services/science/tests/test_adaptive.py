from itertools import combinations
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np
import pytest

from photon.adaptive import AdaptivePolicy, ControllerConfig, feasible_completion
from photon.data import SequenceMetadata
from photon.gaussian import Gaussian, GaussianFitConfig, render_gaussians
from photon.replay import run_replay
from photon.policy import ScheduledPolicy
from photon.schemas import ObservedFrame
from photon.tracking import GaussianSceneModel, TrackingConfig


def metadata(total, shape=(41, 41)):
    return SequenceMetadata("controlled-fixture", "01", total, shape, "float32", source="synthetic",
                            voxel_size_xyz_um=(1.0,) * len(shape))


def policy(config=ControllerConfig(min_gap=1, max_gap=10), **kwargs):
    return AdaptivePolicy(config=config, fit_config=GaussianFitConfig(min_signal=1e-4, noise_multiplier=0,
                          smoothing_um=0, min_voxels=3), **kwargs)


def clip(total, *, elongate=False):
    result = []
    for t in range(total):
        # A deliberately forecastable shape cue precedes a scripted split.
        if elongate and 8 <= t <= 16:
            objects = [Gaussian(np.array([20., 20.]), np.diag([2., 24.]), 0.8)]
        elif elongate and t > 16:
            objects = [Gaussian(np.array([20., 15.]), np.eye(2)*3, 0.8),
                       Gaussian(np.array([20., 25.]), np.eye(2)*3, 0.8)]
        else:
            objects = [Gaussian(np.array([20., 20.]), np.eye(2)*4, 0.8)]
        result.append(render_gaussians((41, 41), objects, truncate=8))
    return result


def drive(p, frames, budget):
    p.reset(metadata(len(frames), frames[0].shape), budget, 42)
    history, trace = [], []
    for t in range(len(frames)):
        acquire = p.decide(t, tuple(history))
        trace.append({**p.last_decision, "t": t, "acquire": acquire})
        if acquire:
            frame = ObservedFrame(t, frames[t], "synthetic")
            p.observe(frame)
            history.append(frame)
    return [frame.index for frame in history], trace


def test_feasibility_matches_exhaustive_integer_schedule_search():
    # Independent enumeration checks the closed-form planner, including the tail.
    for total in range(1, 9):
        for minimum in range(1, 4):
            for maximum in range(minimum, 5):
                for last in range(total):
                    for earliest in range(last+1, total+1):
                        for remaining in range(total+1):
                            expected = any(
                                all(minimum <= b-a <= maximum for a, b in zip((last, *tail), tail))
                                and total-1-(tail[-1] if tail else last) <= maximum
                                for tail in combinations(range(earliest, total), remaining))
                            assert feasible_completion(total, last, remaining, earliest, minimum, maximum) == expected


def test_controller_never_uses_rendered_predictions_for_decisions(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Rendering is outside the acquisition decision path")
    monkeypatch.setattr("photon.gpu.render_gaussian_batch",forbidden)
    monkeypatch.setattr(GaussianSceneModel,"predict",forbidden)
    indices,trace = drive(policy(),clip(40),10)
    assert len(indices)==10 and len(trace)==40


@pytest.mark.parametrize("threshold", [0.001, 1.0, 1e6])
def test_all_feasible_boundary_budgets_and_guardrails(threshold):
    for total in (1, 2, 7, 17):
        frames = [np.zeros((5, 5), dtype=np.float32)] * total
        for minimum, maximum in ((1, 1), (1, 5), (2, 5), (3, 20)):
            for budget in range(1, total+1):
                p = AdaptivePolicy("image_change", config=ControllerConfig(min_gap=minimum, max_gap=maximum, threshold=threshold))
                if not feasible_completion(total, 0, budget-1, 1, minimum, maximum):
                    with pytest.raises(ValueError, match="infeasible"):
                        drive(p, frames, budget)
                    continue
                indices, trace = drive(p, frames, budget)
                assert len(indices) == budget and indices[0] == 0
                assert all(minimum <= b-a <= maximum for a, b in zip(indices, indices[1:]))
                assert total-1-indices[-1] <= maximum
                assert all(not row["acquire"] for row in trace[indices[-1]+1:])


def test_observed_shape_cue_can_increase_density_before_scripted_split():
    config = ControllerConfig(min_gap=2, max_gap=10, uncertainty_weight=0, motion_weight=0,
                              event_weight=1, gap_weight=0.4, threshold=0.35)
    stable, _ = drive(policy(config), clip(40), 10)
    event, trace = drive(policy(config), clip(40, elongate=True), 10)
    assert len(event) == len(stable) == 10
    assert sum(8 < t <= 16 for t in event) > sum(8 < t <= 16 for t in stable)
    assert any(row["event_interest"] > 0.5 and row["reason"] == "priority_threshold" for row in trace if 8 < row["t"] <= 16)
    assert any(row["acquire"] for row in trace if 8 < row["t"] < 17)


def test_high_uncertainty_can_trigger_earlier_capture_and_empty_scene_is_safe():
    config = ControllerConfig(min_gap=1, max_gap=12, gap_weight=0.1, motion_weight=0, event_weight=0,
                              uncertainty_weight=1, threshold=0.8)
    a, _ = drive(policy(config, tracking_config=TrackingConfig(process_sigma_um_per_frame=0.01)), clip(30), 5)
    b, trace = drive(policy(config, tracking_config=TrackingConfig(process_sigma_um_per_frame=0.5)), clip(30), 5)
    assert b[1] < a[1]
    empty, empty_trace = drive(policy(config), [np.zeros((41, 41), dtype=np.float32)] * 30, 5)
    assert len(empty) == 5
    assert all(np.isfinite(row["score"]) for row in trace + empty_trace)


def test_unexpected_change_affects_only_decisions_after_acquisition():
    config = ControllerConfig(min_gap=1, max_gap=12)
    frames = clip(30)
    indices, before = drive(policy(config), frames, 6)
    changed = [frame.copy() for frame in frames]
    next_acquisition = indices[1]
    changed[next_acquisition] = np.zeros_like(changed[next_acquisition])
    _, after = drive(policy(config), changed, 6)
    assert before[:next_acquisition+1] == after[:next_acquisition+1]
    assert before[next_acquisition+1]["uncertainty_um"] != after[next_acquisition+1]["uncertainty_um"]


@pytest.mark.parametrize("name", ["photon_adaptive", "image_change"])
def test_real_runner_api_reads_only_acquisitions_and_unseen_perturbation_is_inert(tmp_path, name):
    frames = clip(30, elongate=True)
    reads = []
    sequence = SimpleNamespace(metadata=metadata(30), fingerprint="synthetic-controlled", provenance={},
                               read=lambda t: (reads.append(t) or frames[t]))
    config = ControllerConfig(min_gap=2, max_gap=9)
    a = run_replay(sequence, policy(config, name=name), 7, 42, tmp_path/"first")
    assert reads == list(a.acquired_indices)
    for t in set(range(30)) - set(a.acquired_indices):
        frames[t] = np.random.default_rng(t).uniform(0, 1, (41, 41)).astype(np.float32)
    reads.clear()
    b = run_replay(sequence, policy(config, name=name), 7, 42, tmp_path/"repeat")
    assert reads == list(b.acquired_indices)
    assert a.decisions == b.decisions and a.acquired_indices == b.acquired_indices
    for filename in ("config.json", "decisions.jsonl", "metrics.json", "timeline.txt", "observed.png"):
        assert (tmp_path/"first"/filename).read_bytes() == (tmp_path/"repeat"/filename).read_bytes()
    stored = json.loads((tmp_path/"first/config.json").read_text())
    assert stored["controller_config"]["max_gap"] == 9
    for row in a.decisions:
        assert row["remaining_budget_after"] >= 0
        assert row["last_acquired_index_before"] is None or row["last_acquired_index_before"] < row["t"]
        assert row["reason"] != "precommitted baseline schedule"
        assert np.isfinite(row["score"])


def test_invalid_parameters_and_policy_lifecycle():
    for kwargs in ({"min_gap": 0}, {"min_gap": True}, {"min_gap": 3, "max_gap": 2},
                   {"threshold": float("nan")}, {"uncertainty_scale_um": 0}):
        with pytest.raises(ValueError):
            ControllerConfig(**kwargs)
    p = policy()
    p.reset(metadata(10), 3, 0)
    assert p.decide(0, ())
    with pytest.raises(ValueError, match="pending"):
        p.decide(1, ())
    with pytest.raises(ValueError, match="pending"):
        p.observe(ObservedFrame(1, clip(1)[0], "synthetic"))
    p.observe(ObservedFrame(0, clip(1)[0], "synthetic"))
    with pytest.raises(ValueError, match="history"):
        p.decide(1, ())


def test_animation_reads_only_recorded_acquisitions_and_holds_each_policies_own_past(tmp_path, monkeypatch):
    from PIL import Image
    frames = []
    for t in range(10):
        image = np.zeros((41, 41), dtype=np.float32)
        image[5+t:9+t, 10:25] = 1
        frames.append(image)
    reads = []
    sequence = SimpleNamespace(metadata=metadata(10), fingerprint="animation-fixture", provenance={},
                               read=lambda t: (reads.append(t) or frames[t]))
    outputs = tmp_path/"runs"
    a = run_replay(sequence, ScheduledPolicy("fixed_interval"), 4, 42, outputs/"fixed_interval")
    b = run_replay(sequence, policy(ControllerConfig(min_gap=1, max_gap=7)), 4, 42, outputs/"photon_adaptive")
    reads.clear()
    script = Path(__file__).resolve().parents[3]/"scripts/build_schedule_replay.py"
    spec = importlib.util.spec_from_file_location("schedule_viewer", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "load_sequence", lambda *args, **kwargs: sequence)
    output = tmp_path/"replay.gif"
    monkeypatch.setattr(sys, "argv", [str(script), "--runs", str(outputs), "--output", str(output)])
    module.main()
    manifest = json.loads(output.with_suffix(".json").read_text())
    assert reads == sorted(set(a.acquired_indices) | set(b.acquired_indices)) == manifest["image_read_indices"]
    with Image.open(output) as movie:
        assert movie.n_frames == 10 and movie.size == (680, 460)
    preview = Image.open(output.with_suffix(".png"))
    t = manifest["preview_index"]
    for column, record in enumerate((a, b)):
        last = max(index for index in record.acquired_indices if index <= t)
        expected = Image.fromarray((frames[last]*255).astype(np.uint8)).resize((320, 320)).convert("RGB")
        x = 10 + column*340
        np.testing.assert_array_equal(np.asarray(preview.crop((x+2, 57, x+318, 373))),
                                      np.asarray(expected.crop((2, 2, 318, 318))))
