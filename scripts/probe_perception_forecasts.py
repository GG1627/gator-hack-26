"""Bounded causal development probes, using three acquisitions per reset model.

These are sparse-history probes, not full saved-policy replays. The canonical
tracking module stays unchanged; a private module instance supplies the candidate
detector while reusing exactly the same tracking implementation.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

import numpy as np
import tifffile
import photon.tracking as baseline_tracking
from photon.gaussian import GaussianFitConfig
from experiments.perception.watershed import watershed_and_fit
from photon.schemas import ObservedFrame


def candidate_tracking_module():
    path = Path(baseline_tracking.__file__)
    name = "photon._perception_probe_tracking"
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    def detector(signal,spacing,noise_sigma,config):
        components,diagnostics,_ = watershed_and_fit(signal,spacing,noise_sigma,config)
        return components,diagnostics
    module.detect_and_fit = detector
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('runs/perception-forecast-probes'))
    args = parser.parse_args()
    folder = Path("runs/mskcc-phase3-refined/photon_adaptive")
    config = json.loads((folder/"config.json").read_text())
    state = json.loads((folder/"state.json").read_text())
    assert config["sequence_id"]=="mskcc_confocal_s1" and config["split"]=="development"
    candidate = candidate_tracking_module()
    assert candidate is not baseline_tracking
    assert candidate.detect_and_fit is not baseline_tracking.detect_and_fit
    windows = [(127,132),(188,193),(254,260)]
    for previous,current in windows:
        assert {0,previous,current}<=set(config["acquired_indices"])
    output = args.output
    if (output/"summary.json").exists():
        raise ValueError("Completed probe output exists; preserve its source provenance")
    output.mkdir(parents=True,exist_ok=True)
    rows = []
    hashes = {}
    def read(t):
        path = Path(f"data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1/images/mskcc_confocal_s1_t{t:03d}.tif")
        hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        return tifffile.imread(path,maxworkers=1)
    for previous,current in windows:
        models = {name:module.GaussianSceneModel(state["spacing_um"],
                    fit_config=GaussianFitConfig(**state["fit_config"]),
                    tracking_config=module.TrackingConfig(**state["tracking_config"]))
                  for name,module in [("baseline",baseline_tracking),("watershed",candidate)]}
        raw_hold = None
        for t in [0,previous,current]:
            pixels = read(t)
            for model in models.values():
                model.observe(ObservedFrame(t,pixels,"microscopy"))
            if t==current:
                raw_hold = models["baseline"].calibration.normalize(pixels)
        del pixels
        # Freeze every forecast before loading any future target image.
        predictions = {horizon:{name:model.predict(current+horizon) for name,model in models.items()}
                       for horizon in [1,3]}
        for horizon in [1,3]:
            target = current+horizon
            forecasts = predictions.pop(horizon)
            assert all(frame.based_on_indices==(0,previous,current) for frame in forecasts.values())
            truth = models["baseline"].calibration.normalize(read(target))
            def errors(prediction):
                delta = prediction-truth
                return {"mse":float(np.mean(delta**2,dtype=np.float64)),
                        "mae":float(np.mean(np.abs(delta),dtype=np.float64))}
            row = {"acquired_indices":[0,previous,current],"target":target,"horizon":horizon,
                   "raw_hold":errors(raw_hold),
                   **{name:errors(frame.pixels) for name,frame in forecasts.items()},
                   "components":{name:len(model.tracks) for name,model in models.items()}}
            rows.append(row)
            print(json.dumps(row),flush=True)
            del forecasts,truth
        del models,raw_hold
    sources = [Path(__file__),Path(baseline_tracking.__file__),
               Path("experiments/perception/watershed.py"),folder/"config.json",folder/"state.json"]
    result = {"scope":"development sparse-history forecast probes; not full policy evaluation",
              "windows":[[0,*window] for window in windows],"horizons":[1,3],
              "protocol":"identical calibration/tracker; forecasts generated before target reads; raw-hold comparator",
              "limitations":["Models reset for every window; intermediate saved acquisitions are omitted.",
                             "Selected development windows cannot establish generalization.",
                             "No acquisition decisions or biological outcomes evaluated."],
              "source_sha256":{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
              "image_sha256":hashes,"rows":rows}
    (output/"summary.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
