"""Validated microscopy TIFF access for oracle/evaluation only, never policies."""
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re

import numpy as np
import tifffile


MSKCC_ID = "MSKCC-CONFOCAL"
MSKCC_WINDOW = 270
MSKCC_SHAPE = (41,512,512)
MSKCC_SPLITS = {"mskcc_confocal_s1": "development", "mskcc_confocal_s2": "evaluation", "mskcc_confocal_s3": "evaluation"}


@dataclass(frozen=True)
class SequenceMetadata:
    dataset_id: str
    sequence_id: str
    frame_count: int
    shape: tuple[int, ...]
    dtype: str
    source: str = "microscopy"
    split: str = "training"
    frame_interval_minutes: float | None = None
    voxel_size_xyz_um: tuple[float, ...] | None = None


class TiffSequence:
    def __init__(self, paths, metadata, fingerprint, provenance=None):
        self.paths = tuple(paths)
        self.metadata = metadata
        self.fingerprint = fingerprint
        self.provenance = provenance or {}

    def read(self, index):
        try:
            image = tifffile.imread(self.paths[index])
        except Exception as exc:
            raise ValueError(f"Cannot read TIFF {self.paths[index]}: {exc}") from exc
        if image.shape != self.metadata.shape or str(image.dtype) != self.metadata.dtype:
            raise ValueError(f"Changed shape/dtype at {self.paths[index]}")
        return image


def load_sequence(directory: Path, *, dataset_id="unknown", sequence_id=None, source="microscopy"):
    if source not in ("microscopy", "synthetic"):
        raise ValueError("source must be microscopy or synthetic")
    directory = Path(directory)
    mskcc = dataset_id == MSKCC_ID
    selected_id = sequence_id or (directory.parent.name if mskcc and directory.name == "images" else directory.name)
    if mskcc:
        if source != "microscopy" or selected_id not in MSKCC_SPLITS:
            raise ValueError("MSKCC requires microscopy source and a known s1/s2/s3 sequence ID")
        images = directory if directory.name == "images" else directory/"images"
        pattern = re.compile(re.escape(selected_id)+r"_t(\d+)\.tif")
        indexed = sorted((int(m.group(1)), p) for p in images.glob("*.tif")
                         if (m := pattern.fullmatch(p.name)) and int(m.group(1)) < MSKCC_WINDOW)
    else:
        indexed = sorted((int(m.group(1)), p) for p in directory.glob("t*.tif")
                         if (m := re.fullmatch(r"t(\d+)\.tif", p.name)))
    if not indexed:
        raise ValueError(f"No CTC or native MSKCC TIFF frames in {directory}")
    expected_count = MSKCC_WINDOW if mskcc else len(indexed)
    if [i for i, _ in indexed] != list(range(expected_count)):
        raise ValueError(f"Missing or duplicate frame indices in {directory}; expected contiguous indices from 0")
    shape = dtype = None
    digest = hashlib.sha256()
    for _, path in indexed:
        try:
            with tifffile.TiffFile(path) as tif:
                if any(page.samplesperpixel != 1 for page in tif.pages):
                    raise ValueError("Multichannel/RGB TIFFs are unsupported")
                image = tif.asarray()
        except Exception as exc:
            raise ValueError(f"Cannot read TIFF {path}: {exc}") from exc
        if image.ndim not in (2, 3) or min(image.shape) < 1 or image.dtype not in (np.dtype('uint8'), np.dtype('uint16')):
            raise ValueError(f"Unsupported shape/dtype {image.shape}/{image.dtype} in {path}; expected 2D/3D uint8/uint16")
        if shape is not None and (image.shape != shape or str(image.dtype) != dtype):
            raise ValueError(f"Inconsistent shape/dtype in {path}")
        shape, dtype = image.shape, str(image.dtype)
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    cho = dataset_id == "Fluo-N3DH-CHO"
    if mskcc and (shape != MSKCC_SHAPE or dtype != "uint16"):
        raise ValueError(f"MSKCC expected shape {MSKCC_SHAPE}, uint16; got {shape}, {dtype}")
    metadata = SequenceMetadata(dataset_id, selected_id, len(indexed), shape, dtype, source=source,
                                split=MSKCC_SPLITS[selected_id] if mskcc else "training",
                                frame_interval_minutes=1.25 if mskcc else 9.5 if cho else None,
                                voxel_size_xyz_um=(0.15,0.15,0.75) if mskcc else (0.202,0.202,1.0) if cho else None)
    provenance = {"source_doi":"10.5281/zenodo.6460303","license":"CC-BY-4.0",
                  "source_frame_count":400,"source_window_inclusive":[0,MSKCC_WINDOW-1],
                  "metadata_source":"Author README and MaMuT image calibration",
                  "observation_unit":"complete 41-plane volume"} if mskcc else {}
    return TiffSequence([p for _, p in indexed], metadata, digest.hexdigest(), provenance)
