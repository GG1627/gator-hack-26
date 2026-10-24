"""Phase2 real-data Gaussian prediction preview; ground truth revealed only after replay."""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
import scipy

from photon.data import load_sequence
from photon.gaussian import render_gaussians
from photon.oracle import ReplayOracle
from photon.replay import RunRecord
from photon.tracking import GaussianSceneModel


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sequence",type=Path,default=Path("data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1"))
    parser.add_argument("--observed",type=int,nargs="+",default=[0,5,10])
    parser.add_argument("--target",type=int,default=12)
    parser.add_argument("--output",type=Path,default=Path("runs/mskcc-phase2"))
    args=parser.parse_args()
    if args.output.exists():
        parser.error("Output exists; choose a new directory")
    if not args.observed or args.observed[0]!=0 or args.observed!=sorted(set(args.observed)) or args.observed[-1]>=args.target:
        parser.error("Use increasing unique observed indices starting at0, all before target")
    sequence=load_sequence(args.sequence,dataset_id="MSKCC-CONFOCAL")
    if not 0<args.target<sequence.metadata.frame_count:
        parser.error("Target must be a withheld index within source window")
    spacing=sequence.metadata.voxel_size_xyz_um[::-1]
    model=GaussianSceneModel(spacing)
    oracle=ReplayOracle(sequence,len(args.observed))
    decisions=[]
    acquired=[]
    prediction=None
    reconstruction=None
    for t in range(sequence.metadata.frame_count):
        oracle.advance(t)
        if t in args.observed:
            frame=oracle.acquire(t)
            model.observe(frame)
            acquired.append(frame)
            print(f"Acquired t={t}: {model.observation_log[-1]['active_tracks']} Gaussian tracks; {model.observation_log[-1]['detection']}",flush=True)
        if t==args.target:
            prediction=model.predict(t,include_uncertainty_map=True)
            reconstruction=render_gaussians(model.shape,model.scene_at(model.last_observed))
            print(f"Predicted t={t} using {list(prediction.based_on_indices)}; uncertainty={prediction.uncertainty:.6f}um (heuristic)",flush=True)
        decisions.append({"t":t,"decision":"ACQUIRE" if t in args.observed else "SKIP",
                          "remaining_budget":len(args.observed)-len(acquired),"reason":"predeclared Phase2 observation schedule, not adaptive"})
    indices=oracle.finish()
    record=RunRecord("phase2_predeclared_sparse",0,len(indices),indices,tuple(decisions))
    truth,metrics=oracle.evaluate_prediction_after_run(record,prediction,foreground_threshold=0.1)
    args.output.mkdir(parents=True)
    state=model.state_dict()
    code_hash=hashlib.sha256()
    for path in sorted(Path(__file__).resolve().parents[1].joinpath("services/science/photon").glob("*.py")):
        code_hash.update(path.name.encode())
        code_hash.update(path.read_bytes())
    config={**asdict(sequence.metadata),"provenance":sequence.provenance,"sequence_sha256":sequence.fingerprint,
            "policy":"phase2_predeclared_sparse","budget":len(indices),"acquired_indices":list(indices),"target":args.target,
            "seed":0,"seed_note":"deterministic model and +/-axis ensemble; no RNG", "model_version":state["model_version"],
            "fit_config":state["fit_config"],"tracking_config":state["tracking_config"],
            "foreground_threshold":0.1,"photon_code_sha256":code_hash.hexdigest(),"scipy_version":scipy.__version__,
            "numpy_version":np.__version__,"hardware":{"kernel_backend":"cpu","gpu":None},
            "scope":"single withheld development frame; full 3D computation, MIP previews; no adaptive policy comparison"}
    (args.output/"config.json").write_text(json.dumps(config,indent=2),encoding="utf-8")
    (args.output/"state.json").write_text(json.dumps(state,indent=2),encoding="utf-8")
    (args.output/"metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
    (args.output/"decisions.jsonl").write_text("".join(json.dumps(d)+"\n" for d in decisions),encoding="utf-8")
    np.savez_compressed(args.output/"prediction.npz",pixels=prediction.pixels,uncertainty_map=prediction.uncertainty_map,
                        kind=prediction.kind,based_on_indices=prediction.based_on_indices,uncertainty_um=prediction.uncertainty)
    np.savez_compressed(args.output/"evaluation_truth.npz",pixels=truth.pixels,kind=truth.kind)
    measured=model.calibration.normalize(acquired[-1].pixels)
    error=np.abs(prediction.pixels-truth.pixels)
    panels=[(f"MEASURED t={indices[-1]}",measured),
            (f"GAUSSIAN FIT t={indices[-1]} (in sample)",reconstruction),
            (f"PREDICTED t={args.target}",prediction.pixels),
            (f"GROUND TRUTH (EVAL ONLY) t={args.target}",truth.pixels),
            ("EVAL ONLY: MIP absolute voxel error",error),
            ("ENSEMBLE DISAGREEMENT x5 (heuristic)",prediction.uncertainty_map*5)]
    canvas=Image.new("RGB",(960,688),"black")
    draw=ImageDraw.Draw(canvas)
    for index,(label,volume) in enumerate(panels):
        mip=volume.max(axis=0)
        image=Image.fromarray((np.clip(mip,0,1)*255).astype(np.uint8)).resize((320,320))
        x,y=(index%3)*320,(index//3)*344
        canvas.paste(image,(x,y+24))
        draw.text((x+4,y+4),label,fill="white")
    canvas.save(args.output/"comparison.png")
    print(json.dumps(metrics,indent=2),flush=True)


if __name__=="__main__":
    main()
