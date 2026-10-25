"""Cheap, offline development diagnostic; no images, inference, or policy updates.

Counts cannot establish segmentation accuracy: components are intensity regions,
and annotation spots are not masks. Spatial matching is deliberately excluded.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics
import xml.etree.ElementTree as ET


def audit(config, state, root):
    if config.get("sequence_id") != "mskcc_confocal_s1" or config.get("split") != "development":
        raise ValueError("This diagnostic is restricted to the s1 development sequence")
    observations = state["observations"]
    times = [entry["t"] for entry in observations]
    if times != config["acquired_indices"] or len(set(times)) != len(times):
        raise ValueError("Observation times must exactly match the saved acquisition schedule")
    spots = root.findall("Model/AllSpots/SpotsInFrame/Spot")
    ids = [spot.attrib["ID"] for spot in spots]
    if not spots or len(set(ids)) != len(ids):
        raise ValueError("Missing spots or duplicate annotation IDs")
    counts = Counter(int(spot.attrib["FRAME"]) for spot in spots)
    if any(counts[t] == 0 for t in times):
        raise ValueError("Missing annotation frame; cannot interpret absence as zero cells")
    rows = [{"source_frame":entry["t"], "annotated_spots":counts[entry["t"]],
             "accepted_components":entry["detection"]["accepted"],
             "connected_regions":entry["detection"]["connected_regions"],
             "rejected_by_size":entry["detection"]["rejected_size"],
             "active_tracks_after_observation":entry["active_tracks"]}
            for entry in observations]
    for row in rows:
        row["component_to_spot_ratio"] = row["accepted_components"] / row["annotated_spots"]
    return {"sequence":config["sequence_id"], "scope":"development-only offline count diagnostic",
            "observations":len(rows), "median_component_to_spot_ratio":statistics.median(
                row["component_to_spot_ratio"] for row in rows),
            "fewer_components_than_spots":sum(row["accepted_components"] < row["annotated_spots"] for row in rows),
            "more_components_than_spots":sum(row["accepted_components"] > row["annotated_spots"] for row in rows),
            "limitations":["Count agreement is not segmentation accuracy or recall.",
                           "Mismatch does not distinguish merging, fragmentation, missed signal, or annotation coverage.",
                           "No spatial matching: known TSV/XML position differences remain unresolved.",
                           "This does not measure whether a new segmenter improves acquisition."],
            "rows":rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=Path("runs/mskcc-phase3-refined/photon_adaptive"))
    parser.add_argument("--annotations", type=Path, default=Path("data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1/tracks/tracks_mamut.xml"))
    parser.add_argument("--output", type=Path, default=Path("runs/perception-count-audit/summary.json"))
    args = parser.parse_args()
    paths = [args.run/"config.json", args.run/"state.json", args.annotations]
    result = audit(json.loads(paths[0].read_text()), json.loads(paths[1].read_text()), ET.parse(paths[2]).getroot())
    result["source_sha256"] = {path.as_posix():hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({key:value for key,value in result.items() if key not in {"rows","source_sha256"}}, indent=2))


if __name__ == "__main__":
    main()
