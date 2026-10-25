"""Compare frozen fitting with an experimental splitter on acquired s1 frames.

Run with isolated optional dependencies on PYTHONPATH. This is in-sample image
fitting, not held-out forecasting, instance accuracy, or acquisition evaluation.
"""
from dataclasses import asdict
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import time
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

import numpy as np
from PIL import Image, ImageDraw
import tifffile
from photon.gaussian import IntensityCalibration, GaussianFitConfig, detect_and_fit, render_gaussians
from experiments.perception.watershed import WatershedConfig, watershed_and_fit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('runs/perception-watershed-panel'))
    args = parser.parse_args()
    folder = Path("runs/mskcc-phase3-refined/photon_adaptive")
    config = json.loads((folder/"config.json").read_text())
    assert config["sequence_id"]=="mskcc_confocal_s1" and config["split"]=="development"
    state = json.loads((folder/"state.json").read_text())
    panel = [0,66,132,193,260]
    assert set(panel)<=set(config["acquired_indices"])
    observed = {row["t"]:row["detection"] for row in state["observations"]}
    calibration = IntensityCalibration(**state["normalization"])
    fit = GaussianFitConfig(**state["fit_config"])
    seeds = WatershedConfig()
    output = args.output
    if (output/"summary.json").exists():
        raise ValueError("Completed panel output exists; preserve its source provenance")
    output.mkdir(parents=True,exist_ok=True)
    rows = []
    for t in panel:
        path = Path(f"data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1/images/mskcc_confocal_s1_t{t:03d}.tif")
        raw = tifffile.imread(path,maxworkers=1)
        signal = calibration.normalize(raw,clip=False)
        truth = np.clip(signal,0,1)
        strip = Image.new("RGB",(768,292),"#f7f6f1")
        draw = ImageDraw.Draw(strip)
        def tile(volume,column,title):
            projection = np.clip(volume.max(axis=0)*255,0,255).astype(np.uint8)
            strip.paste(Image.fromarray(projection).resize((256,256)),(column*256,0))
            draw.text((column*256+6,264),title,fill="#252a29")
        tile(truth,0,f"Acquired s1 t{t}")
        row = {"t":t,"image_sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
        for column,method in enumerate(["frozen_components","experimental_watershed"],1):
            start = time.perf_counter()
            if method=="frozen_components":
                components,diagnostics = detect_and_fit(signal,state["spacing_um"],calibration.noise_sigma,fit)
                assert diagnostics==observed[t],f"Baseline mismatch at {t}"
            else:
                components,diagnostics,labels = watershed_and_fit(signal,state["spacing_um"],calibration.noise_sigma,fit,seeds)
                del labels
            fitting_seconds = time.perf_counter()-start
            rendered = render_gaussians(signal.shape,components)
            error = rendered-truth
            row[method] = {"diagnostics":diagnostics,"in_sample_mse":float(np.mean(error**2,dtype=np.float64)),
                           "in_sample_mae":float(np.mean(np.abs(error),dtype=np.float64)),
                           "fitting_seconds_single_run":fitting_seconds}
            tile(rendered,column,f"{'Baseline' if column==1 else 'Watershed'} fit / {len(components)} components")
            del rendered,error,components
        strip.save(output/f"frame-{t:03d}.png")
        rows.append(row)
        print(json.dumps(row),flush=True)
        del raw,signal,truth
    sources = [folder/"config.json",folder/"state.json",Path(__file__),
               Path("experiments/perception/watershed.py"),Path("services/science/photon/gaussian.py")]
    result = {"scope":"development-only in-sample fitting; not forecasting or segmentation accuracy",
              "panel":panel,"seed_config":asdict(seeds),"fit_config":asdict(fit),
              "normalization":state["normalization"],
              "source_sha256":{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
              "versions":{p:importlib.metadata.version(p) for p in ["numpy","scipy","scikit-image"]},
              "timing_note":"Single runs concurrent with Phase5; timings are diagnostics, not benchmark claims.",
              "rows":rows}
    (output/"summary.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
