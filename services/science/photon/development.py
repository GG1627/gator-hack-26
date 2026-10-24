"""Trusted development replay/evaluator. Never imported by acquisition policies.

All forecast geometry is frozen causally before evaluation. Raw truth and lineage
labels become available only after every compared oracle has closed. Saved scene
archives allow independent metric recomputation without running a policy again.
"""
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy

from photon.annotations import audit_mamut
from photon.gaussian import Gaussian, IntensityCalibration, render_gaussians
from photon.oracle import ReplayOracle
from photon.replay import RunRecord
from photon.tracking import GaussianSceneModel


def science_hash():
    digest = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob("*.py")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def save_scenes(path, scenes, ndim):
    times, offsets, values = [], [0], []
    for t, scene in sorted(scenes.items()):
        times.append(t)
        values.extend(scene)
        offsets.append(len(values))
    np.savez_compressed(path, times=np.array(times, dtype=np.int64), offsets=np.array(offsets, dtype=np.int64),
                        centers=np.array([g.center for g in values]).reshape(-1, ndim),
                        covariances=np.array([g.covariance for g in values]).reshape(-1, ndim, ndim),
                        amplitudes=np.array([g.amplitude for g in values]))


def load_scenes(path):
    with np.load(path, allow_pickle=False) as archive:
        times, offsets = archive["times"], archive["offsets"]
        centers, covariances, amplitudes = archive["centers"], archive["covariances"], archive["amplitudes"]
        if (len(offsets) != len(times)+1 or offsets[0] != 0 or offsets[-1] != len(amplitudes)
                or np.any(np.diff(offsets) < 0) or np.any(np.diff(times) <= 0)
                or len(centers) != len(amplitudes) or len(covariances) != len(amplitudes)):
            raise ValueError("Malformed saved Gaussian scenes")
        return {int(t): [Gaussian(centers[i], covariances[i], float(amplitudes[i]))
                         for i in range(offsets[j], offsets[j+1])] for j, t in enumerate(times)}


@dataclass
class ClosedDevelopmentRun:
    label: str
    oracle: ReplayOracle
    record: RunRecord
    forecasts: dict
    held_scenes: dict
    calibration: IntensityCalibration


