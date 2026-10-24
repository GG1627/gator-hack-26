# Dataset selection investigation — 2026-10-23

## Recommendation

**3D-priority follow-up (2026-10-23 23:11 -04:00):** The recommendation below
compared the two requested 2D alternatives, not all available 3D+t resources.
Broader search found independent 3D+t sources. For preserving volumetric scope,
prioritize MSKCC-CONFOCAL C. elegans for the next feasibility audit; LFCT remains
a verified-access 2D fallback. No production dataset switch has been applied.

**Audit update (23:25 -04:00):** MSKCC selective audit completed: all three
TSV/XML lineages and 15 volume samples inspected; 1695 binary divisions fully
inside the common first270 frames. Strong volumetric replacement recommended;
spatial coordinate discrepancies documented separately. See [full audit](mskcc-audit.md).

**Current selection:** MSKCC was subsequently approved and Phase1 completed on
its full s1 first270 window. Additional BBBC035/Zenodo CE suggestions were audited
2026-10-24: keep MSKCC. See [additional-source audit](bbbc-ce-audit.md) for actual
files inspected, size corrections, synthetic/real distinction and audit limits.

Use **LFCT fluorescent-nuclei sequences as the primary 2D+t experiment**, with
Figshare division/tracking data as a secondary coarse-time stress test. Keep CHO
as a future 3D+t comparison if the official host returns. This is a recommendation,
not a silently applied replacement of the spec's CTC requirement. No replacement
dataset has yet run through PHOTON replay; Phase 1's real-data gate stays open.

The main reason is temporal sampling: PHOTON needs enough source times to compare
many acquisition choices, estimate motion from acquired images and evaluate what
happened during skips. Having division labels alone does not compensate for a
source movie sampled only once every four hours.

## What made CHO attractive

- Real fluorescent nuclei in 3D+t, with documented 9.5-minute cadence and XYZ
  voxel spacing 0.202/0.202/1.0 um.
- Small advertised training download (98 MB), standard CTC TIFF layout and
  accompanying available training annotations.
- Direct methodological relevance: CellSplat4D reports evaluating CHO and
  C. elegans, so CHO would support a transparent comparison in a related setting.
- A natural path from 2D maximum-intensity-projection prototypes to volumetric
  Gaussians, without changing experiments.

These are design advantages, not evidence CHO has adequate division labels or
that PHOTON performs well on it. The archive was never obtained. The original
spec explicitly requires auditing events rather than assuming they exist.
Server access and public non-CTC-use permission remain obstacles.

