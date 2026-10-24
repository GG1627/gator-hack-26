"""Audit author-hosted MSKCC data using verified HTTP ranges, without a 26GB download.

Offline evaluation only. No frames or annotations from this tool enter a policy.
"""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import io
import json
from pathlib import Path, PurePosixPath
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from PIL import Image, ImageDraw
import tifffile


URL = "https://zenodo.org/records/6460303/files/mskcc_confocal.zip"
SIZE = 26141247410


class RangeReader(io.RawIOBase):
    def __init__(self, url=URL, size=SIZE):
        self.url, self.size, self.position = url, size, 0
        self.transferred = 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        position = offset if whence == 0 else self.position+offset if whence == 1 else self.size+offset
        if position < 0:
            raise ValueError("Negative file position")
        self.position = position
        return position

    def read(self, size=-1):
        start = self.position
        count = self.size-start if size < 0 else min(size, self.size-start)
        if count <= 0:
            return b""
        end = start+count-1
        request = urllib.request.Request(self.url, headers={"Range": f"bytes={start}-{end}"})
        with urllib.request.urlopen(request, timeout=45) as response:
            expected = f"bytes {start}-{end}/{self.size}"
            if response.status != 206 or response.headers.get("Content-Range") != expected:
                raise ValueError(f"Server did not honor requested range {expected}: {response.status}, {response.headers.get('Content-Range')}")
            data = response.read(count+1)
        if len(data) != count:
            raise ValueError("Incomplete or excessive HTTP range response")
        self.position += count
        self.transferred += count
        return data

    def readinto(self, buffer):
        view = memoryview(buffer).cast("B")
        payload = self.read(len(view))
        view[:len(payload)] = payload
        return len(payload)


def cached_entry(z, name, cache):
    relative = PurePosixPath(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Unsafe ZIP path")
    path = cache.joinpath(*relative.parts)
    if path.exists():
        # Check cached content against the archive CRC, not just file size.
        import zlib
        payload = path.read_bytes()
        if len(payload) == z.getinfo(name).file_size and zlib.crc32(payload) == z.getinfo(name).CRC:
            return path
        raise ValueError(f"Cached file fails ZIP integrity check: {path}")
    if z.getinfo(name).file_size > 150_000_000:
        raise ValueError(f"Entry too large for focused audit: {name}")
    print(f"Fetching {name} ({z.getinfo(name).file_size} bytes)", flush=True)
    payload = z.read(name)  # zipfile verifies the entry CRC during decompression.
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix+".part")
    temporary.write_bytes(payload)
    temporary.replace(path)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory-only", action="store_true")
    args = parser.parse_args()
    output = Path("runs/mskcc-audit")
    output.mkdir(parents=True, exist_ok=True)
    reader = RangeReader()
    with zipfile.ZipFile(reader) as z:
        inventory = [{"name": f.filename, "bytes": f.file_size, "compressed_bytes": f.compress_size,
                      "crc32": f"{f.CRC:08x}"} for f in z.infolist() if not f.is_dir()]
        (output/"inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")
        print(json.dumps({"files": len(inventory), "transferred_bytes": reader.transferred,
                          "annotation_files": [f for f in inventory if f["name"].endswith((".xml", ".csv", ".md", ".txt"))]}, indent=2), flush=True)
        if args.inventory_only:
            return
        audit(z, Path("data/mskcc-audit"), output)
    (output/"transfer.json").write_text(json.dumps({"bytes_transferred_this_run": reader.transferred,
        "completed_local_time": datetime.now().astimezone().isoformat()}, indent=2), encoding="utf-8")


