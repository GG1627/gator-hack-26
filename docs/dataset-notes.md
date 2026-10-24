# CTC data provenance and use conditions

**Current plan:** MSKCC-CONFOCAL is the approved primary replacement (2026-10-23).
See [the MSKCC audit](mskcc-audit.md) and README for its CC BY 4.0 source and current
commands. CTC notes below are historical and do not impose conditions on MSKCC.

Checked 2026-10-23 against the official
[dataset description](https://celltrackingchallenge.net/datasets/),
[3D dataset page](https://celltrackingchallenge.net/3d-datasets/),
[annotations](https://celltrackingchallenge.net/annotations/) and
[naming conventions](https://public.celltrackingchallenge.net/documents/Naming%20and%20file%20content%20conventions.pdf).
The naming PDF search extract was available; direct PDF retrieval timed out.

## Intended training archive

`https://data.celltrackingchallenge.net/training-datasets/Fluo-N3DH-CHO.zip`

Official metadata: CHO nuclei overexpressing GFP-PCNA; Zeiss LSM 510; 9.5 minutes
per source timestep; XYZ voxel size 0.202, 0.202, 1.0 micrometers. These values
come from the official dataset page, not TIFF-derived measurements. Array shape
is preserved in TIFF order (for a volume, ZYX); `voxel_size_xyz_um` explicitly
uses XYZ order. Do not infer sub-frame temporal precision.

Data provider: Dr. J. Essers, Dept. of Cell Biology, Erasmus Medical Center,
Rotterdam, The Netherlands, as credited by CTC.

## Conditions relevant to PHOTON

The official conditions request CTC/data-source acknowledgment and citation of
the linked Nature Methods paper (optionally its predecessor). CTC-related use
does not require explicit consent; public scientific use outside CTC requires
organizer permission. Commercial use requires organizer and provider permission.
Dataset/annotation cloning is prohibited; share official download links rather
than repackaging data. Downloads do not require CTC registration; official result
submission does.

Current scope is local development. **Public hackathon display/release permission
has not been established.** Obtain organizer clarification/permission before a
public non-CTC scientific demo using these images; synthetic fixtures remain the
public fallback. Do not publish raw data, contact sheets or annotations generated
from CTC in this repository. `data/` and `runs/` are ignored. No permission request
has been sent on the user's behalf.

## Audit status

Download connection timed out on both Windows and WSL (HTTPS); an HTTP retry also
timed out. DNS resolved the official data host to 147.251.52.183. A probe of the
official public host also timed out. No archive was obtained, and no actual
frame count, shape, track count, annotation coverage or division count is known.
Do not substitute metadata copied from a paper for inspecting this archive.

When available, inspect `01`/`02` source folders and corresponding `*_GT/TRA` and
`*_GT/SEG`. CTC gold tracking annotations provide cell markers and a lineage
graph, while gold segmentation has limited cell instance coverage. Silver
segmentations are not independent gold division labels. The audit parses each
`man_track.txt` row as label, begin, end, parent; validates parent timing and
counts a binary division only for a parent with two immediate children.
Missing files yield unavailable labels, never fabricated zero-event evidence.
Mask content/lineage consistency still requires review of the actual archive.

## Resume commands (PowerShell; not yet verified on real data)

Download through the official page into `data/downloads/Fluo-N3DH-CHO.zip`, then:

```powershell
Expand-Archive -LiteralPath data/downloads/Fluo-N3DH-CHO.zip -DestinationPath data/ctc
# Locate the directory containing 01 and 01_GT; adjust this root if needed.
.\.venv\Scripts\python.exe scripts/inspect_dataset.py data/ctc/Fluo-N3DH-CHO --output runs/cho-audit.json
.\.venv\Scripts\python.exe scripts/run_experiment.py --sequence data/ctc/Fluo-N3DH-CHO/01 --budget 10 --seed 42 --output runs/cho-phase1
```

Check the audited frame count before choosing B. `B=10` is an example request,
not a claim about actual sequence length. `--policy both` is the CLI default.
The real-data gate remains closed until these execute, annotations are audited,
and equal-count run artifacts are inspected.

## Alternative-source investigation (2026-10-23)

No verified provider-authorized CHO mirror was found in this search. Other CTC
datasets linked by the site use the same unavailable data host.

Successfully downloaded the author-deposited
[Division Detection and Tracking Annotated Dataset](https://figshare.com/articles/dataset/Division_Detection_and_Tracking_Annotated_Dataset/25766259)
through Figshare API metadata (`https://api.figshare.com/v2/articles/25766259`)
and file `https://ndownloader.figshare.com/files/46163280` into ignored
`data/downloads/division-tracking-figshare.zip`. Size 175060057 bytes; local MD5
`369e4c3823b594c409b6d2a4862591f0` matches the depositor's computed checksum.
API lists CC BY 4.0. Archive inspection confirms raw multichannel TIFF images,
segmentation masks, division CSV files for ten videos, and tracking XML for three
videos. READMEs describe 19 frames per video; API describes 4-hour cadence,
512x512 images, 0.3 um pixels and four fluorescence channels. Archive READMEs
give inconsistent wording about cross-folder video correspondence; validate
actual identities before joining tracking and division labels. Mac resource
fork entries must be excluded. No channel selected or event counts audited yet.

This is a practical small real-data fallback, but 19 frames at 4-hour intervals
limits meaningful adaptive scheduling and fine mitosis timing. A non-CTC dataset
does not fulfill the current CTC-specific requirement automatically; document a
plan/spec amendment if selected. No dataset switch or gate completion yet.

[LFCT](https://davislab.github.io/LFCT-dataset/) is another promising source:
the [MCF10A page](https://davislab.github.io/LFCT-dataset/mcf10a.html) links original
RFP images and corresponding XML annotations by field of view via Clemson Box;
it describes 10–15 minute acquisition intervals. Prefer original image downloads
over rendered GAP videos for replay. Box downloads, exact sequence metadata,
annotation completeness and dataset licensing have not yet been validated
locally. A Zenodo record linked in the indexed paper returned HTTP 404 from the
local API; do not rely on it as a verified download source.
