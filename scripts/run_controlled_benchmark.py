"""Bounded controlled comparison. Run with single-thread BLAS; no real-volume work."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from experiments.controlled.benchmark import make_clip, ControlledSequence, policies, run_closed, score


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--development",action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Choose a fresh output directory")
    args.output.mkdir(parents=True)
    start = time.monotonic()
    deadline = start+120
    seeds = [7,42] if args.development else [101,102,103,104,105,2026]
    sources = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
               for p in [Path(__file__),*sorted((ROOT/"experiments/controlled").glob("*.py"))]}
    protocol = {"scope":"controlled synthetic; not biological evidence", "seeds":seeds,"budget":40,
                "conditions":["precursor","abrupt","quiet"],"tolerance_frames":1,
                "source_sha256":sources,"hard_limit_seconds":120,"tuning_split":"development" if args.development else "held-out seeds",
                "primary_metric":"events within +/-1 source frame at equal capture budget",
                "fixed_phases":[0,1/3,2/3],"demo_seed":2026,"image_backend":"CPU analytic Gaussian forward model"}
    (args.output/"protocol.json").write_text(json.dumps(protocol,indent=2))
    rows=[]
    status="complete"
    try:
        for seed in seeds:
            for condition in protocol["conditions"]:
                clip, events, _ = make_clip(seed,condition)
                sequence = ControlledSequence(clip)
                # Close ALL policies before opening event labels for scoring.
                closed=[run_closed(sequence,p,40,seed,deadline) for p in policies()]
                for record in closed:
                    rows.append({"seed":seed,"condition":condition,"sequence_sha256":sequence.fingerprint,
                                 "events":events,"run":record,"metrics":score(record,clip,events)})
                print(f"seed={seed} {condition}: "+", ".join(f"{r['run']['policy']} {r['metrics']['covered_events']}/{len(events)}" for r in rows[-5:]),flush=True)
    except TimeoutError:
        status="time_limit_partial"
    result={"status":status,"elapsed_seconds":time.monotonic()-start,"protocol":protocol,"rows":rows}
    (args.output/"summary.json").write_text(json.dumps(result,indent=2))
    print(f"{status}: {len(rows)} comparisons in {result['elapsed_seconds']:.1f}s",flush=True)
    return 0 if status=="complete" else 2


if __name__=="__main__":
    raise SystemExit(main())
