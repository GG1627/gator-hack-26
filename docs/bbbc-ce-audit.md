# User-suggested dataset audit — 2026-10-24 00:09 -04:00

## Decision

**Retain MSKCC-CONFOCAL as the sole required dataset family.** The suggestions
are legitimate and their hosts are reachable, but neither demonstrates a clear
advantage for PHOTON's primary causal acquisition experiment on real 3D microscopy.
No new dataset is integrated, no policy/evaluation settings change, and the
verified Phase 1 replay remains valid. This is a suitability assessment, not a
comparative reconstruction or scheduling benchmark.

## BBBC035 / Fluo-N3DH-SIM+

[Broad's original dataset page](https://bbbc.broadinstitute.org/BBBC035) explicitly
identifies it as an exact copy of CTC Fluo-N3DH-SIM+, generated with MitoGen.
It is **synthetic**, not a recording of live HL60 cells. Broad documents a
29-minute source interval, CC BY 3.0 attribution licensing and CTC-use notices.
Preserve the whole source notice if used later; no public redistribution occurred.

### Access and integrity

- Images: `https://data.broadinstitute.org/bbbc/BBBC035/BBBC035_v1_dataset.zip`,
  3180529910 bytes. Byte-range access verified; ZIP directory parsed remotely.
- Ground truth: `https://data.broadinstitute.org/bbbc/BBBC035/BBBC035_v1_DatasetGroundTruth.zip`,
  150947167 bytes, downloaded completely. All ZIP entries passed CRC checks.
- Six image volumes and their matching segmentation volumes downloaded and
  decoded, using early/middle/last times in each sequence. Selected image entries
  passed source ZIP CRC. Full image ZIP checksum/integrity is not verified.
- Initial TIFF decoding failed because LZW needs imagecodecs. Installed
  imagecodecs 2026.10.10 only in ignored `.tools/dataset-audit-deps`; application
  dependencies are unchanged. Preview generation also needed that isolated
  import path; rerun succeeded with it loaded.

### Actual local findings

| Sequence | Source frames | SEG files | Track records | Binary divisions | Sampled ZYX shape |
|---|---:|---:|---:|---:|---|
| 01 | 150 | 150 | 81 | 37 | 59 x 349 x 639 |
| 02 | 80 | 80 | 117 | 40 | 59 x 642 x 652 |

Both sequences have contiguous zero-based image indices. All six sampled images
and masks are uint16 with exactly matching geometry. Visually inspected synthetic
MIP/segmentation-boundary overlays at times 01:[0,75,149], 02:[0,40,79]; foreground
positions align in the samples. This is a spot check of masks, not validation of
every instance boundary. The source supplies masks at all times, an advantage
for testing segmentation/model-fitting methods against simulator truth.

The lineage-table count is **77 binary divisions total**. Sequence02 also has
two parents with one annotated child (track IDs28 and29); these are excluded from
the strict binary count. Their reason was not established, so do not automatically
call them either errors or complete two-child division events. Counts come from
the actual source lineage tables and do not measure a PHOTON result.

### Why it does not replace MSKCC

Synthetic instance masks are useful for controlled numerical or segmentation
validation. They cannot satisfy our real-microscopy evidence goal or establish
robustness to real imaging/biological variability. It also has fewer source
times and much coarser time sampling than MSKCC's 75 seconds. Retain as an audited,
optional future validation source; it is not part of the current pipeline or
required demo. Existing small scripted fixtures remain the automated test inputs.

## Zenodo CTC CE deposit

[Source version record](https://zenodo.org/records/4630933).
`https://zenodo.org/api/records/4630932` redirects to the same record as
4630933. These links do not represent two additional independent datasets.
The version bundles two CE sequences plus a separate PH dataset and pretrained
model weights.

### Corrections to download-size interpretation

The whole deposit is roughly15.9GB, but the two CE image files alone total
**4769684314 bytes (~4.77GB)**: CE01 2128586382 and CE02 2641097932. Their XML and
Mastodon files add about5.5MB. The PH files and pretrained weights are not needed
to access the CE images. No model weights were downloaded or used; using weights
trained on evaluation sequences could violate the causal/training contract.

### Metadata/container audit actually executed

- Downloaded both XML files (59833 bytes each) and CE01 Mastodon project
  (2779476 bytes); all three match the source's published MD5 checksums.
- XML declares 250 times, indices0..249, for each sequence.
  CE01: ZYX35x512x708. CE02: ZYX31x512x712.
  XYZ calibration approximately0.09/0.09/1.0um.
- Public byte ranges of CE01 HDF5 are reachable. Using h5py3.16.0 from the
  isolated audit directory, read HDF5 metadata and one small patch. It contains
  250 time groups; `/t00000/s00/0/cells` matches CE01 XML shape, uses int16
  storage, gzip compression and16x16x16 chunks. Only43474 bytes transferred in
  this probe. Correct interpretation of stored intensity values still requires
  verification before any quantitative use; do not blindly reuse the uint16
  TIFF profile.
- CE01 Mastodon ZIP CRC passes. Members are `project.xml`, `model.raw` and
  `tags.raw`; the graph is binary Mastodon data, not our validated MaMuT XML
  graph. **No lineage graph was decoded, and no division count or completeness
  claim is made for this source.** Full HDF5 volume quality and CE02 HDF5 were not
  audited locally. This is explicitly a bounded metadata/container audit.
- An initial h5py open required `readinto`, missing from our ZIP-oriented HTTP
  reader. Added the standard file-like method and exercised it in tests; HDF5
  metadata/patch access then succeeded. No application science module changed.

### Reasons not to switch

The author's description explicitly states **CC BY-NC-ND4.0**, compared with
MSKCC's CC BY4.0. The API license tag is `other-closed`; preserve the more specific
description instead of interpreting that tag as ordinary unrestricted reuse.
The deposit is publicly downloadable, but its stated reuse terms are less
permissive. No legal conclusion about a particular future public artifact is
assumed here.

The two real C. elegans sequences are relevant, but they do not add a new organism
relative to MSKCC. Switching would require HDF5/intensity handling plus a tested
Mastodon importer and a new annotation-quality audit. MSKCC already offers three
independent embryos, a validated270-frame real development window, open CSV/XML
lineages, and successful reproducible baseline replays. No demonstrated benefit
justifies replacing that working vertical slice. This is an integration/suitability
decision, not evidence MSKCC images are intrinsically higher quality.

## Reproduction and Phase 1 status

```powershell
.\.venv\Scripts\python.exe -m pip install --no-deps --target .tools/dataset-audit-deps h5py==3.16.0 imagecodecs==2026.10.10
.\.venv\Scripts\python.exe scripts/audit_bbbc_ce.py
.\.venv\Scripts\python.exe -m pytest -q
```

The script uses the downloaded source API record/XML/Mastodon/ground-truth files;
URLs are recorded above and in the script. Machine findings:
`runs/bbbc-ce-audit/bbbc-audit.json`, `ce-audit.json`; selected files under ignored
`data/bbbc-audit/`. HDF5/codec dependencies remain outside application requirements.

Audit script completed successfully. Final test run: **34 passed in2.69s**,
including `readinto` support. `pip check` reported no broken application
requirements. Existing MSKCC artifacts still match their repeated outputs and
the current science-code hash
`a9392d99895f45f25635d5a215598cf5138c64c8742d76c49a24c36020362f8c`.
Therefore no Phase1 real replay or dataset split needs to be redone. Phase1
remains verified; Phase2 remains unstarted.
