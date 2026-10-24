"""Standalone scientific chart and transparent card data from trusted JSON."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from photon.benchmark import ESTIMATORS, write_json


def build_report(root):
    benchmark = json.loads((root/"benchmark.json").read_text(encoding="utf-8"))
    cards = []
    lines = ["# PHOTON held-out Phase 5 results", "",
             "Generated from benchmark.json; CPU, frozen paced_robust, s2/s3 only.", "",
             "Event coverage is retrospective observation coverage, not event detection. Acquisition count is an exposure proxy; biological phototoxicity was not measured.", "",
             "| Embryo | B/270 | Policy | Events | Own raw MSE | Matched raw MSE | Fixed on same targets | Own Gaussian forecast MSE |",
             "|---|---:|---|---:|---:|---:|---:|---:|"]
    for key, group in benchmark["groups"].items():
        for method, value in group["variants"].items():
            event = value["event"]
            events = f"{event['covered_events']}/{event['events']}" if event["event_coverage"] is not None else "not available"
            lines.append(f"| {key.split('/')[0]} | {group['budget']} | {method} | {events} | {value['own_withheld']['raw_hold']['mse']:.9g} | {value['matched_fixed']['raw_hold']['mse']:.9g} | {value['fixed_on_matched']['raw_hold']['mse']:.9g} | {value['own_withheld']['gaussian_forecast']['mse']:.9g} |")
            cards.append({"group": key, "method": method, "acquisitions": value["acquisitions"],
                          "relative_exposure_proxy": value["relative_exposure_proxy"],
                          "event": event, "own_withheld": value["own_withheld"],
                          "matched_fixed": value["matched_fixed"], "fixed_on_matched": value["fixed_on_matched"]})
    lines += ["", "## Fixed versus PHOTON", ""]
    for key, group in benchmark["groups"].items():
        diff = group["comparison"]
        event_difference = diff['photon_minus_fixed_event_coverage']
        event_text = f"{event_difference:+.6f}" if event_difference is not None else "not available"
        lines.append(f"- {key}: event coverage difference {event_text}; matched raw-hold MSE difference {diff['photon_minus_fixed_matched_raw_hold_mse']:+.9g} on {diff['matched_target_count']} targets. Positive error difference favors fixed.")
        fail = group["failure_analysis"]
        lines.append(f"  Fixed-only covered events {len(fail['fixed_only_events'])}; PHOTON-only {len(fail['photon_only_events'])}; missed by both {len(fail['missed_by_both_events'])}. All identities and extreme errors are retained in benchmark.json.")
    lines += ["", "Random seeds 7/42/2026 are repeated schedules, not independent embryos. Random has no hard gap constraint. Own-withheld and matched targets differ and can reverse rankings. Matched sets depend on schedules. Gaussian hold versus forecast isolates the motion contribution; both use an approximate appearance model.", "",
              "Only two independent held-out embryos; no statistical significance, calibrated event forecasting, or generalization to mammalian cells is established. No held-out tuning was performed. Phase 6 UI has not started.", ""]
    (root/"report.md").write_text("\n".join(lines), encoding="utf-8")
    write_json(root/"cards.json", {"source": "benchmark.json", "protocol_sha256": benchmark["protocol_sha256"], "cards": cards})
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    random_summary = {}
    def event_percent(value):
        coverage = value["event"]["event_coverage"]
        return coverage*100 if coverage is not None else np.nan
    for col, sid in enumerate(benchmark["protocol"]["evaluation_sequences"]):
        groups = [benchmark["groups"][f"{sid}/b{b}"] for b in benchmark["protocol"]["budgets"]]
        budgets = [g["budget"] for g in groups]
        for name, color, marker in (("fixed", "#444444", "s"), ("photon", "#007c91", "o"), ("image_change", "#a54e00", "^")):
            axes[0, col].plot(budgets, [event_percent(g["variants"][name]) for g in groups], label=name, color=color, marker=marker)
        random_values = np.array([[event_percent(g["variants"][f"random_{s}"]) for s in (7,42,2026)] for g in groups])
        axes[0, col].plot(budgets, random_values.mean(axis=1), label="random mean (3 seeds)", color="#7350a2", linestyle="--")
        axes[0, col].fill_between(budgets, random_values.min(axis=1), random_values.max(axis=1), color="#7350a2", alpha=0.12, label="random min–max")
        random_summary[sid] = {str(b): {"event_coverage_percent_mean": float(row.mean()) if np.isfinite(row).all() else None,
                                      "min": float(row.min()) if np.isfinite(row).all() else None,
                                      "max": float(row.max()) if np.isfinite(row).all() else None} for b, row in zip(budgets, random_values)}
        if not np.isfinite(random_values).any():
            axes[0, col].text(.5, .5, "Event coverage not available", transform=axes[0, col].transAxes, ha="center")
        for name, color, marker in (("photon", "#007c91", "o"), ("fixed", "#444444", "s")):
            # Same pairwise target set for both curves in this panel.
            field = "matched_fixed" if name == "photon" else "fixed_on_matched"
            axes[1, col].plot(budgets, [g["variants"]["photon"][field]["raw_hold"]["mse"] for g in groups], label=name+" raw hold", color=color, marker=marker)
        axes[0, col].set(title=sid+": annotated event coverage", ylabel="Covered events (%)", ylim=(0, 105))
        axes[1, col].set(title="Fixed/PHOTON common withheld targets", ylabel="Normalized 3D raw-hold MSE")
        for ax in axes[:, col]:
            ax.set_xlabel("Acquired volumes / 270")
            ax.set_xticks(budgets)
            ax.grid(alpha=.2)
            ax.legend(fontsize=8)
    fig.suptitle("PHOTON held-out evaluation: equal capture counts, frozen controller\nTwo embryos; schedule-dependent targets; exposure proxy only", fontsize=13)
    fig.savefig(root/"comparison.png", dpi=170)
    fig.savefig(root/"comparison.svg")
    plt.close(fig)
    write_json(root/"random-summary.json", random_summary)
    # Every card is a direct projection of the trusted result, with no scoring logic.
    for card in cards:
        result = benchmark["groups"][card["group"]]["variants"][card["method"]]
        if any(card[key] != result[key] for key in card if key not in ("group", "method")):
            raise ValueError("Generated card differs from trusted benchmark")
    write_json(root/"report-verification.json", {"verified": True, "cards": len(cards), "source": "benchmark.json", "all_card_fields_exact": True})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("runs/phase5"))
    args = parser.parse_args()
    build_report(args.output)


if __name__ == "__main__":
    main()
