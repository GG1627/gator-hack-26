"""Animate completed fixed/PHOTON runs using only each run's acquired images.

This offline artifact viewer never feeds pixels or completed traces to a policy.
Skipped steps display a held measured image, explicitly not a predicted frame.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from photon.data import load_sequence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=Path("runs/mskcc-phase3"))
    parser.add_argument("--sequence", type=Path, default=Path("data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1"))
    parser.add_argument("--output", type=Path, default=Path("runs/mskcc-phase3/replay.gif"))
    parser.add_argument("--fixed-name", default="fixed_interval", help="Completed fixed-run directory name")
    parser.add_argument("--adaptive-name", default="photon_adaptive", help="Completed adaptive-run directory name")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output exists; choose a new path")
    names = (args.fixed_name, args.adaptive_name)
    configs = [json.loads((args.runs / name / "config.json").read_text()) for name in names]
    traces = [[json.loads(line) for line in (args.runs / name / "decisions.jsonl").read_text().splitlines()] for name in names]
    sequence = load_sequence(args.sequence, dataset_id=configs[0]["dataset_id"], source=configs[0]["source"])
    total = sequence.metadata.frame_count
    for config, trace in zip(configs, traces):
        if (config["sequence_sha256"] != sequence.fingerprint or config["budget"] != configs[0]["budget"]
                or config["frame_count"] != total or len(trace) != total):
            parser.error("Comparison requires matching source, frame count and budgets")
        if [row["t"] for row in trace if row["decision"] == "ACQUIRE"] != config["acquired_indices"]:
            parser.error("Trace does not match declared acquisitions")
    # Decode only the union of recorded acquisitions, never any other source image.
    thumbnails = {}
    for t in sorted(set(configs[0]["acquired_indices"]) | set(configs[1]["acquired_indices"])):
        volume = sequence.read(t)
        image = volume.max(axis=0) if volume.ndim == 3 else volume
        lo, hi = float(image.min()), float(image.max())
        signal = np.clip((image.astype(np.float32) - lo) / max(hi-lo, 1), 0, 1)
        thumbnails[t] = Image.fromarray((signal*255).astype(np.uint8)).resize((320, 320))
    frames = []
    last = [0, 0]
    counts = [0, 0]
    synthetic = sequence.metadata.source == "synthetic"
    for t in range(total):
        canvas = Image.new("RGB", (680, 460), "black")
        draw = ImageDraw.Draw(canvas)
        draw.text((12, 5), f"COMPLETED {'SYNTHETIC' if synthetic else 'REAL'} REPLAY | source frame {t}/{total-1} | equal budget {configs[0]['budget']}", fill="white")
        for column, (config, trace) in enumerate(zip(configs, traces)):
            x = 10 + column*340
            captured = trace[t]["decision"] == "ACQUIRE"
            if captured:
                last[column] = t
                counts[column] += 1
            canvas.paste(thumbnails[last[column]], (x, 55))
            color = (80, 210, 190) if column else (180, 180, 180)
            draw.text((x, 24), f"{names[column]}: {counts[column]}/{config['budget']}", fill=color)
            label = "SYNTHETIC" if synthetic else "MEASURED"
            draw.text((x, 39), f"{label} t={last[column]}" + (" | ACQUIRED NOW" if captured else " | held display"), fill="white")
            draw.rectangle((x, 55, x+319, 374), outline=color if captured else (60, 60, 60), width=2)
            draw.line((x, 393, x+319, 393), fill=(70, 70, 70))
            for index in config["acquired_indices"]:
                at = x + round(index / max(1, total-1)*319)
                draw.line((at, 387, at, 399), fill=color if index <= t else (45, 45, 45))
            cursor = x + round(t / max(1, total-1)*319)
            draw.ellipse((cursor-3, 390, cursor+3, 396), fill="white")
            reason = trace[t]["reason"]
            draw.text((x, 406), reason, fill="white")
            if column:
                draw.text((x, 421), f"priority={trace[t]['score']:.3f} (heuristic)", fill=color)
        draw.text((12, 443), "Skipped steps hold past measurements. No truth reveal or accuracy claim. Display-only scaling.", fill=(170, 170, 170))
        frames.append(canvas)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    durations = [80] * total
    durations[-1] = 1200
    frames[0].save(args.output, save_all=True, append_images=frames[1:], duration=durations, loop=0)
    preview_index = next((t for t in range(1, total) if traces[0][t]["decision"] != traces[1][t]["decision"]), 0)
    frames[preview_index].save(args.output.with_suffix(".png"))
    manifest = {"source_sha256": sequence.fingerprint, "policies": names, "budget": configs[0]["budget"],
                "frame_count": total, "image_read_indices": sorted(thumbnails),
                "display": "only previously acquired images per policy, held between acquisitions",
                "scaling": "per-acquired-image min/max, display only", "preview_index": preview_index}
    args.output.with_suffix(".json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Saved {total}-step completed-run animation to {args.output}")


if __name__ == "__main__":
    main()
