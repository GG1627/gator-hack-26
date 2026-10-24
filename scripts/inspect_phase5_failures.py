"""Post-hoc scientific case panels; never imported by the acquisition code."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from photon.benchmark import file_hash, write_json
from photon.data import load_sequence
from photon.development import load_scenes
from photon.gaussian import IntensityCalibration, render_gaussians


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("runs/phase5"))
    parser.add_argument("--data", type=Path, default=Path("data/mskcc-audit/mskcc-confocal"))
    args = parser.parse_args()
    benchmark = json.loads((args.output/"benchmark.json").read_text())
    # This consumer runs only after trusted verification and full recomputation.
    for name in ("verification.json", "recomputation.json"):
        evidence = json.loads((args.output/name).read_text())
        if not evidence["verified"] or evidence["protocol_sha256"] != benchmark["protocol_sha256"]:
            raise ValueError("Post-hoc case panels require verified, fully recomputed results")
    output = args.output/"cases"
    output.mkdir(exist_ok=True)
    sequences, manifest = {}, []
    for key, group in benchmark["groups"].items():
        sid, budget = key.split("/")
        if sid not in sequences:
            sequence = load_sequence(args.data/sid, dataset_id="MSKCC-CONFOCAL")
            if sequence.fingerprint != benchmark["protocol"]["data_validation"]["sequences"][sid]["sequence_sha256"]:
                raise ValueError("Source changed")
            sequences[sid] = sequence
        sequence = sequences[sid]
        configs = {name: json.loads((args.output/key/name/"config.json").read_text()) for name in ("fixed", "photon")}
        forecasts = {name: load_scenes(args.output/key/name/"forecasts.npz") for name in configs}
        calibration = IntensityCalibration(**group["normalization"])
        for direction, field in (("loss", "largest_raw_hold_losses"), ("win", "largest_raw_hold_wins")):
            ranked = group["failure_analysis"][field]
            if not ranked:  # Never call a small loss a win (or a small win a loss).
                continue
            case = ranked[0]
            t = case["t"]
            truth = calibration.normalize(sequence.read(t))
            truth_mip = truth.max(axis=0)
            fig, axes = plt.subplots(2, 3, figsize=(11, 7), constrained_layout=True)
            sources = {}
            for row, name in enumerate(("fixed", "photon")):
                last = max(index for index in configs[name]["acquired_indices"] if index < t)
                raw_hold = calibration.normalize(sequence.read(last))
                predicted = render_gaussians(sequence.metadata.shape, forecasts[name][t])
                for col, (pixels, title) in enumerate(((raw_hold.max(axis=0), f"{name}: MEASURED t={last}, held"),
                                                       (predicted.max(axis=0), f"{name}: PREDICTED t={t}"),
                                                       (truth_mip, f"GROUND TRUTH t={t} (EVAL ONLY)"))):
                    axes[row, col].imshow(pixels, cmap="gray", vmin=0, vmax=1)
                    axes[row, col].set_title(title, fontsize=10)
                    axes[row, col].axis("off")
                sources[name] = {"last_acquired_index": last,
                                 "forecast_scene_sha256": file_hash(args.output/key/name/"forecasts.npz")}
            difference = case["photon_minus_fixed_raw_hold_mse"]
            fig.suptitle(f"{sid}, {budget}, t={t}: largest matched raw-hold {direction}\n"
                         f"PHOTON minus fixed 3D MSE = {difference:+.6g}; panels are MIPs, scores use full volumes\n"
                         "Exploratory post-hoc case selection; not a new test or policy input", fontsize=11)
            filename = f"{sid}-{budget}-{direction}-t{t}.png"
            fig.savefig(output/filename, dpi=150)
            plt.close(fig)
            manifest.append({"group": key, "direction": direction, **case, "sources": sources,
                             "figure": filename, "display_normalization": group["normalization"],
                             "display": "maximum-intensity projection, shared frozen normalization [0,1]",
                             "selection": "largest signed matched raw-hold difference, after evaluation; no tuning"})
    write_json(output/"manifest.json", {"protocol_sha256": benchmark["protocol_sha256"], "cases": manifest})
    print(f"Saved {len(manifest)} post-hoc case panels. No policy executed.")


if __name__ == "__main__":
    main()
