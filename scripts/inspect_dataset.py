"""Offline microscopy data/annotation audit; output never goes to policies."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path

from photon.audit import audit_lineage
from photon.data import load_sequence
from photon.data import MSKCC_ID
from photon.annotations import audit_mamut


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--dataset-id", default=MSKCC_ID)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = []
    for directory in sorted(args.root.iterdir()):
        if not directory.is_dir() or not (directory.name.isdigit() or directory.name.startswith("mskcc_confocal_s")):
            continue
        if args.dataset_id == MSKCC_ID and not (directory/"download-manifest.json").exists():
            continue  # Audit-cache samples are not a complete replay window.
        sequence = load_sequence(directory, dataset_id=args.dataset_id)
        gt = args.root / f"{directory.name}_GT"
        lineage = (audit_mamut(directory/"tracks/tracks_mamut.xml", sequence.metadata.frame_count)
                   if args.dataset_id == MSKCC_ID else audit_lineage(gt / "TRA/man_track.txt", sequence.metadata.frame_count))
        results.append({**asdict(sequence.metadata), "sequence_sha256": sequence.fingerprint,
                        "provenance":sequence.provenance,
                        "lineage": lineage, "tracking_mask_count": len(list((gt/"TRA").glob("man_track*.tif"))),
                        "segmentation_mask_count": len(list((gt/"SEG").glob("man_seg*.tif")))})
    if not results:
        parser.error("No complete microscopy sequence directories found")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
