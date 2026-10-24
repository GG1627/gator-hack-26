"""Standalone Matplotlib export from measured benchmark JSON."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_benchmark(report, output):
    fig, ax = plt.subplots(figsize=(12,7))
    fig.subplots_adjust(left=.26,right=.97,top=.90,bottom=.24)
    y = np.arange(len(report["cases"]))
    for offset,key,label,color in ((-.25,"cpu_reference_median_ms","CPU full reference","#747f8b"),
                                   (0,"warm_device_interval_median_ms","CUDA warm device interval","#008e82"),
                                   (.25,"single_render_caller_median_ms","CUDA full Python caller","#c47b23")):
        ax.barh(y+offset,[case[key] for case in report["cases"]],height=.22,label=label,color=color)
    ax.set_yticks(y,[case["label"] for case in report["cases"]],fontsize=11)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlabel("Median milliseconds (log scale; lower is better)",labelpad=10)
    fig.suptitle("PHOTON native CUDA Rust: measured rendering cost",fontsize=15,y=.97)
    ax.grid(axis="x",which="both",alpha=.15)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles,labels,loc="lower center",bbox_to_anchor=(.6,.08),ncol=3,fontsize=9)
    fig.text(.5,.035,"Warm device interval excludes JIT, transfers and context. Full caller includes packing, files, WSL,\n"
             "GPU, readback, repair and cleanup. Measurements do not show an application speedup.",ha="center",fontsize=9)
    fig.savefig(output,dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",type=Path,default=Path("runs/phase4-benchmark-verified"))
    args = parser.parse_args()
    report = json.loads((args.run/"benchmark.json").read_text())
    plot_benchmark(report,args.run/"timings.png")


if __name__=="__main__":
    main()
