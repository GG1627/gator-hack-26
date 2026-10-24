"""Frozen-protocol, post-closure benchmark built on the existing causal runner.

This trusted module is never imported by policies. Annotations and metric
feedback have no path back into a trajectory. Saved sufficient statistics and
causal geometry support both ledger checks and complete source recomputation.
"""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

import numpy as np

from photon.adaptive import AdaptivePolicy, ControllerConfig, controller_variant, feasible_completion
from photon.annotations import audit_mamut
from photon.development import aggregate_errors
from photon.gaussian import GaussianFitConfig
from photon.policy import ScheduledPolicy
from photon.tracking import TrackingConfig


SCOPE = "frozen Phase 5 held-out evaluation; no selection or tuning on s2/s3"
ESTIMATORS = ("gaussian_forecast", "gaussian_hold", "raw_hold")
METHODS = ("fixed", "photon", "image_change", "random_7", "random_42", "random_2026")
SEQUENCES = ("mskcc_confocal_s2", "mskcc_confocal_s3")
BUDGETS = (27, 54, 89)


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def make_policy(method):
    if method == "fixed":
        return ScheduledPolicy("fixed_interval"), 42
    if method.startswith("random_") and method in METHODS:
        return ScheduledPolicy("seeded_random"), int(method.split("_")[1])
    if method in ("photon", "image_change"):
        return AdaptivePolicy("photon_adaptive" if method == "photon" else "image_change"), 42
    raise ValueError("Unknown benchmark method")


def protocol_definition():
    # No image/label access. All values are chosen before held-out outcomes.
    for budget in BUDGETS:
        if not feasible_completion(270, 0, budget-1, 1, 2, 12):
            raise ValueError("Declared benchmark budget is infeasible")
    return {
        "version": "photon-phase5-v1", "scope": SCOPE,
        "development_sequence": "mskcc_confocal_s1", "evaluation_sequences": list(SEQUENCES),
        "source_window_inclusive": [0, 269], "budgets": list(BUDGETS), "methods": list(METHODS),
        "random_seeds": [7, 42, 2026], "deterministic_policy_seed": 42,
        "budget_semantics": "exactly B whole-volume captures including frame 0",
        "photon_controller": asdict(controller_variant("paced_robust")),
        "image_change_controller": asdict(ControllerConfig()),
        "fit_config": asdict(GaussianFitConfig()), "tracking_config": asdict(TrackingConfig()),
        "baseline_constraints": "fixed endpoint-inclusive floor spacing; random uniform without replacement including 0; random has no gap constraint",
        "adaptive_constraints": "min gap 2, max gap 12, terminal age <=12; feasible at all declared budgets",
        "event_tolerance_frames": 1, "foreground_threshold": 0.1,
        "normalization": "first acquired volume only: median background, percentile 99.99 minus median scale, clipped float32 [0,1]",
        "foreground": "evaluation-only normalized truth >0.1; not a segmentation or controller input",
        "estimators": list(ESTIMATORS),
        "primary_objectives": ["annotated event coverage", "fixed/photon pairwise-common withheld raw_hold MSE"],
        "secondary_objectives": ["own-withheld MAE/MSE", "pairwise-common foreground MAE/MSE", "all-method common errors", "Gaussian forecast/held-fit ablations"],
        "target_sets": "own withheld; exact pairwise intersection with fixed; all-method intersection (schedule dependent); no observed-frame fitting error included",
        "aggregation": "float64 voxel error sums / voxel counts; foreground voxel weighted; no averaging of per-frame foreground means",
        "event_definition": "canonical MaMuT binary parent with two immediate children, first daughter frame, nodes inside window; simultaneous events separate",
        "missing_annotations": "event_coverage null with reason; incomplete graphs rejected",
        "false_alerts": "no validated event classifier; report uncorroborated heuristic-interest >=0.5 times only, not classifier precision",
        "random_summary": "all three seeds retained, descriptive mean/min/max; seeds are not independent embryos",
        "inference": "two held-out embryos, descriptive results only; no significance or phototoxicity claim",
        "ssim": None, "ssim_reason": "3D spatial window/physical anisotropy not validated; use MAE/MSE",
        "selection_rule": "none; retain frozen paced_robust regardless of held-out wins/losses",
        "closure_rule": "every matrix trajectory closes before any outcome scoring; no policy executes during evaluation",
        "failure_analysis": "all fixed-only/photon-only covered event IDs; all misses; largest per-frame matched raw-hold MSE losses and wins; uncorroborated heuristic hints",
    }


