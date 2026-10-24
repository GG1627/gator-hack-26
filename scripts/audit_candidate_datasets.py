"""Offline candidate-data audit. Never import this into an acquisition policy."""
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from PIL import Image, ImageDraw
import tifffile


def audit_lfct(downloads, output):
    archive = downloads / "lfct-mcf10a-fld3-rfp.zip"
    xml = downloads / "lfct-mcf10a-fld3.xml"
    root = ET.parse(xml).getroot()
    spots = {int(s.attrib["ID"]): s.attrib for s in root.findall("Model/AllSpots/SpotsInFrame/Spot")}
    tracks = root.findall("Model/AllTracks/Track")
    filtered = {int(t.attrib["TRACK_ID"]) for t in root.findall("Model/FilteredTracks/TrackID")}
    outgoing = {}
    gaps = Counter()
    backwards = []
    for track in tracks:
        if int(track.attrib["TRACK_ID"]) not in filtered:
            continue
        for edge in track.findall("Edge"):
            a, b = int(edge.attrib["SPOT_SOURCE_ID"]), int(edge.attrib["SPOT_TARGET_ID"])
            fa, fb = int(spots[a]["FRAME"]), int(spots[b]["FRAME"])
            if fb < fa:
                a, b, fa, fb = b, a, fb, fa
            if fb <= fa:
                backwards.append([a, b])
            outgoing.setdefault(a, set()).add(b)
            gaps[fb-fa] += 1
    branches = [{"mother_frame": int(spots[a]["FRAME"]),
                 "daughter_frames": sorted(int(spots[b]["FRAME"]) for b in children)}
                for a, children in outgoing.items() if len(children) == 2]
    shapes, dtypes, compressions, names, samples = Counter(), Counter(), Counter(), [], {}
    with zipfile.ZipFile(archive) as z:
        names = sorted(n for n in z.namelist() if re.fullmatch(r"FLD_3/rfp_\d+\.tif", n))
        for number, name in enumerate(names):
            with tifffile.TiffFile(io.BytesIO(z.read(name))) as tif:
                shapes[str(tif.series[0].shape)] += 1
                dtypes[str(tif.series[0].dtype)] += 1
                compressions[str(tif.pages[0].compression)] += 1
                if number in (0, 100, 200, len(names)-1):
                    pixels = tif.asarray()
                    samples[number] = pixels
        indices = [int(re.search(r"rfp_(\d+)", n).group(1)) for n in names]
    canvas = Image.new("RGB", (400*len(samples), 320), "black")
    draw = ImageDraw.Draw(canvas)
    for col, (t, pixels) in enumerate(samples.items()):
        low, high = np.percentile(pixels, [1, 99.8])
        grayscale = np.clip((pixels.astype(float)-low)/max(high-low, 1)*255, 0, 255).astype(np.uint8)
        image = Image.fromarray(grayscale).convert("RGB").resize((400, 296))
        canvas.paste(image, (400*col, 24))
        draw.text((400*col+4, 4), f"EVAL ONLY: RFP t={t}, XML positions", fill="white")
        for spot in spots.values():
            if int(spot["FRAME"]) == t:
                x = float(spot["POSITION_X"])*400/pixels.shape[1]+400*col
                y = float(spot["POSITION_Y"])*296/pixels.shape[0]+24
                draw.ellipse((x-4, y-4, x+4, y+4), outline="lime")
    canvas.save(output/"lfct-alignment-eval-only.png")
    return {"zip_bytes": archive.stat().st_size, "zip_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "xml_sha256": hashlib.sha256(xml.read_bytes()).hexdigest(), "image_count": len(names),
            "filename_index_range": [min(indices), max(indices)], "filename_indices_contiguous": indices == list(range(min(indices), max(indices)+1)),
            "shapes": dict(shapes), "dtypes": dict(dtypes), "compression": dict(compressions),
            "xml_image_metadata": {k:v for k,v in root.find("Settings/ImageData").attrib.items() if k != "folder"},
            "xml_model_units": root.find("Model").attrib,
            "spots": len(spots), "spot_frame_range": [min(int(s["FRAME"]) for s in spots.values()), max(int(s["FRAME"]) for s in spots.values())],
            "tracks": len(tracks), "filtered_tracks": len(filtered),
            "filtered_binary_branch_points": len(branches), "branch_points": sorted(branches, key=lambda b:b["mother_frame"]),
            "edge_frame_gaps": dict(gaps), "nonforward_edges": backwards,
            "warning": "Binary branch points are candidate annotated mitoses, not independently validated biological events. XML time interval is uncalibrated; use source frame indices until cadence verified."}