def record_development_run(sequence, policy, budget, seed, label, output):
    """Trusted runner: no withheld reads, no annotations, no scoring feedback."""
    output = Path(output)
    if output.exists():
        raise ValueError("Development run output already exists")
    oracle = ReplayOracle(sequence, budget)
    metadata = oracle.public_metadata()
    policy.reset(metadata, budget, seed)
    model = getattr(policy, "model", None)
    if model is None:
        spacing = metadata.voxel_size_xyz_um
        if spacing is None and metadata.source != "synthetic":
            raise ValueError("Physical spacing required")
        model = GaussianSceneModel(tuple(reversed(spacing)) if spacing else (1.0,)*len(metadata.shape))
    history, decisions, forecasts, held = [], [], {}, {}
    for t in range(metadata.frame_count):
        oracle.advance(t)
        acquire = policy.decide(t, tuple(history))
        detail = dict(getattr(policy, "last_decision", None) or {})
        if type(acquire) is not bool or (t == 0 and not acquire):
            raise ValueError("Invalid policy acquisition action")
        before = budget-len(history)
        if acquire:
            frame = oracle.acquire(t)
            policy.observe(frame)
            if model is not getattr(policy, "model", None):
                model.observe(frame)
            history.append(frame)
            held[t] = model.scene_at(t)
            if len(history) == 1 or len(history) % 10 == 0:
                print(f"{label}: acquired t={t}, {len(history)}/{budget}", flush=True)
        else:
            forecasts[t] = model.scene_at(t)
        decisions.append({"t": t, "decision": "ACQUIRE" if acquire else "SKIP",
                          "remaining_budget_before": before, "remaining_budget_after": budget-len(history),
                          "last_acquired_index": history[-1].index, "reason": "fixed schedule", **detail})
    record = RunRecord(policy.name, seed, budget, oracle.finish(), tuple(decisions))
    oracle.evaluate_after_run(record)  # closure verified before saving sealed outputs
    output.mkdir(parents=True)
    config = {**asdict(metadata), "variant": label, "policy": policy.name, "budget": budget, "seed": seed,
              "acquired_indices": list(record.acquired_indices), "sequence_sha256": sequence.fingerprint,
              "photon_code_sha256": science_hash(), "model_version": "causal-moment-gaussian-v1",
              "normalization": model.calibration.to_dict(), "numpy_version": np.__version__,
              "scipy_version": scipy.__version__, "hardware": {"kernel_backend": "cpu", "gpu": None},
              "scope": "exploratory s1 development ablation, not held-out evidence"}
    if hasattr(policy, "configuration"):
        extra = policy.configuration()
        extra.pop("state_after_run", None)
        config.update(extra)
    (output/"config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    (output/"decisions.jsonl").write_text("".join(json.dumps(row)+"\n" for row in decisions), encoding="utf-8")
    (output/"state.json").write_text(json.dumps(model.state_dict(), indent=2), encoding="utf-8")
    save_scenes(output/"forecasts.npz", forecasts, len(metadata.shape))
    save_scenes(output/"held_scenes.npz", held, len(metadata.shape))
    return ClosedDevelopmentRun(label, oracle, record, forecasts, held, model.calibration)


def load_closed_run(sequence, folder):
    """Recreate the acquisition-only oracle ledger, then load immutable forecasts.

    Does not fit a model or execute policy code. No labels/withheld reads until
    the independent evaluator subsequently runs.
    """
    folder = Path(folder)
    config = json.loads((folder/"config.json").read_text())
    if config["sequence_sha256"] != sequence.fingerprint:
        raise ValueError("Saved run source hash differs")
    indices = tuple(config["acquired_indices"])
    decisions = tuple(json.loads(line) for line in (folder/"decisions.jsonl").read_text().splitlines())
    total = sequence.metadata.frame_count
    if (len(decisions) != total or [row["t"] for row in decisions] != list(range(total))
            or [row["t"] for row in decisions if row["decision"] == "ACQUIRE"] != list(indices)
            or len(indices) != config["budget"] or not indices or indices[0] != 0):
        raise ValueError("Invalid saved acquisition trace")
    oracle = ReplayOracle(sequence, config["budget"])
    for t in range(total):
        oracle.advance(t)
        if t in indices:
            oracle.acquire(t)
    record = RunRecord(config["policy"], config["seed"], config["budget"], oracle.finish(), decisions)
    forecasts, held = load_scenes(folder/"forecasts.npz"), load_scenes(folder/"held_scenes.npz")
    if set(forecasts) != set(range(total))-set(indices) or set(held) != set(indices):
        raise ValueError("Saved scene timestamps do not match acquisition ledger")
    return ClosedDevelopmentRun(config["variant"], oracle, record, forecasts, held,
                                IntensityCalibration(**config["normalization"]))


def event_coverage(indices, annotation, tolerance):
    if isinstance(tolerance, bool) or not isinstance(tolerance, int) or tolerance < 0:
        raise ValueError("Event tolerance must be a nonnegative source-frame integer")
    if not annotation or not annotation.get("available"):
        return {"event_coverage": None, "reason": "No canonical event annotations available"}
    if not annotation.get("all_requested_frames_have_annotations"):
        raise ValueError("Incomplete temporal annotations cannot define whole-window event coverage")
    times = annotation["division_times"]
    if not times:
        return {"event_coverage": None, "reason": "No annotated binary divisions in window", "events": 0}
    covered = [any(abs(t-index) <= tolerance for index in indices) for t in times]
    return {"event_coverage": sum(covered)/len(times), "covered_events": sum(covered), "events": len(times),
            "tolerance_frames": tolerance, "missed_event_ordinals": [i for i, value in enumerate(covered) if not value],
            "definition": "retrospective capture within +/- tolerance of first daughter frame; simultaneous events counted separately"}


def image_error(prediction, truth, roi):
    error = np.subtract(prediction, truth, dtype=np.float64)
    return {"squared_error_sum": float(np.sum(error*error)), "absolute_error_sum": float(np.sum(np.abs(error))),
            "voxel_count": int(truth.size), "foreground_squared_error_sum": float(np.sum(error[roi]**2)),
            "foreground_absolute_error_sum": float(np.sum(np.abs(error[roi]))), "foreground_voxel_count": int(roi.sum())}


def aggregate_errors(rows):
    totals = {key: sum(row[key] for row in rows) for key in image_error(np.zeros((1,)), np.zeros((1,)), np.zeros((1,), dtype=bool))}
    n, foreground = totals["voxel_count"], totals["foreground_voxel_count"]
    return {"frames": len(rows), "mse": totals["squared_error_sum"]/n if n else None,
            "mae": totals["absolute_error_sum"]/n if n else None,
            "foreground_mse": totals["foreground_squared_error_sum"]/foreground if foreground else None,
            "foreground_mae": totals["foreground_absolute_error_sum"]/foreground if foreground else None, **totals}


def evaluate_development(runs, *, annotation_path=None, event_tolerance=1, foreground_threshold=0.1):
    """No policy calls: all oracles must close before any truth/label access."""
    if not runs or len({run.label for run in runs}) != len(runs):
        raise ValueError("Need distinct completed runs")
    for run in runs:
        run.oracle.evaluate_after_run(run.record)
    metadata = runs[0].oracle.public_metadata()
    if any(run.oracle.public_metadata() != metadata or run.record.budget != runs[0].record.budget for run in runs):
        raise ValueError("Comparison needs same metadata and exact budget")
    if not 0 < foreground_threshold < 1:
        raise ValueError("Foreground threshold must be in (0,1)")
    annotation = audit_mamut(annotation_path, metadata.frame_count) if annotation_path is not None else None
    calibration = IntensityCalibration.from_image(runs[0].oracle.read_evaluation_after_run(runs[0].record, 0).pixels)
    if any(run.calibration != calibration for run in runs):
        raise ValueError("All forecasts must use the same first-acquisition calibration")
    withheld_sets = [set(range(metadata.frame_count))-set(run.record.acquired_indices) for run in runs]
    common = sorted(set.intersection(*withheld_sets))
    if not common:
        raise ValueError("No common withheld times for comparison")
    common_set = set(common)
    estimators = ("gaussian_forecast", "gaussian_hold", "raw_hold")
    rows = {run.label: [] for run in runs}
    last_pixels, last_scene = {}, {}
    rendered_held = {}
    for t in range(metadata.frame_count):
        raw = runs[0].oracle.read_evaluation_after_run(runs[0].record, t).pixels
        truth = calibration.normalize(raw)
        roi = truth > foreground_threshold
        for run in runs:
            if t in run.held_scenes:
                last_pixels[run.label], last_scene[run.label] = truth, run.held_scenes[t]
                rendered_held.pop(run.label, None)
                continue
            if run.label not in rendered_held:
                rendered_held[run.label] = render_gaussians(metadata.shape, last_scene[run.label])
            estimates = (render_gaussians(metadata.shape, run.forecasts[t]), rendered_held[run.label], last_pixels[run.label])
            rows[run.label].append({"t": t, "common_target": t in common_set,
                                    "errors": {name: image_error(pixels, truth, roi) for name, pixels in zip(estimators, estimates)}})
        if t % 25 == 0 or t == metadata.frame_count-1:
            print(f"Offline evaluation t={t}/{metadata.frame_count-1}; no policy updates", flush=True)
    summary = {"scope": "exploratory development selection on s1 only, not held-out evidence",
               "budget": runs[0].record.budget, "event_tolerance_frames": event_tolerance,
               "foreground_definition": f"evaluation-only truth normalized signal > {foreground_threshold}",
               "common_withheld_indices": common, "normalization": calibration.to_dict(), "variants": {}}
    for run in runs:
        indices = run.record.acquired_indices
        summary["variants"][run.label] = {
            "acquired_indices": list(indices), "acquisitions": len(indices),
            "captures_in_first_half": sum(t < metadata.frame_count//2 for t in indices),
            "max_gap": max(np.diff(indices).tolist(), default=0), "terminal_age": metadata.frame_count-1-indices[-1],
            "gap_histogram": {str(gap): int(np.sum(np.diff(indices) == gap)) for gap in sorted(set(np.diff(indices).tolist()))},
            "event": event_coverage(indices, annotation, event_tolerance),
            "own_withheld": {name: aggregate_errors([row["errors"][name] for row in rows[run.label]]) for name in estimators},
            "common_withheld": {name: aggregate_errors([row["errors"][name] for row in rows[run.label] if row["common_target"]]) for name in estimators}}
    return summary, rows


def select_variant(summary):
    """Predeclared development-only event/raw-hold Pareto filter, never a policy input."""
    original = summary["variants"]["original"]
    base_coverage = original["event"]["event_coverage"]
    base_mse = original["common_withheld"]["raw_hold"]["mse"]
    eligible = []
    for name in ("paced", "robust", "paced_robust"):
        result = summary["variants"][name]
        coverage, mse = result["event"]["event_coverage"], result["common_withheld"]["raw_hold"]["mse"]
        if base_coverage is not None and coverage is not None and coverage > base_coverage and mse <= base_mse:
            eligible.append((-coverage, mse, name))
    return min(eligible)[2] if eligible else "original"