Sources: [CTC dataset details](https://celltrackingchallenge.net/3d-datasets/),
[CellSplat4D abstract](https://arxiv.org/abs/2610.04199),
[CTC conditions](https://celltrackingchallenge.net/datasets/).

## LFCT — downloaded and audited sample

Author-provided [MCF10A page](https://davislab.github.io/LFCT-dataset/mcf10a.html)
links original RFP image ZIPs and XML annotations. Downloaded FLD_3 images
(231337877 bytes) and XML (19093520 bytes) from public Clemson Box links;
also downloaded FLD_4 XML (20870993 bytes). No account was needed.

FLD_3 local findings:

- 433 contiguous `rfp_0000.tif` through `rfp_0432.tif`, all 904x1224 uint8,
  single-plane, uncompressed TIFFs. 2D+t, not 3D+t.
- XML declares matching dimensions and 433 frames, contains 6656 spots and
  16 filtered track graphs. A graph can include multiple cells across divisions;
  16 graphs does not mean only 16 individual cell trajectories.
- 17 binary branching points reconstructed from directed links, matching the
  XML's total reported splits. All 6627 filtered edges join consecutive source
  frames. No merges or direct consecutive mother/daughter branch points found.
  6643 spots participate in links, versus 6656 total spots.
- Visually checked XML position overlays on RFP frames 0,100,200,432. They align
  with fluorescent objects in these samples. This is a spot check, not independent
  certification of all 17 mitoses or all object identities.
- FLD_4 XML declares 433 frames, 9877 spots, 22 track graphs and 44 reported
  splits. Its original images are not yet downloaded. It is a candidate separate
  evaluation sequence; do not tune parameters using its labels.

Timing caveat: authors describe 10–15 minute imaging intervals, but both XMLs
declare `timeinterval=1.0` and FLD_3 labels model time units as seconds. The sampled
TIFF has no acquisition timestamp or calibration beyond an ImageJ description.
Do not interpret the XML as actual one-second imaging or assign a precise
physical cadence by inference from movie length. Keep source frame indices and
unknown physical interval until sequence-specific calibration is confirmed.

Licensing: the [authors' paper data-availability section](https://pmc.ncbi.nlm.nih.gov/articles/PMC13251996/)
states CC BY 4.0 for the dataset. The website repository's LICENSE.txt contains
CC BY 3.0 and appears alongside an HTML5 UP site; do not conflate website-template
licensing with the paper's dataset license. Preserve paper/source attribution.
The cited Zenodo record returned 404 via local API, but author-linked Box downloads
work. [Preprint](https://www.biorxiv.org/content/10.64898/2026.05.30.728955v1).

Engineering fit: fluorescent blobs suit an initial Gaussian observation model,
hundreds of times support useful budget sweeps, XML lineage structure supports
post-hoc event coverage, and separate fields allow development/evaluation splits.
8-bit images and bright/saturated objects limit intensity fidelity. Use suitable
ROI metrics later so background pixels do not dominate evaluation. Do not supply
phase-contrast images, annotations or precomputed full-sequence tracks to an
RFP-only acquisition controller.

## Figshare — downloaded and audited archive

[Author deposition](https://figshare.com/articles/dataset/Division_Detection_and_Tracking_Annotated_Dataset/25766259),
API record `https://api.figshare.com/v2/articles/25766259`, file ID 46163280.
175060057 bytes; MD5 `369e4c3823b594c409b6d2a4862591f0`, verified against depositor.
API states CC BY 4.0, four-hour intervals, four fluorescent channels and
0.3 um pixels. Ten division-video folders each contain 76 raw TIFFs (19 source
times x 4 channels); sampled images are 512x512 uint8. Three additional tracking
video folders contain images, masks and TrackMate XML.

Division CSV audit (12 numeric columns, no header):

| Video | Annotated division rows |
|---|---:|
| 0 | 10 |
| 1 | 12 |
| 2 | 38 |
| 3 | 97 |
| 4 | 10 |
| 5 | 75 |
| 6 | 47 |
| 7 | 50 |
| 8 | 60 |
| 9 | 19 |
| Total | 418 |

Six fully empty rows are excluded. Counts were independently reproduced using
NumPy `genfromtxt` and finite-row filtering. These are annotation records, not
validated recall or a biological outcome measured by PHOTON. Annotation times
include 0, while image filenames use 1..19, so index conversion must be explicit.
Source README descriptions conflict on which tracking folders correspond to
division folders. Neither exact raw-file hashes nor full raw-pixel-array hashes
found identical whole-video pairs across sections. Do not join by video number;
use division images and their own CSVs independently until correspondence is
established. No channel identity/biological reporter selection is validated yet.

Suitability: excellent for a compact labeled event fixture and a harder
coarse-time condition. Poor primary schedule benchmark: 19 frames offer few
budget choices, and four-hour source gaps cannot evaluate minute-scale division
timing or changes between recorded frames. Both replacements lose CHO's 3D data.

## Reproducibility and next steps

`scripts/audit_candidate_datasets.py` reproduces the downloaded-sample audit;
output `runs/candidate-audit/audit.json` includes source SHA256 hashes and counts.
Evaluation-only alignment contact sheet is generated locally and ignored by Git.
Initial exploratory parsing incorrectly assumed CSV headers; corrected before
using the counts, then handled empty rows and independently verified total 418.
Initial console inspection encountered Windows encoding of an author's path;
JSON-escaped output fixed it. No scientific benchmark was run.

Before replay integration: document the CTC-to-LFCT dataset-plan amendment,
download a separate field's images, keep raw/label namespaces separate, implement
a tested TrackMate importer with frame-based branch events, and preserve unknown
physical timing. Re-run all Phase 1 gates on actual images. Then freeze development
vs held-out fields before policy tuning. This keeps the scientific objective and
GPU roadmap intact while explicitly adopting a 2D+t primary dataset.

## Independent 3D+t alternatives

### MSKCC-CONFOCAL C. elegans — strongest next candidate

[Author Zenodo deposit](https://zenodo.org/records/6460303), CC BY 4.0 confirmed
through downloaded record API metadata. Three real confocal embryo movies,
400 frames each, 41x512x512 uint16 voxels, 75-second cadence, curated
tracks/lineages. TIFF per timepoint; MaMuT XML and CSV track representations.
Three embryos enable sequence-level development/evaluation separation.
The README explicitly cautions about later embryonic twitching: the linked
tracking paper used only the first 270 frames. Use that pre-existing restriction
as an initial evaluation scope, not a favorable trace selected after tuning.
Annotation completeness still requires local audit.

Archive size from API: 26141247410 bytes (26.1 GB), substantially larger than CHO.
Verified a public byte-range download directly from the archive: HTTP 206,
1024 requested bytes received. Both metadata and file host are reachable.
No full archive, image volume or lineage file downloaded yet. Byte-range support
allows investigating selective ZIP extraction; it does not yet establish a
working partial-download importer. Embryo proliferation differs biologically
from cultured CHO; generalization claims must stay within tested samples.

### Mouse intestinal organoid reference OME-Zarr — smaller packaged alternative

[Author Zenodo deposit](https://zenodo.org/records/22078388), CC BY 4.0 from API.
Real 3D+t light-sheet imaging, nuclear H2B and membrane markers, raw and
deconvolved volumes, segmentations, GEFF lineage graph, per-frame timestamps.
Full movie: 667 timepoints, 39.8 GB. Contiguous `001-small.zip`: roughly 50
timepoints, 2394240964 bytes. Five-frame mini is an I/O fixture, insufficient
for the main acquisition benchmark. Avoid pre-subsampled lowT/varT versions
as primary truth; make new policy schedules against contiguous raw source times.

Verified HTTP 206 for a 1024-byte range of `001-small.zip`; no full data downloaded.
Tradeoffs: OME-Zarr v0.5/GEFF require new readers, one original movie limits
independent sequence splits, annotations become sparse later, and reported
graph splits/merges require audit. Use raw nuclear channel as observations;
full-sequence deconvolution, normalization statistics and track-derived features
must not enter a causal controller without establishing causal preprocessing.

### Ultrack zebrafish neuromast — additional streaming candidate

[Author data portal](https://public.czbiohub.org/royerlab/ultrack/) supplies
nuclear/membrane Zarr data and manually curated track CSV, plus volume TIFFs.
Locally retrieved Zarr metadata confirms 500 times, 2 channels, with a coarse
3D level of 10x128x128 per channel/time (float32). TIFF directory lists 500 files,
hundreds of MiB each, so streaming a fixed resolution/channel is preferable.
Metadata/annotation licensing, acquisition timing and processing provenance are
not validated sufficiently to rank it above the two Zenodo candidates. Metadata
access is verified; image chunks and track content are not yet audited.

All three preserve 3D+t. None is automatically a CTC training sequence, so the
plan's dataset-specific requirement still needs an explicit amendment if chosen.
