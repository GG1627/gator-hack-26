"""Plot full caller medians/p95 from actual measured samples."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,default=Path("runs/cuda-latency-audit/matrix/latency.json"))
    p.add_argument("--output",type=Path,default=Path("runs/cuda-latency-audit/full-caller.png"))
    args=p.parse_args()
    cases=json.loads(args.input.read_text())["cases"]
    fig,ax=plt.subplots(figsize=(12,7.5))
    y=np.arange(len(cases))
    for offset,key,color,label in ((-.23,"cpu_warm","#465467","CPU reference"),
                                    (0,"worker_warm_full","#188477","Persistent GPU: full caller"),
                                    (.23,"one_shot_disk_cache_full","#cb7944","One-shot GPU: full caller")):
        med=np.array([c[key]["median_ms"] for c in cases])
        p95=np.array([c[key]["p95_ms"] for c in cases])
        ax.barh(y+offset,med,height=.21,color=color,label=label)
        ax.errorbar(med,y+offset,xerr=np.array([np.zeros(len(cases)),p95-med]),fmt="none",ecolor=color,capsize=3)
    ax.set_yticks(y,[c["label"] for c in cases]);ax.invert_yaxis()
    ax.set_xscale("log");ax.set_xlabel("Latency per complete render call (ms, log scale)")
    ax.set_title("PHOTON CPU / CUDA Rust through WSL2\nBars: median; whisker ends: sample p95 (15 calls)",loc="left",pad=45)
    ax.grid(axis="x",alpha=.2);ax.set_axisbelow(True)
    ax.spines[["top","right"]].set_visible(False)
    ax.legend(loc="upper left",bbox_to_anchor=(0,1.035),ncol=3,fontsize=8.5)
    fig.text(.27,.025,"Warm worker excludes startup/first JIT; each call includes packing, transfers, files, repair and cleanup.\nRenderer benchmark: acquisition scores and fitting remain CPU. Active laptop; no clock locks.",fontsize=9,color="#465467")
    fig.subplots_adjust(left=.27,right=.97,top=.82,bottom=.15)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(args.output,dpi=160)
    plt.close(fig)


if __name__=="__main__":main()