def validate_trace(config, decisions, total):
    indices = config["acquired_indices"]
    budget = config["budget"]
    if (len(decisions) != total or not indices or indices[0] != 0 or len(indices) != budget
            or sorted(set(indices)) != indices or any(type(t) is not int or not 0 <= t < total for t in indices)):
        raise ValueError("Invalid exact-budget acquisition ledger")
    seen = []
    for t, row in enumerate(decisions):
        if row["t"] != t or row["decision"] not in ("ACQUIRE", "SKIP") or row["remaining_budget_before"] != budget-len(seen):
            raise ValueError("Invalid chronological decision ledger")
        last_before = seen[-1] if seen else None
        if row["decision"] == "ACQUIRE":
            seen.append(t)
        if (not seen or row["remaining_budget_after"] != budget-len(seen) or row["last_acquired_index"] != seen[-1]
                or row.get("last_acquired_index_before", last_before) != last_before):
            raise ValueError("Budget/history mismatch")
    if seen != indices:
        raise ValueError("Trace/config acquisition mismatch")
    if config["policy"] in ("photon_adaptive", "image_change"):
        gaps = np.diff(indices)
        if np.any(gaps < 2) or np.any(gaps > 12) or total-1-indices[-1] > 12:
            raise ValueError("Adaptive hard gap violation")


def summarize_group(summary, rows, runs, annotation, protocol):
    """Derive all comparisons from saved per-frame statistics, never retune."""
    total = runs[0].oracle.public_metadata().frame_count
    if {run.record.budget for run in runs} != {summary["budget"]}:
        raise ValueError("Unequal comparison budgets")
    if tuple(run.label for run in runs) != tuple(protocol["methods"]):
        raise ValueError("Incomplete benchmark group")
    fixed_targets = {row["t"] for row in rows["fixed"]}
    for run in runs:
        target = set(range(total))-set(run.record.acquired_indices)
        if [row["t"] for row in rows[run.label]] != sorted(target):
            raise ValueError("Evaluation contains acquired/missing/duplicate targets")
        result = summary["variants"][run.label]
        result["relative_exposure_proxy"] = len(run.record.acquired_indices)/total
        result["exposure_reduction_vs_every_volume"] = 1-len(run.record.acquired_indices)/total
        common = sorted(target & fixed_targets)
        result["matched_fixed_indices"] = common
        for key, label in (("matched_fixed", run.label), ("fixed_on_matched", "fixed")):
            selected = [row for row in rows[label] if row["t"] in set(common)]
            result[key] = {est: aggregate_errors([row["errors"][est] for row in selected]) for est in ESTIMATORS}
    fixed, photon = summary["variants"]["fixed"], summary["variants"]["photon"]
    annotation_times = annotation.get("division_times", []) if annotation and annotation.get("available") else []
    tolerance = protocol["event_tolerance_frames"]
    def covered(indices, t):
        return any(abs(index-t) <= tolerance for index in indices)
    events = annotation.get("events", []) if annotation else []
    failure = {"fixed_only_events": [], "photon_only_events": [], "missed_by_both_events": []}
    for event in events:
        a, b = (covered(result["acquired_indices"], event["daughter_frame"]) for result in (fixed, photon))
        key = "fixed_only_events" if a and not b else "photon_only_events" if b and not a else "missed_by_both_events" if not a and not b else None
        if key:
            failure[key].append(event)
    fixed_rows = {row["t"]: row for row in rows["fixed"]}
    differences = [{"t": row["t"], "photon_minus_fixed_raw_hold_mse":
                    (row["errors"]["raw_hold"]["squared_error_sum"]-fixed_rows[row["t"]]["errors"]["raw_hold"]["squared_error_sum"])/row["errors"]["raw_hold"]["voxel_count"]}
                   for row in rows["photon"] if row["t"] in fixed_targets]
    ordered = sorted(differences, key=lambda row: (row["photon_minus_fixed_raw_hold_mse"], row["t"]))
    failure["largest_raw_hold_losses"] = list(reversed([row for row in ordered if row["photon_minus_fixed_raw_hold_mse"] > 0][-5:]))
    failure["largest_raw_hold_wins"] = [row for row in ordered if row["photon_minus_fixed_raw_hold_mse"] < 0][:5]
    hint_times = [row["t"] for run in runs if run.label == "photon" for row in run.record.decisions if row.get("event_interest", 0) >= 0.5]
    failure["heuristic_hint_times"] = hint_times
    failure["uncorroborated_hint_times"] = ([t for t in hint_times if not any(abs(t-e) <= tolerance for e in annotation_times)]
                                            if annotation_times else None)
    failure["hint_caveat"] = "Uncalibrated observed-shape interest, not a validated event alert; no classifier precision/recall claimed"
    summary.update(scope=SCOPE, protocol_version=protocol["version"], failure_analysis=failure)
    summary["comparison"] = {
        "photon_minus_fixed_event_coverage": (photon["event"]["event_coverage"]-fixed["event"]["event_coverage"]
                                               if photon["event"]["event_coverage"] is not None and fixed["event"]["event_coverage"] is not None else None),
        "photon_minus_fixed_matched_raw_hold_mse": photon["matched_fixed"]["raw_hold"]["mse"]-photon["fixed_on_matched"]["raw_hold"]["mse"],
        "matched_target_count": len(photon["matched_fixed_indices"]),
        "caveat": "Matched withheld set depends on both schedules; own-withheld results retained; random is equal-count but unconstrained in gaps",
    }
    return summary


