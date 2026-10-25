"""Evaluate registered appearance correction using sealed causal scene archives."""
import argparse
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from PIL import Image, ImageDraw
import tifffile
from photon.development import load_scenes
from photon.gaussian import IntensityCalibration, render_gaussians
from photon.schemas import ObservedFrame, PredictedFrame
from experiments.forecasting.appearance import appearance_forecast
from scripts.run_perception_ablation import digest, write_json

TARGETS=(133,135,194,196,261,263)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,default=ROOT/"runs/perception-controller-ablation")
    parser.add_argument("--output",type=Path,default=ROOT/"runs/appearance-forecast-probe")
    args=parser.parse_args();source=args.input.resolve();output=args.output.resolve()
    status=json.loads((source/"status.json").read_text());verification=json.loads((source/"verification.json").read_text())
    if status["state"]!="complete" or not verification.get("verified") or digest(source/"summary.json")!=verification["summary_sha256"]:
        raise ValueError("The input acquisition ablation must finish and pass ledger verification")
    for path,expected in verification["closed_artifact_sha256"].items():
        if digest(source/path)!=expected: raise ValueError("Input causal archive changed")
    if output.exists(): raise ValueError("Probe output exists; preserve its provenance")
    output.mkdir(parents=True)
    paths=[Path(__file__),ROOT/"experiments/forecasting/appearance.py",ROOT/"experiments/forecasting/__init__.py",
           ROOT/"docs/APPEARANCE_FORECAST_PLAN.md",ROOT/"tests/test_appearance_forecast.py",
           ROOT/"services/science/photon/gaussian.py",ROOT/"services/science/photon/schemas.py",
           ROOT/"services/science/photon/development.py"]
    protocol={"scope":"previously inspected development s1; selected forecast probe only", "targets":TARGETS,
        "methods":["adaptive","watershed"],"mixing_weight":1,"input_summary_sha256":verification["summary_sha256"],
        "input_verification_sha256":digest(source/"verification.json"),
        "source_sha256":{str(path.relative_to(ROOT)):digest(path) for path in paths},
        "rule":"retain every eligible per-policy outcome; cross-policy table uses targets withheld by both; no replacements"}
    write_json(output/"protocol.json",protocol)
    with zipfile.ZipFile(output/"source.zip","w",zipfile.ZIP_DEFLATED) as archive:
        for path in paths: archive.write(path,path.relative_to(ROOT))
        archive.write(output/"protocol.json","experiment-protocol.json")
    write_json(output/"registration.json",{"protocol_sha256":digest(output/"protocol.json"),"source_zip_sha256":digest(output/"source.zip"),"outcomes_computed_at_registration":False})
    methods={}
    for name in protocol["methods"]:
        folder=source/name;config=json.loads((folder/"config.json").read_text())
        if config["sequence_id"]!="mskcc_confocal_s1": raise ValueError("Development s1 only")
        methods[name]={"config":config,"calibration":IntensityCalibration(**config["normalization"]),
            "held":load_scenes(folder/"held_scenes.npz"),"forecasts":load_scenes(folder/"forecasts.npz"),
            "trace":{row["t"]:row for row in map(json.loads,(folder/"decisions.jsonl").read_text().splitlines())}}
    image_hashes={}
    def read(t):
        path=ROOT/f"data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1/images/mskcc_confocal_s1_t{t:03d}.tif"
        image_hashes[str(path.relative_to(ROOT))]=digest(path)
        return tifffile.imread(path,maxworkers=1)
    rows=[];exclusions=[]
    for target in TARGETS:
        estimates={}
        for name,value in methods.items():
            if target in value["config"]["acquired_indices"]:
                exclusions.append({"method":name,"target":target,"reason":"acquired by this policy; not a withheld target"});continue
            history=tuple(t for t in value["config"]["acquired_indices"] if t<target);last=history[-1]
            calibration=value["calibration"];observed=ObservedFrame(last,read(last),"microscopy")
            sigma=value["trace"][target]["uncertainty_um"]
            process=value["config"]["tracking_config"]["process_sigma_um_per_frame"]
            base_sigma=float(np.sqrt(max(0,sigma*sigma-((target-last)*process)**2)))
            fit=PredictedFrame(last,render_gaussians(observed.pixels.shape,value["held"][last]),history,base_sigma,
                normalization=calibration.to_dict())
            forecast=PredictedFrame(target,render_gaussians(observed.pixels.shape,value["forecasts"][target]),history,sigma,
                normalization=calibration.to_dict())
            corrected=appearance_forecast(observed,fit,forecast,calibration)
            estimates[name]={"raw_hold":calibration.normalize(observed.pixels),"gaussian_forecast":forecast.pixels,
                             "appearance_corrected":corrected.pixels,"last":last,"history":history}
            del observed,fit,forecast,corrected
        if not estimates: continue
        # Neither prediction function receives this target image.
        truth=next(iter(methods.values()))["calibration"].normalize(read(target))
        for name,value in estimates.items():
            scores={}
            strip=Image.new("RGB",(1024,294),"#f7f6f1");draw=ImageDraw.Draw(strip)
            for column,key in enumerate(["raw_hold","gaussian_forecast","appearance_corrected"]):
                error=np.subtract(value[key],truth,dtype=np.float64)
                scores[key]={"mse":float(np.mean(error*error)),"mae":float(np.mean(np.abs(error)))}
                mip=np.round(np.clip(value[key].max(axis=0),0,1)*255).astype(np.uint8)
                strip.paste(Image.fromarray(mip).resize((256,256)),(column*256,0));draw.text((column*256+6,264),key.replace('_',' '),fill="#252a29")
                del error
            mip=np.round(truth.max(axis=0)*255).astype(np.uint8)
            strip.paste(Image.fromarray(mip).resize((256,256)),(768,0));draw.text((774,264),f"GROUND TRUTH / eval only / t{target}",fill="#252a29")
            strip.save(output/f"{name}-t{target}.png")
            row={"method":name,"target":target,"last_acquired":value["last"],"horizon":target-value["last"],
                 "based_on_indices":value["history"],"common_target":len(estimates)==len(methods),"scores":scores}
            rows.append(row);print(json.dumps(row),flush=True)
        del estimates,truth
    if any(digest(ROOT/path)!=expected for path,expected in protocol["source_sha256"].items()):
        raise ValueError("Probe source changed during evaluation")
    write_json(output/"summary.json",{"protocol":protocol,"protocol_sha256":digest(output/"protocol.json"),
        "image_sha256":image_hashes,"rows":rows,"exclusions":exclusions,
        "limitations":["Selected previously inspected development targets, not an overall benchmark.",
                       "No controller or acquisition changes; residual texture is held rather than transported.",
                       "Inherited position uncertainty remains heuristic and is not image-error calibration."]})


if __name__=="__main__": main()
