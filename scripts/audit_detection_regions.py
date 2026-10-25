"""Offline s1 diagnostic on five preselected acquired volumes; no controller changes."""
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import ndimage
import tifffile
from photon.gaussian import IntensityCalibration


def region_statistics(signal, spacing, config, noise_sigma):
    threshold = max(config["min_signal"], config["noise_multiplier"]*noise_sigma)
    smoothed = ndimage.gaussian_filter(signal.astype(np.float32),
        sigma=config["smoothing_um"]/np.asarray(spacing), mode="nearest")
    labels, count = ndimage.label(smoothed > threshold)
    sizes = np.bincount(labels.ravel())[1:]
    small = sizes < config["min_voxels"]
    large = sizes > config["max_voxels"]
    return {"threshold":float(threshold), "connected_regions":int(count),
            "accepted":int((~small & ~large).sum()),
            "too_small":int(small.sum()), "too_large":int(large.sum()),
            "largest_region_voxels":int(sizes.max()) if len(sizes) else 0,
            "foreground_fraction":float(sizes.sum()/signal.size),
            "oversize_foreground_fraction":float(sizes[large].sum()/max(1,sizes.sum()))}


def main():
    folder = Path("runs/mskcc-phase3-refined/photon_adaptive")
    config = json.loads((folder/"config.json").read_text())
    if config["sequence_id"] != "mskcc_confocal_s1" or config["split"] != "development":
        raise ValueError("Development sequence only")
    state = json.loads((folder/"state.json").read_text())
    observed = {row["t"]:row["detection"] for row in state["observations"]}
    panel = [0,66,132,193,260]
    if not set(panel) <= set(config["acquired_indices"]):
        raise ValueError("Panel must contain acquired frames only")
    calibration = IntensityCalibration(**state["normalization"])
    rows = []
    for t in panel:
        path = Path(f"data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1/images/mskcc_confocal_s1_t{t:03d}.tif")
        raw = tifffile.imread(path, maxworkers=1)
        signal = calibration.normalize(raw, clip=False)
        result = region_statistics(signal, state["spacing_um"], state["fit_config"], calibration.noise_sigma)
        if (result["connected_regions"] != observed[t]["connected_regions"] or
            result["accepted"] != observed[t]["accepted"] or
            result["too_small"]+result["too_large"] != observed[t]["rejected_size"]):
            raise ValueError(f"Diagnostic does not reproduce saved detector counts at {t}")
        row = {"t":t, "image_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
               "raw_percentiles_50_95_99_9999":np.percentile(raw,[50,95,99,99.99]).tolist(), **result}
        rows.append(row)
        print(json.dumps(row), flush=True)
        del raw, signal
    result = {"scope":"development-only acquired-image diagnostic, not segmentation accuracy",
              "panel":panel, "baseline_counts_reproduced":True,
              "fit_config":state["fit_config"], "normalization":state["normalization"],
              "source_sha256":{str(folder/name):hashlib.sha256((folder/name).read_bytes()).hexdigest()
                               for name in ["config.json","state.json"]}, "rows":rows}
    output = Path("runs/perception-region-audit/summary.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")


if __name__ == "__main__":
    main()