def verify_statistics(summary, rows, configs, traces, annotation, protocol):
    """Independent scalar accounting, set/event arithmetic and trace checks."""
    common = set.intersection(*(set(range(270))-set(configs[name]["acquired_indices"]) for name in protocol["methods"]))
    if summary["common_withheld_indices"] != sorted(common):
        raise ValueError("Common target intersection mismatch")
    for name in protocol["methods"]:
        config = configs[name]
        validate_trace(config, traces[name], 270)
        if config["budget"] != summary["budget"]:
            raise ValueError("Unequal comparison budgets")
        indices = config["acquired_indices"]
        expected_seed = int(name.split("_")[1]) if name.startswith("random_") else 42
        if config["seed"] != expected_seed:
            raise ValueError("Wrong declared seed")
        if name == "fixed":
            expected = [k*269//(config["budget"]-1) for k in range(config["budget"])]
            if indices != expected:
                raise ValueError("Fixed schedule rounding differs")
        elif name.startswith("random_"):
            expected = sorted([0, *np.random.default_rng(expected_seed).choice(np.arange(1,270), size=config["budget"]-1, replace=False).tolist()])
            if indices != expected:
                raise ValueError("Random schedule/seed differs")
        else:
            expected_config = protocol["photon_controller" if name == "photon" else "image_change_controller"]
            if config["controller_config"] != expected_config:
                raise ValueError("Controller differs from frozen protocol")
        if [row["t"] for row in rows[name]] != sorted(set(range(270))-set(indices)):
            raise ValueError("Wrong evaluation targets")
        result = summary["variants"][name]
        if (result["acquisitions"] != config["budget"] or result["relative_exposure_proxy"] != config["budget"]/270
                or result["exposure_reduction_vs_every_volume"] != 1-config["budget"]/270):
            raise ValueError("Exposure accounting mismatch")
        if result["acquired_indices"] != indices:
            raise ValueError("Event/trace mismatch")
        event = result["event"]
        if annotation and annotation.get("available") and annotation.get("division_times"):
            if not annotation["all_requested_frames_have_annotations"]:
                raise ValueError("Incomplete event annotations")
            times = np.asarray(annotation["division_times"], dtype=np.int64)
            covered = np.min(np.abs(times[:, None]-np.asarray(indices)[None, :]), axis=1) <= protocol["event_tolerance_frames"]
            if (event["events"] != len(times) or event["covered_events"] != int(covered.sum())
                    or event["event_coverage"] != int(covered.sum())/len(times)
                    or event["missed_event_ordinals"] != np.flatnonzero(~covered).tolist()
                    or event["tolerance_frames"] != protocol["event_tolerance_frames"]):
                raise ValueError("Independent event arithmetic differs")
        elif event["event_coverage"] is not None or not event.get("reason"):
            raise ValueError("Missing annotations must yield null with reason")
        matched = set(rows_t["t"] for rows_t in rows[name]) & {row["t"] for row in rows["fixed"]}
        if result["matched_fixed_indices"] != sorted(matched):
            raise ValueError("Pairwise target mismatch")
        for field, source_name, targets in (("own_withheld", name, set(range(270))-set(indices)),
                                            ("common_withheld", name, common),
                                            ("matched_fixed", name, matched), ("fixed_on_matched", "fixed", matched)):
            selected = [row for row in rows[source_name] if row["t"] in targets]
            for estimator in ESTIMATORS:
                value = result[field][estimator]
                if value["frames"] != len(selected):
                    raise ValueError("Incorrect metric frame count")
                for prefix in ("", "foreground_"):
                    count = sum(row["errors"][estimator][prefix+"voxel_count"] for row in selected)
                    squared = sum(row["errors"][estimator][prefix+"squared_error_sum"] for row in selected)
                    absolute = sum(row["errors"][estimator][prefix+"absolute_error_sum"] for row in selected)
                    for key, expected in ((prefix+"voxel_count", count), (prefix+"squared_error_sum", squared),
                                          (prefix+"absolute_error_sum", absolute),
                                          (prefix+"mse", squared/count if count else None), (prefix+"mae", absolute/count if count else None)):
                        if value[key] != expected:
                            raise ValueError(f"Metric accounting mismatch: {name}/{field}/{estimator}/{key}")
    photon, fixed = summary["variants"]["photon"], summary["variants"]["fixed"]
    delta = (photon["event"]["event_coverage"]-fixed["event"]["event_coverage"]
             if photon["event"]["event_coverage"] is not None and fixed["event"]["event_coverage"] is not None else None)
    comparison = summary["comparison"]
    if (comparison["photon_minus_fixed_event_coverage"] != delta
            or comparison["matched_target_count"] != len(photon["matched_fixed_indices"])
            or comparison["photon_minus_fixed_matched_raw_hold_mse"] !=
            photon["matched_fixed"]["raw_hold"]["mse"]-photon["fixed_on_matched"]["raw_hold"]["mse"]):
        raise ValueError("Primary comparison differs from run metrics")
    return True
