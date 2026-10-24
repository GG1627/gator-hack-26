# MSKCC-CONFOCAL audit — 2026-10-23 23:25 -04:00

## Verdict

**Strong 3D+t replacement for PHOTON if CHO remains unavailable.** It preserves
volumetric fluorescence, provides three independent embryos for development and
evaluation, and has substantial, internally consistent division annotations.
The first 270 frames of each embryo are the recommended initial scope, following
the authors' pre-existing caution about later embryonic twitching. This is a
dataset-suitability finding, not evidence PHOTON outperforms a baseline.

This report records the candidate audit before dataset selection. The user
subsequently authorized MSKCC as the primary dataset after CHO remained
unavailable; the spec and Phase 1 gate now reflect that choice. No Gaussian
fitting, adaptive benchmark or phase completion is claimed by this audit.

## Source and scope of verification

- [Author deposit](https://zenodo.org/records/6460303), DOI 10.5281/zenodo.6460303.
- [Author README](https://zenodo.org/records/6460303/files/README.md?download=1).
- Downloaded API record lists open access and CC BY 4.0; preserve attribution to
  the data creators and associated publications. This is not an unauthorized
  clone of the unavailable CTC archive.
- Official ZIP: 26141247410 bytes; publisher MD5
  `74e2da0e745d67c2e174dc384f3d8ca4`. **Full ZIP MD5 was not verified**, because
  the full 26.1 GB was not downloaded.
- Parsed ZIP64 central directory over verified HTTP byte ranges. It lists
  400 contiguous image indices, 0..399, in each of three embryos.
- Downloaded all three main tab-separated lineage tables and MaMuT XMLs, plus
  five image volumes per embryo at source indices **0,89,179,269,399**. These
  times were selected before image/event inspection, not for favorable events.
- Local audit cache: **433089383 bytes**, roughly 433 MB. Every selected entry
  passed ZIP CRC validation on retrieval and cache reuse. This verifies selected
  files, not the integrity of the other 1185 image files or the complete archive.
- Did not use the supplied global foreground masks or separate polar-body tracks.

## Image findings

All 15 decoded samples are **41 x 512 x 512 uint16** volumes. No sampled pixel
equals the uint16 maximum 65535. Actual intensity distributions were recorded
per volume in `runs/mskcc-audit/audit.json`; do not apply per-frame display
contrast settings as metric normalization or supply future-derived normalization
statistics to the acquisition controller.

The XML calibration agrees across embryos: X/Y 0.15 um, Z 0.75 um, 400 frames.
The author README documents **75 seconds per volume**. XML model time is in
frames; use the README as the cadence source rather than inventing TIFF
timestamps. Each observation would be one complete 41-plane volume; count
acquisitions consistently across policies. This is an exposure-count proxy,
not measured illumination dose or phototoxicity.

### Coordinate convention

CSV and MaMuT XYZ positions use XY-pixel-sized units. Thus:

- voxel indices = `(z/5, y, x)` in ZYX array order;
- physical XYZ coordinates = `(x*0.15, y*0.15, z*0.15)` um.

The ratio 5 follows the XML voxel calibration. Sampled annotation positions are
within image bounds after this conversion. Viewed maximum-intensity projections
with position overlays at all 15 sample times. Positions align with visible
nuclei in labeled samples; this does not independently validate all individual
track identities. For embryo 1 frame0, annotated-center neighborhoods contain
peaks 4735 and 4348 versus a volume 99.9th intensity percentile of 2598,
supporting the XYZ calibration at those two sampled nuclei.

## Annotation findings

Counts below were derived from actual downloaded files, not copied from the
dataset description. A division is a mother spot with exactly two outgoing
children. An event is inside the first270 scope only if mother and both children
are within frames 0..269.

| Sequence | Spot records | Labeled frame range (inclusive) | Binary divisions, all labels | Binary divisions within first270 |
|---|---:|---|---:|---:|
| s1 | 129879 | 0..399 | 655 | 568 |
| s2 | 114937 | 0..375 | 653 | 560 |
| s3 | 111175 | 0..369 | 652 | 567 |
| Total | 355991 | — | 1960 | **1695** |

All three first270 windows have annotations at every frame. All parent IDs
resolve, all parent-child links advance exactly one frame, and there are no
parents with more than two children. Each sequence has two founder roots; the
`track_id` values identify two founder-connected lineage graphs, not just two
individual cells. All binary branch parents carry the independent `div_state=1`
marker. These are annotated events, not biological events independently verified
by PHOTON or a measured event-detection score.

### CSV/XML discrepancy discovered and bounded

Cross-checked every spot ID, frame index and edge in the convenient TSV tables
against the separately provided MaMuT XML. **All IDs, frames and edges agree in
all three sequences.** Positions agree exactly in s1, but differ for:

- s2: 163 spots, including 154 in the first270 window; largest spatial difference
  about 10.09 XY-pixel units (~1.51 um).
- s3: 102 spots, including 98 in the first270 window; largest spatial difference
  about 10.31 XY-pixel units (~1.55 um).

An initial strict equality check halted at s2. Investigation established that
the discrepancy is spatial, with zero temporal-graph differences. The final
audit reports it explicitly and requires temporal-graph agreement. The reason
for the different coordinates is unknown. This does **not** change the reported
division times or counts, but spatial tracking accuracy should be deferred until
a canonical annotation representation is documented. Do not silently mix the
two coordinate sets or claim complete agreement.

## Suitability and limitations for PHOTON

**Advantages:** genuine 3D+t raw volumes; dense temporal sampling; 1695 annotated
divisions in a defensible common scope; separate embryos permit sequence-level
development/evaluation splits; understandable nuclear proliferation; substantial
scientific Gaussian evaluation workload. TIFF per source frame fits our replay
architecture without requiring a Zarr/GEFF stack.

**Limits:** embryos are more stereotyped and densely dividing than cultured CHO
cells. Results would demonstrate performance on C. elegans development, not
general live-cell imaging. Dense late nuclei overlap in 2D projections, so retain
volumes for scientific scoring. Annotation objects are points/lineages, not full
per-nucleus segmentation masks. Bright polar bodies and background fluorescence
are visible; their separate annotations and full-sequence masks must remain
evaluation-only unless a causal use is independently justified. Later motion
and incomplete late labels motivate the first270 restriction.

**Execution cost:** one volume is roughly 21.5 MB of pixel data; 270 source frames
are roughly 5.8 GB per embryo uncompressed. Stream volumes instead of loading
all embryos into memory. Selective downloading works, but full sequence ingest
still requires a larger transfer and validation of all frames selected for replay.
No end-to-end download timing or GPU speedup benchmark is claimed.

## Reproduction and checks

```powershell
.\.venv\Scripts\python.exe scripts/audit_mskcc_dataset.py --inventory-only
.\.venv\Scripts\python.exe scripts/audit_mskcc_dataset.py
.\.venv\Scripts\python.exe -m pytest -q
```

Audit completed successfully after resolving the position discrepancy. Final
test run: **22 passed in 2.36s**. Added tests cover valid remote ZIP extraction,
cache corruption, ignored/wrong HTTP ranges, truncated data and invalid seeking.
The initial audit pass sampled volumes and TSVs; the final pass cross-checked all
three XMLs and reused CRC-verified cached files. Raw/annotation cache stays under
ignored `data/mskcc-audit/`; inventory, exact counts, calibration and evaluation-only
contact sheets stay under ignored `runs/mskcc-audit/`.

## Integration requirements (selection now authorized)

Explicitly amend the dataset-specific requirement while preserving the science
contracts. Provisionally use s1 for development and s2/s3 for held-out evaluation,
all limited to 0..269, with that split frozen before tuning. Audit access to their
labels is dataset QA, not permission to tune on held-out outcomes. Download and
validate the full declared windows, add native filename/metadata support and a
tested lineage importer, then run the Phase 1 same-budget real-data gate. Preserve
annotation/future-image isolation. Do not progress to Phase 2 based on this
sample audit alone.
