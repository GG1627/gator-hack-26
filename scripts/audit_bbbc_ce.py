"""Focused, offline audit of user-suggested sources; no controller integration.

Requires optional h5py under .tools/dataset-audit-deps for remote HDF5 inspection.
The application and tests do not acquire this optional dependency.
"""
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

sys.path.insert(0,str(Path(".tools/dataset-audit-deps").resolve()))
import numpy as np
import tifffile

from audit_mskcc_dataset import RangeReader, cached_entry
from photon.audit import audit_lineage


def audit_bbbc(output):
    reader = RangeReader("https://data.broadinstitute.org/bbbc/BBBC035/BBBC035_v1_dataset.zip",3180529910)
    cache = Path("data/bbbc-audit")
    results = {}
    gt_path = Path("data/downloads/BBBC035_v1_DatasetGroundTruth.zip")
    with zipfile.ZipFile(reader) as z, zipfile.ZipFile(gt_path) as gt:
        if gt.testzip() is not None:
            raise ValueError("Ground-truth ZIP CRC validation failed")
        for sequence in ("01","02"):
            names = sorted(n for n in z.namelist() if re.fullmatch(sequence+r"/t\d+\.tif",n))
            indices = [int(Path(n).stem[1:]) for n in names]
            if indices != list(range(len(names))):
                raise ValueError("Non-contiguous synthetic sequence")
            track_path = cached_entry(gt,f"{sequence}_GT/TRA/man_track.txt",cache)
            lineage = audit_lineage(track_path,len(names))
            samples = []
            for t in (0,len(names)//2,len(names)-1):
                raw_path = cached_entry(z,names[t],cache)
                mask_path = cached_entry(gt,f"{sequence}_GT/SEG/man_seg{t:03}.tif",cache)
                pixels, mask = tifffile.imread(raw_path), tifffile.imread(mask_path)
                if pixels.shape != mask.shape:
                    raise ValueError("Image/mask geometry mismatch")
                samples.append({"frame":t,"shape":list(pixels.shape),"image_dtype":str(pixels.dtype),
                    "mask_dtype":str(mask.dtype),"image_range":[int(pixels.min()),int(pixels.max())],
                    "labeled_instances":len(np.unique(mask))-int(np.any(mask==0))})
            results[sequence] = {"source":"synthetic","frame_count":len(names),"lineage":lineage,
                "segmentation_files":len([n for n in gt.namelist() if re.fullmatch(sequence+r"_GT/SEG/man_seg\d+\.tif",n)]),
                "samples":samples}
    report = {"image_archive_bytes":3180529910,"gt_archive_bytes":gt_path.stat().st_size,
        "gt_sha256":hashlib.sha256(gt_path.read_bytes()).hexdigest(),"gt_all_zip_entries_crc_valid":True,
        "remote_image_bytes_transferred":reader.transferred,"sequences":results}
    (output/"bbbc-audit.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("BBBC audit completed",flush=True)


def audit_ce(output):
    sys.path.insert(0,str(Path(".tools/dataset-audit-deps").resolve()))
    import h5py
    record = json.loads(Path("data/zenodo-4630933.json").read_text())
    files = {f["key"]:f for f in record["files"]}
    report = {"version_record":record["id"],"license_description":record["metadata"]["description"],"metadata":{}}
    for name in ("Fluo-N3DH-CE_01.xml","Fluo-N3DH-CE_02.xml","Fluo-N3DH-CE_01.mastodon"):
        path = Path("data/downloads")/name
        digest = "md5:"+hashlib.md5(path.read_bytes()).hexdigest()
        if digest != files[name]["checksum"]:
            raise ValueError(f"Source checksum mismatch: {name}")
        if name.endswith(".xml"):
            r = ET.parse(path).getroot()
            setup = r.find("SequenceDescription/ViewSetups/ViewSetup")
            times = r.find("SequenceDescription/Timepoints")
            report["metadata"][name] = {"md5_verified":True,"xyz_shape":setup.findtext("size"),
                "xyz_spacing":setup.findtext("voxelSize/size"),"spatial_unit":setup.findtext("voxelSize/unit"),
                "time_range":[int(times.findtext("first")),int(times.findtext("last"))]}
        else:
            with zipfile.ZipFile(path) as z:
                if z.testzip() is not None:
                    raise ValueError("Mastodon ZIP failed CRC")
                report["mastodon"] = {"md5_verified":True,"members":z.namelist(),
                    "model_raw_bytes":z.getinfo("model.raw").file_size,
                    "note":"Binary Mastodon graph not decoded; no event counts or completeness claim"}
    reader = RangeReader("https://zenodo.org/records/4630933/files/Fluo-N3DH-CE_01.h5",2128586382)
    with h5py.File(reader,"r") as f:
        times = sorted(k for k in f.keys() if re.fullmatch(r"t\d+",k))
        group = f[times[0]]
        setup = next(iter(group))
        level = next(iter(group[setup]))
        ds = group[setup][level]["cells"]
        patch = ds[:1,:16,:16]
        report["h5"] = {"time_groups":len(times),"time_group_range":[times[0],times[-1]],
            "dataset_path":ds.name,"shape":list(ds.shape),"dtype":str(ds.dtype),"chunks":list(ds.chunks),
            "compression":ds.compression,"patch_range":[int(patch.min()),int(patch.max())],
            "bytes_transferred":reader.transferred,"h5py_version":h5py.__version__,
            "note":"Only metadata and one small chunk/patch audited; full volumes and annotations not scientifically validated"}
    (output/"ce-audit.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("CTC CE metadata/container audit completed",flush=True)


if __name__ == "__main__":
    output = Path("runs/bbbc-ce-audit")
    output.mkdir(parents=True,exist_ok=True)
    audit_bbbc(output)
    audit_ce(output)
