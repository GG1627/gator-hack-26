"""Offline annotation audit; never imported by policy or replay driver."""
from collections import Counter
from pathlib import Path


def audit_lineage(path, frame_count):
    path = Path(path)
    if not path.exists():
        return {"available": False, "reason": "No gold TRA/man_track.txt"}
    rows = {}
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            label, begin, end, parent = map(int, line.split())
        except ValueError as exc:
            raise ValueError(f"Invalid lineage row {path}:{number}") from exc
        if label <= 0 or label in rows or not 0 <= begin <= end < frame_count or parent < 0:
            raise ValueError(f"Invalid lineage values {path}:{number}")
        rows[label] = (begin, end, parent)
    children = Counter()
    for label, (begin, end, parent) in rows.items():
        if parent:
            if parent not in rows or rows[parent][1] != begin-1:
                raise ValueError(f"Missing/nonconsecutive parent for track {label}")
            children[parent] += 1
    return {"available": True, "tracks": len(rows), "root_tracks": sum(p == 0 for _, _, p in rows.values()),
            "child_tracks": sum(children.values()), "binary_divisions": sum(n == 2 for n in children.values()),
            "nonbinary_parents": {str(p): n for p, n in children.items() if n != 2},
            "division_times": sorted(rows[p][1]+1 for p, n in children.items() if n == 2),
            "definition": "Binary division = a parent with exactly two children beginning one frame after parent end; not a detection score"}