def audit(z, cache, output):
    reports = {}
    for sequence in ("mskcc_confocal_s1", "mskcc_confocal_s2", "mskcc_confocal_s3"):
        prefix = f"mskcc-confocal/{sequence}"
        names = sorted(n for n in z.namelist() if n.startswith(prefix+"/images/") and n.endswith(".tif"))
        indices = [int(Path(n).stem.rsplit("t", 1)[-1]) for n in names]
        if indices != list(range(400)):
            raise ValueError(f"Image inventory not contiguous: {sequence}")
        txt = cached_entry(z, prefix+"/tracks/tracks.txt", cache)
        with txt.open(newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        spots = {int(row["cell_id"]): row for row in rows}
        if len(spots) != len(rows):
            raise ValueError("Duplicate annotation IDs")
        outgoing = defaultdict(list)
        gaps, missing = Counter(), []
        for row in rows:
            parent = int(row["parent_id"])
            if parent < 0:
                continue
            if parent not in spots:
                missing.append(parent)
                continue
            outgoing[parent].append(int(row["cell_id"]))
            gaps[int(row["t"])-int(spots[parent]["t"])] += 1
        branches = {parent: children for parent, children in outgoing.items() if len(children) == 2}
        events = [{"mother_frame": int(spots[p]["t"]),
                   "daughter_frames": sorted(int(spots[c]["t"]) for c in cs),
                   "mother_id": p} for p, cs in branches.items()]
        early = [e for e in events if e["mother_frame"] < 270 and max(e["daughter_frames"]) < 270]
        counts = Counter(int(row["t"]) for row in rows)
        report = {"image_inventory_count": len(names), "spots": len(rows),
                  "annotation_frame_range": [min(counts), max(counts)],
                  "missing_annotation_frames": [t for t in range(400) if t not in counts],
                  "root_spots": sum(int(row["parent_id"]) < 0 for row in rows),
                  "track_id_count": len({row["track_id"] for row in rows}),
                  "missing_parent_ids": missing, "edge_frame_gaps": dict(gaps),
                  "nonbinary_parents": {str(p): len(cs) for p,cs in outgoing.items() if len(cs)>2},
                  "binary_branches_all": len(events), "binary_branches_first270": len(early),
                  "events": sorted(events, key=lambda e:e["mother_frame"]),
                  "annotation_count_at_sample_times": {str(t):counts[t] for t in (0,89,179,269,399)},
                  "volumes": []}
        # Cross-check the convenient TSV against the separately provided MaMuT XML.
        xml = cached_entry(z, prefix+"/tracks/tracks_mamut.xml", cache)
        root = ET.parse(xml).getroot()
        report["xml_root"] = root.tag
        report["xml_model_units"] = root.find("Model").attrib
        report["xml_image_data"] = root.find("Settings/ImageData").attrib
        xml_spots = {int(s.get("ID")): s.attrib for s in root.iter("Spot")}
        xml_edges = set()
        for edge in root.iter("Edge"):
            a,b = int(edge.get("SPOT_SOURCE_ID")),int(edge.get("SPOT_TARGET_ID"))
            if int(xml_spots[a]["FRAME"]) > int(xml_spots[b]["FRAME"]):
                a,b = b,a
            xml_edges.add((a,b))
        csv_edges = {(int(row["parent_id"]),int(row["cell_id"])) for row in rows if int(row["parent_id"])>=0}
        mismatch = [cell_id for cell_id,row in spots.items() if cell_id not in xml_spots or any(
            abs(float(row[column])-float(xml_spots[cell_id][attribute]))>1e-6
            for column,attribute in (("t","FRAME"),("x","POSITION_X"),("y","POSITION_Y"),("z","POSITION_Z")))]
        report["xml_csv_crosscheck"] = {"csv_spot_ids_missing_or_coordinate_mismatch":len(mismatch),
            "edge_symmetric_difference":len(xml_edges.symmetric_difference(csv_edges)),
            "xml_spots":len(xml_spots),"xml_edges":len(xml_edges)}
        missing_ids = set(spots).symmetric_difference(xml_spots)
        frame_mismatch = [i for i,row in spots.items() if i in xml_spots and int(row["t"]) != int(xml_spots[i]["FRAME"])]
        spatial_mismatch = [i for i in mismatch if i in xml_spots and i not in frame_mismatch]
        crosscheck = report["xml_csv_crosscheck"]
        crosscheck.update({"missing_ids":len(missing_ids),"frame_mismatches":len(frame_mismatch),
            "spatial_mismatches":len(spatial_mismatch),
            "spatial_mismatches_first270":sum(int(spots[i]["t"])<270 for i in spatial_mismatch),
            "max_spatial_delta_xy_pixel_units":max((float(np.linalg.norm([
                float(spots[i][column])-float(xml_spots[i][attribute]) for column,attribute in (
                    ("x","POSITION_X"),("y","POSITION_Y"),("z","POSITION_Z"))])) for i in spatial_mismatch), default=0),
            "note":"Spatial disagreement does not change event times when IDs, frames and edges agree. Defer spatial accuracy metrics until a canonical annotation representation is documented."})
        if missing_ids or frame_mismatch or xml_edges != csv_edges:
            raise ValueError(f"{sequence} CSV/XML temporal graphs disagree; investigate before trusting events")
        calibration = report["xml_image_data"]
        z_scale = float(calibration["voxeldepth"])/float(calibration["pixelwidth"])
        report["csv_z_units_per_slice"] = z_scale
        report["branch_parent_div_state_disagreements"] = sum(spots[p]["div_state"] != "1" for p in branches)
        sheet = Image.new("RGB", (320*5, 344), "black")
        draw = ImageDraw.Draw(sheet)
        for col, t in enumerate((0,89,179,269,399)):
            path = cached_entry(z, names[t], cache)
            with tifffile.TiffFile(path) as tif:
                pixels = tif.asarray()
                tags = {tag.name: str(tag.value)[:2000] for tag in tif.pages[0].tags.values()
                        if tag.name in ("ImageDescription", "Software", "XResolution", "YResolution", "ResolutionUnit", "DateTime")}
            if pixels.shape != (41,512,512) or pixels.dtype != np.uint16:
                raise ValueError(f"Unexpected volume shape/dtype: {path}")
            # CSV z is in XY pixel-size units (0.15um), so five units per slice.
            frame_spots = [row for row in rows if int(row["t"]) == t]
            bad = [int(row["cell_id"]) for row in frame_spots if not (
                0 <= float(row["x"]) < 512 and 0 <= float(row["y"]) < 512 and 0 <= float(row["z"])/z_scale < 41)]
            report["volumes"].append({"frame":t,"shape":list(pixels.shape),"dtype":str(pixels.dtype),
                "min":int(pixels.min()),"max":int(pixels.max()),
                "percentiles":np.percentile(pixels,[1,50,99,99.9]).tolist(),
                "fraction_uint16_max":float(np.mean(pixels==65535)),
                "out_of_bounds_spots_under_z_div5":bad, "tags":tags})
            mip = pixels.max(axis=0)
            low, high = np.percentile(mip,[1,99.8])
            preview = np.clip((mip.astype(float)-low)/max(high-low,1)*255,0,255).astype(np.uint8)
            sheet.paste(Image.fromarray(preview).convert("RGB").resize((320,320)),(320*col,24))
            draw.text((320*col+4,4),f"EVAL ONLY {sequence[-2:]} t={t}",fill="white")
            for row in frame_spots:
                x,y = float(row["x"])*320/512+320*col, float(row["y"])*320/512+24
                draw.ellipse((x-2,y-2,x+2,y+2),outline="lime")
            print(f"Validated {sequence} t={t}: {pixels.shape}, {len(frame_spots)} labels",flush=True)
        sheet.save(output/f"{sequence}-alignment.png")
        reports[sequence] = report
        (output/"audit.json").write_text(json.dumps(reports,indent=2),encoding="utf-8")
        print(f"{sequence}: {len(rows)} spots, {len(events)} binary branches, {len(early)} fully within first270",flush=True)


if __name__ == "__main__":
    main()
