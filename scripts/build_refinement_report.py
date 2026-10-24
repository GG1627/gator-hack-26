"""Write a readable development report directly from measured JSON artifacts."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=Path("runs/mskcc-phase3-refinement"))
    parser.add_argument("--output", type=Path, default=Path("docs/phase3-refinement-results.md"))
    args = parser.parse_args()
    summary = json.loads((args.run/"summary.json").read_text())
    protocol = json.loads((args.run/"protocol.json").read_text())
    names = ("fixed", "original", "paced", "robust", "paced_robust")
    selected = summary["selected_variant"]
    lines = ["# Phase 3 refinement: measured development results", "",
             "Exploratory selection on MSKCC s1 source frames 0..269 only. No s2/s3",
             "evaluation was used. All methods acquired 54 complete volumes, including",
             "frame zero. These results do not establish generalization or biological benefit.", "",
             f"Selected by the [fixed development protocol](phase3-refinement-plan.md): **{selected}**.", "",
             "The adoption rule requires more covered events than original and no higher",
             "common-target raw hold-last MSE, then ranks coverage, raw-hold MSE and name.", "",
             "## Schedule and retrospective event coverage", "",
             "Coverage counts canonical binary divisions with a capture within +/-1 source",
             "frame of the first daughter time. Simultaneous divisions count separately.",
             "This is temporal observation coverage, not detection recall or alert precision.", "",
             "| Variant | First-half captures | Max gap | Terminal age | Covered events | Coverage |",
             "|---|---:|---:|---:|---:|---:|"]
    for name in names:
        value = summary["variants"][name]
        event = value["event"]
        coverage = f"{100*event['event_coverage']:.2f}%" if event["event_coverage"] is not None else "not measured"
        count = f"{event['covered_events']}/{event['events']}" if event["event_coverage"] is not None else "not measured"
        lines.append(f"| {name} | {value['captures_in_first_half']} | {value['max_gap']} | {value['terminal_age']} | {count} | {coverage} |")
    lines += ["", "## Reconstruction on identical withheld times", "",
              f"All five schedules share **{len(summary['common_withheld_indices'])} withheld target times**. These",
              "tables use exactly that intersection. Full3D voxel-weighted errors use the",
              "first acquisition's frozen normalization and [0,1] clipping. Foreground is",
              "evaluation-only normalized truth signal>0.1, shared by all estimators for",
              "each target. Own-withheld results are also saved in JSON, but those sets differ.", "",
              "Gaussian hold freezes the last fitted scene and isolates motion extrapolation.",
              "Raw hold carries forward the last measured volume. Neither reads future truth."]
    for field, title in (("mse", "Whole-volume MSE"), ("foreground_mse", "Foreground MSE")):
        lines += ["", f"### {title}", "", "| Variant | Gaussian forecast | Gaussian hold | Raw hold-last |",
                  "|---|---:|---:|---:|"]
        for name in names:
            scores = summary["variants"][name]["common_withheld"]
            values = [f"{scores[estimator][field]:.10g}" if scores[estimator][field] is not None else "not measured"
                      for estimator in ("gaussian_forecast", "gaussian_hold", "raw_hold")]
            lines.append(f"| {name} | " + " | ".join(values) + " |")
    lines += ["", "### Each method's own withheld targets", "",
              "All methods withhold216 frames, but the timestamps differ. These scores",
              "complement the matched-target comparison and can rank methods differently.", "",
              "| Variant | Gaussian forecast MSE | Gaussian hold MSE | Raw hold-last MSE |",
              "|---|---:|---:|---:|"]
    for name in names:
        values = summary["variants"][name]["own_withheld"]
        lines.append(f"| {name} | " + " | ".join(f"{values[estimator]['mse']:.10g}" for estimator in ("gaussian_forecast", "gaussian_hold", "raw_hold")) + " |")
    lines += ["", "## Interpretation and limits", "",
              "Only the declared variants were evaluated; no post-score parameter search was",
              "performed. The original run and all losing variants are preserved. A selected",
              "variant can still lose to fixed sampling or raw hold-last; read all tables.", "",
              "In this run fixed sampling covers more events and has lower own-withheld raw",
              "MSE than the selected variant. The selected variant has lower common-target raw",
              "MSE. There is no overall superiority claim over fixed sampling. Most coverage",
              "gain over original comes from pacing; robust aggregation adds one covered event",
              "over pacing-only here. Gaussian forecasts lose strongly to raw hold-last, and",
              "their motion extrapolation also loses slightly to holding the fitted scene.", "",
              "Event counts are clustered within one embryo and are not independent biological",
              "replicates. Reconstruction includes camera noise and simplified-Gaussian appearance",
              "bias. The shared withheld set is schedule-dependent, and the first-acquisition",
              "normalization is not a photon-count calibration. Future Phase5 must evaluate frozen",
              "settings on independent s2/s3 windows and multiple budgets before broad claims.", "",
              "Forecast geometry was saved during causal replay. All five oracles closed before",
              "truth or lineage labels were read for scoring. Offline rendering uses only saved",
              "geometry, fixed normalization and public volume shape; truth never updates it.", "",
              "Artifacts: `runs/mskcc-phase3-refinement/` contains protocol, configs, decision",
              "traces, forecast/held-scene archives, final states, per-frame errors and summary.",
              "`source-snapshot.zip` preserves the exact comparison implementation. Metric",
              "accounting/source-probe evidence is in `verification.json` when checks complete.", "",
              f"Comparison science SHA256: `{protocol['science_code_sha256']}`.",
              f"Source SHA256: `{protocol['source_sha256']}`.", ""]
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote measured report: {args.output}")


if __name__ == "__main__":
    main()
