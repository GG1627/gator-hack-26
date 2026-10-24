"""Offline-only MaMuT annotation import. Never called by a replay policy.

Parse the source temporal graph; do not infer identities from spatial proximity.
This does not provide segmentation truth or resolve TSV/XML position differences.
"""
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET


def audit_mamut(path: Path, frame_count: int) -> dict:
    path = Path(path)
    if not path.exists():
        return {"available": False, "reason": "MaMuT annotation file is missing"}
    if frame_count < 1:
        raise ValueError("frame_count must be positive")
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        raise ValueError(f"Cannot parse MaMuT annotations {path}: {exc}") from exc
    if root.tag != "TrackMate" or root.find("Model/AllSpots") is None:
        raise ValueError(f"Expected TrackMate/MaMuT graph in {path}")
    spots = {}
    try:
        for spot in root.findall("Model/AllSpots/SpotsInFrame/Spot"):
            sid = int(spot.attrib["ID"])
            t = int(spot.attrib["FRAME"])
            if sid < 0 or t < 0 or sid in spots:
                raise ValueError("Duplicate or negative spot ID/frame")
            spots[sid] = t
        if not spots:
            raise ValueError("No annotated spots")
        children, incoming = defaultdict(set), Counter()
        edge_set = set()
        for edge in root.findall("Model/AllTracks/Track/Edge"):
            a,b = int(edge.attrib["SPOT_SOURCE_ID"]), int(edge.attrib["SPOT_TARGET_ID"])
            if a not in spots or b not in spots:
                raise ValueError("Edge references missing spot")
            # TrackMate graph edges may be stored in either orientation.
            if spots[a] > spots[b]:
                a,b = b,a
            if spots[b] != spots[a]+1:
                raise ValueError("Parent-child edges must join consecutive source frames")
            if (a,b) in edge_set:
                raise ValueError("Duplicate graph edge")
            edge_set.add((a,b))
            children[a].add(b)
            incoming[b] += 1
        if any(count>1 for count in incoming.values()):
            raise ValueError("Merge nodes are not supported as biological lineage truth")
        if any(len(values)>2 for values in children.values()):
            raise ValueError("Nonbinary branching in lineage")
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid MaMuT lineage {path}: {exc}") from exc
    annotated_frames = set(spots.values())
    missing = sorted(set(range(frame_count))-annotated_frames)
    events = [{"mother_id":sid,"mother_frame":spots[sid],"daughter_frame":spots[next(iter(values))],
               "daughter_ids":sorted(values)} for sid,values in children.items()
              if len(values)==2 and spots[sid]<frame_count and all(spots[c]<frame_count for c in values)]
    events.sort(key=lambda event:(event["daughter_frame"],event["mother_id"]))
    return {"available":True,"canonical_format":"MaMuT XML temporal graph",
            "all_requested_frames_have_annotations":not missing,"missing_annotation_frames":missing,
            "window_inclusive":[0,frame_count-1],"source_spot_records":len(spots),
            "source_annotation_frame_range":[min(annotated_frames),max(annotated_frames)],
            "root_spots_in_source":sum(sid not in incoming for sid in spots),
            "binary_divisions":len(events),"division_times":[event["daughter_frame"] for event in events],
            "events":events,"definition":"Binary parent with two immediate children; event at first daughter frame; all nodes inside requested window",
            "spatial_accuracy_status":"deferred: known TSV/XML position differences; use temporal graph only"}
