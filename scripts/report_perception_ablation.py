"""Create an evidence figure/report from verified detector-ablation outputs."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=Path("runs/perception-controller-ablation"))
    args=parser.parse_args();folder=args.output
    verification=json.loads((folder/"verification.json").read_text())
    source=folder/"summary.json";summary_bytes=source.read_bytes()
    if not verification.get("verified") or verification["summary_sha256"]!=hashlib.sha256(summary_bytes).hexdigest():
        raise ValueError("Current summary must pass verification before reporting")
    summary=json.loads(summary_bytes);protocol=json.loads((folder/"protocol.json").read_text())
    names=protocol["names"];values=summary["variants"]
    labels={"fixed":"Fixed timing","adaptive":"Original adaptive","watershed":"Adaptive + watershed"}
    colors={"fixed":"#6b726d","adaptive":"#547f83","watershed":"#b04c3c"}
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.spines.top":False,
        "axes.spines.right":False,"figure.facecolor":"#f7f6f1","axes.facecolor":"#f7f6f1",
        "text.color":"#252a29","axes.labelcolor":"#252a29","xtick.color":"#636762","ytick.color":"#636762"})
    fig,axes=plt.subplots(1,3,figsize=(15.5,4.8),gridspec_kw={"width_ratios":[1.35,1,1]})
    for index,name in enumerate(names):
        indices=values[name]["acquired_indices"]
        axes[0].scatter(indices,[index]*len(indices),s=11,color=colors[name],marker="|")
    axes[0].set(yticks=range(len(names)),yticklabels=[labels[n] for n in names],xlabel="Source frame",xlim=(-3,272),
        ylim=(2.6,-.6),title=f"Same image budget: {protocol['budget']} / {protocol['frame_count']}")
    counts=[values[n]["event"]["covered_events"] for n in names]
    axes[1].bar(range(len(names)),counts,color=[colors[n] for n in names],width=.6)
    axes[1].set(xticks=range(len(names)),xticklabels=["Fixed","Adaptive","Adaptive\n+ watershed"],
        ylabel="Annotated divisions covered",title="Retrospective event coverage (±1)")
    for index,count in enumerate(counts): axes[1].text(index,count+3,str(count),ha="center",fontsize=11)
    axes[1].set_ylim(0,max(counts)*1.2)
    scores=[values[n]["common_withheld"]["raw_hold"]["mse"] for n in names]
    axes[2].bar(range(len(names)),scores,color=[colors[n] for n in names],width=.6)
    axes[2].set(xticks=range(len(names)),xticklabels=["Fixed","Adaptive","Adaptive\n+ watershed"],
        ylabel="Normalized full-volume MSE ↓",title=f"Raw hold · {len(summary['common_withheld_indices'])} common targets")
    axes[2].ticklabel_format(axis="y",style="sci",scilimits=(-2,2))
    fig.suptitle("Detector-only acquisition ablation · development embryo s1",x=.02,ha="left",fontsize=17)
    fig.text(.02,.02,"Exploratory development only. Matched targets depend on the schedules. Event coverage is capture timing; cell health was not measured.",fontsize=9,color="#636762")
    fig.tight_layout(rect=(0,.06,1,.9));fig.savefig(folder/"comparison.png",dpi=170);fig.savefig(folder/"comparison.svg");plt.close(fig)
    lines=["# Detector-only acquisition ablation", "", "Exploratory development on the previously inspected s1 embryo; not held-out evidence.", "",
        f"Every schedule acquired {protocol['budget']} of {protocol['frame_count']} complete volumes. Exposure proxy is {protocol['budget']/protocol['frame_count']:.3f} for every method.", "",
        "![Acquisition, event coverage and common-target error](comparison.png)","",
        "| Method | Divisions covered | Own-target raw MSE | Common-target raw MSE | Common Gaussian forecast MSE |",
        "|---|---:|---:|---:|---:|"]
    for name in names:
        value=values[name];event=value["event"]
        lines.append(f"| {labels[name]} | {event['covered_events']} / {event['events']} | {value['own_withheld']['raw_hold']['mse']:.8f} | {value['common_withheld']['raw_hold']['mse']:.8f} | {value['common_withheld']['gaussian_forecast']['mse']:.8f} |")
    lines += ["",f"Three-way-common withheld targets: {len(summary['common_withheld_indices'])}. Own-target sets differ. Pairwise comparisons are below.","",
        "| Pair | Common targets | Left raw MSE | Right raw MSE |","|---|---:|---:|---:|"]
    for pair,value in summary["pairwise_common"].items():
        left,right=value["methods"]
        lines.append(f"| {labels[left]} / {labels[right]} | {value['frames']} | {value['methods'][left]['raw_hold']['mse']:.8f} | {value['methods'][right]['raw_hold']['mse']:.8f} |")
    gate=summary["development_gate"]
    lines += ["", "## Registered development criterion", "",
        f"More annotated events than original adaptive: **{gate['more_events_than_original_adaptive']}**. Pairwise-common raw-hold MSE no worse: **{gate['no_worse_pairwise_raw_hold_mse']}**.","",
        f"Combined criterion met: **{gate['criterion_met']}**. This does not establish generalization, biological benefit or automatic production promotion.","",
        "## Verification and limitations","",
        "Source registration, exact budgets, causal ledgers, gap constraints, event counts and scalar accounting were checked. Independent full source rerender status is recorded separately in recomputation.json when available.","",
        "The three-way-common plot is one view, not an overall-superiority claim. Keep the own-target and pairwise tables alongside it. No new detector thresholds or controller parameters were selected from these outcomes.","",
        "Original artifacts: protocol.json, source.zip, summary.json, per-method configs/traces/scenes/evaluation rows, verification.json and the acquisition-stage annotation-hash supplement.",""]
    (folder/"report.md").write_text("\n".join(lines),encoding="utf-8")
    (folder/"report-provenance.json").write_text(json.dumps({"summary_sha256":verification["summary_sha256"],
        "report_script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+"\n")
    print(f"Created {folder/'report.md'} and comparison.png/svg from the verified summary.")


if __name__=="__main__": main()
