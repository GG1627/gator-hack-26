"""Synthetic fixture export or causal microscopy baseline replay."""

import argparse
import json
from pathlib import Path

import numpy as np

from photon.synthetic import make_synthetic_clip


def main() -> None:
    parser = argparse.ArgumentParser(description="PHOTON: synthetic fixtures and causal microscopy acquisition replay.")
    parser.add_argument("--synthetic-output", type=Path, help="Write a labeled synthetic fixture as a compressed .npz file")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--sequence", type=Path, help="MSKCC sequence root (with images/) or CTC tNNN.tif directory")
    parser.add_argument("--dataset-id", default="MSKCC-CONFOCAL")
    parser.add_argument("--source", choices=["microscopy", "synthetic"], default="microscopy")
    parser.add_argument("--budget", type=int)
    parser.add_argument("--policy", choices=["fixed_interval", "seeded_random", "both", "photon_adaptive", "image_change", "all"], default="both")
    parser.add_argument("--min-gap", type=int, default=2, help="Adaptive policies: minimum inter-acquisition gap")
    parser.add_argument("--max-gap", type=int, default=12, help="Adaptive policies: maximum gap, including terminal coverage")
    from photon.adaptive import DEFAULT_CONTROLLER_VARIANT
    parser.add_argument("--controller-variant", choices=["original", "paced", "robust", "paced_robust"],
                        default=DEFAULT_CONTROLLER_VARIANT, help="PHOTON preset; image-change baseline retains its original configuration")
    parser.add_argument("--output", type=Path, help="New directory for generated run artifacts")
    args = parser.parse_args()
    if args.sequence is not None:
        if args.synthetic_output is not None or args.output is None or args.budget is None:
            parser.error("--sequence requires --budget and --output, and excludes --synthetic-output")
        from photon.data import load_sequence
        from photon.policy import ScheduledPolicy
        from photon.adaptive import AdaptivePolicy, ControllerConfig, controller_variant
        from photon.replay import run_replay
        try:
            sequence = load_sequence(args.sequence, dataset_id=args.dataset_id, source=args.source)
            names = (["fixed_interval", "seeded_random", "photon_adaptive", "image_change"] if args.policy == "all" else
                     ["fixed_interval", "seeded_random"] if args.policy == "both" else [args.policy])
            if args.output.exists():
                parser.error("--output already exists; choose a new directory")
            policies = [AdaptivePolicy(name, config=(controller_variant(args.controller_variant, min_gap=args.min_gap, max_gap=args.max_gap)
                                                     if name == "photon_adaptive" else ControllerConfig(min_gap=args.min_gap, max_gap=args.max_gap)))
                        if name in ("photon_adaptive", "image_change") else ScheduledPolicy(name) for name in names]
            # Validate every configuration before starting any comparison run.
            for policy in policies:
                policy.reset(sequence.metadata, args.budget, args.seed)
            records = [run_replay(sequence, policy, args.budget, args.seed, args.output/policy.name) for policy in policies]
            assert all(len(r.acquired_indices) == args.budget for r in records)
        except ValueError as exc:
            parser.error(str(exc))
        return
    if args.synthetic_output is None:
        parser.print_help()
        return
    if args.synthetic_output.suffix != ".npz":
        parser.error("--synthetic-output must end in .npz")
    if args.synthetic_output.exists():
        parser.error("output already exists; choose a new path")
    clip = make_synthetic_clip(args.seed)
    metadata = {"dataset_id": "synthetic-gaussian-test-v1", "source": "synthetic", "seed": args.seed, "shape": list(clip.shape), "split_index": 4, "purpose": "test fixture; not a benchmark"}
    args.synthetic_output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.synthetic_output, frames=clip, metadata=json.dumps(metadata))
    print(json.dumps({**metadata, "output": str(args.synthetic_output)}))