def audit_figshare(downloads):
    archive = downloads/"division-tracking-figshare.zip"
    results = {}
    with zipfile.ZipFile(archive) as z:
        image_fingerprints = {}
        for section in ("Division Detection", "Tracking"):
            groups = {}
            for name in z.namelist():
                if name.startswith("__MACOSX/") or f"/{section}/" not in name or not re.search(r"/img_t=\d+_ch=\d+\.tif$", name):
                    continue
                groups.setdefault(name.rsplit("/", 1)[0], []).append(name)
            for folder, names in groups.items():
                digest = hashlib.sha256()
                for name in sorted(names):
                    digest.update(name.rsplit("/", 1)[-1].encode())
                    with tifffile.TiffFile(io.BytesIO(z.read(name))) as tif:
                        pixels = tif.asarray()
                    digest.update(str((pixels.shape, pixels.dtype)).encode())
                    digest.update(pixels.tobytes())
                image_fingerprints[folder] = digest.hexdigest()
        for name in z.namelist():
            if name.startswith("__MACOSX/") or not name.endswith("divisions_annotations.csv"):
                continue
            rows = list(csv.reader(io.StringIO(z.read(name).decode("utf-8-sig"))))
            folder = name.rsplit("/", 1)[0]
            image_names = sorted(n for n in z.namelist() if n.startswith(folder+"/img_t="))
            sample = image_names[0]
            with tifffile.TiffFile(io.BytesIO(z.read(sample))) as tif:
                shape, dtype = tif.series[0].shape, str(tif.series[0].dtype)
                pixels = tif.asarray()
            # These CSVs have no header: the first line is an event too.
            events = [list(map(float, row)) for row in rows if any(cell.strip() for cell in row)]
            if any(len(row) != 12 for row in events):
                raise ValueError(f"Expected 12 numeric columns: {name}")
            times = [int(row[i]) for row in events for i in (0, 4, 8)]
            results[folder.rsplit("/", 1)[-1]] = {
                "image_count_all_channels": len(image_names), "sample_shape": shape, "sample_dtype": dtype,
                "sample_range": [int(pixels.min()), int(pixels.max())],
                "csv_has_header": False, "csv_data_rows": len(events),
                "empty_rows_ignored": sum(not any(cell.strip() for cell in row) for row in rows),
                "event_frame_range": [min(times), max(times)] if times else None,
                "sample_event": events[0] if events else None}
    matches = {folder.rsplit("/", 1)[-1]: [candidate.rsplit("/", 1)[-1] for candidate, candidate_hash in image_fingerprints.items()
                if "/Division Detection/" in candidate and candidate_hash == digest]
               for folder, digest in image_fingerprints.items() if "/Tracking/" in folder}
    return {"archive_bytes": archive.stat().st_size, "md5": hashlib.md5(archive.read_bytes()).hexdigest(),
            "tracking_to_division_video_matches_by_all_raw_pixel_arrays": matches,
            "videos": results, "division_csv_rows_total": sum(v["csv_data_rows"] for v in results.values())}


if __name__ == "__main__":
    downloads = Path("data/downloads")
    output = Path("runs/candidate-audit")
    output.mkdir(parents=True, exist_ok=True)
    report = {"lfct": audit_lfct(downloads, output), "figshare": audit_figshare(downloads)}
    (output/"audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
