# PHOTON / Glimpse session handoff

## Current instruction and phase status

**Latest account-switch instruction:** research/discussion only, no code changes.
Read [GLIMPSE_ELEVATION_RESEARCH.md](GLIMPSE_ELEVATION_RESEARCH.md) for the agreed
research priorities, paper links, causal constraints, experiment boundaries and
a ready-to-paste continuation prompt. No proposed research improvement is implemented.

**Phase 5 has been manually resumed by the user**, using the standalone background
runner. At this handoff check, Python PID55068 existed, step1/5 was active, and the
log had reached evaluation t100/269. Recheck `runs/phase5-runner/status.json` and
`latest.log` on arrival; do not duplicate, stop or alter the running evaluation.
Phase 5 remains **INCOMPLETE / NOT VERIFIED**. The older paused checkpoint and
historical instructions below describe the earlier state and do not revoke the
user's subsequent manual resume. See root `PHASE5_RUN.md` for operational commands.

The user originally paused Phase 5 and authorized starting Phase 6 before its
scientific gates finish.
Phase 6 is now in progress under renewed user authorization: `apps/web/`
contains the local React/TypeScript replay viewer. `scripts/build_phase6_assets.py`
exports display assets from authentic closed runs without resuming Phase5.
The user approved the original playthrough, then requested a distinctive redesign
and selected **Glimpse E / Contact**. That design is now implemented with an
interactive Three.js specimen viewer, authentic voxel samples, saved Gaussian
fits/forecasts, an acquired-image toggle and shared photographic contact strips.
Run `scripts/build_glimpse_spatial.py` after the base export for the 3D assets;
existing generated assets are available locally and ignored by Git. See
`docs/design/glimpse/implementation.md` and README for the display/science contract.
The formal unfamiliar-viewer ten-second comprehension
criterion remains unrecorded; Phase6 is not marked fully complete.
See BUILD_PHASES.md and README for current verification, local preview and
remaining acceptance gates. The historical pause-checkpoint details below
describe the state before this Phase6 work.

Read AGENTS.md, PHOTON_SPEC.md, BUILD_PHASES.md and this handoff before coding.
The user-approved sequencing exception is recorded in BUILD_PHASES.md; the
scientific protocol and its completion gates have not changed.

## Workspace and environment

- Existing checkout: C:\Users\gael8\Coding\gator-hack-26, branch main.
- Use .venv/Scripts/python.exe. Existing Python 3.13.5, NumPy 2.5.4, SciPy 1.18.1,
  Matplotlib 3.11.2; requirements-dev.lock records installed dependencies.
- Keep .venv/, .tools/, data/, runs/, caches, binaries and credentials ignored.
  Closing this session does not remove the existing local files. Do not
  force-add raw data or generated runs. Git source alone does not include them.
- At the historical pause, no PHOTON evaluator or stage orchestrator remained running. Ctrl+C to the
  execution session stopped the process tree, and process absence was checked.
  That old automatic chain was stopped. The user has since launched the new
  standalone runner; consult the current status at the top of this file.

## What finished

1. All primary docs and existing repository/artifacts were inspected. Baseline
   tests: 85 passed in56.64s. Latest full tests on the frozen implementation:
   **93 passed in81.47s**, runs/phase5-tests-registered-source.log.
2. Complete s2/s3 source windows0..269 downloaded and validated, each270 decoded
   41x512x512 uint16 volumes. Selected images and main annotations match author
   ZIP CRCs. Image bytes5849610913 /5849623218. Cadence75s; XYZ spacing
   0.15/0.15/0.75um. Frame399 samples are outside the window. Full archive MD5
   was not verified. Details: runs/phase5-data-validation.json.
3. Protocol frozen before held-out outcomes at2026-10-24 13:30 -04:00:
   runs/phase5/protocol.json SHA256
   7e675b6569a82dbf8fff4ac59fbcaf950e7f4dd21d1e3a5b6bd08a861a794b73.
   Frozen source ZIP SHA256
   ed21533fecf4533b2d8b5d94f2656eb88040dc97a33e75a0a7ad0c02d7ff8067.
   Registration's outcomes_inspected=false describes the moment of freezing,
   not the current state: event results and two image conditions are now known.
4. All36 acquisition trajectories closed by14:22 -04:00: s2/s3, B27/54/89,
   fixed, PHOTON paced_robust, image-change, random seeds7/42/2026. Exactly B
   captures including0,9720 decisions,2040 simulated whole-volume captures.
   All PHOTON/image-change min2/max12/terminal-age checks passed. Every run has
   config, decisions, timeline, state, forecast/held-scene NPZs and closed.json.
   Source hashes and all36 closed-file hash ledgers rechecked at pause; source
   ZIP CRC verified. All controllers closed before any outcome scoring.
5. All36 event coverage results computed after closure, with independent
   nearest-capture arithmetic: runs/phase5/event-audit.json. Fixed beats PHOTON
   in all6 conditions. At B27/54/89: s2 fixed176/352/557 of560 versus
   PHOTON140/325/544; s3 fixed150/348/558 of567 versus PHOTON131/332/546.
   These are +/-1-frame retrospective observation-coverage counts, not event
   detector recall. All other baseline/seed results are retained.
6. Full-image FIRST-PASS errors completed for **s2/B27 and s2/B54**, all6
   methods each:12 image-scored runs,2754 withheld-frame statistic rows, all3
   estimators (Gaussian forecast, held Gaussian fit, raw hold). Metrics and
   evaluation JSONL files are present and structurally match saved summaries.
   s2/B27 additionally passed independent scalar/target/budget/seed/controller/
   event accounting: its early-verification.json. s2/B54 has not yet had that
   independent accounting pass. Neither has had a second source rerender.

## What remains unfinished and unverified

- s2/B89 image scoring was interrupted. Last logged frame100; exact subsequent
  in-memory progress is unknown and was not saved. No group summary, image
  metrics or per-frame evaluation exports exist. Resume starts this group at0.
- s3/B27, s3/B54, s3/B89 image scoring has not started. Their acquisition
  trajectories and event-only results are complete.
- No complete benchmark.json, global verification.json, full recomputation.json,
  report.md, comparison chart, cards.json or post-hoc image case panels exist.
- Full source recomputation has **not started**. Phase 5 has not passed.
- Low available RAM (observed below1GB) slowed the CPU image pass. No scientific
  approximation, downsampling or GPU setup change was introduced.

## Checkpoint and authentic partial artifacts

- runs/phase5/checkpoint.json: machine-readable state, exact completed/pending
  conditions, saved-artifact hashes, verification levels and resume commands.
- runs/phase5-paused-checkpoint.zip: all current Phase5 run artifacts, frozen
  protocol/source, validation, pipeline/download logs and final test log;
 17348462 bytes, CRC checked. Raw microscopy is excluded and remains in data/.
  SHA256: 42a73b943ae4e1ea5b7ebbaf8f03c466af36ef6e1d355cfe45a9e4c04ce68b05.
  Sidecar: runs/phase5-paused-checkpoint-manifest.json. Originals stay in place.
- runs/phase5/mskcc_confocal_s2/b27/summary.json and b54/summary.json, plus
  per-method metrics.json / evaluation.jsonl: authentic computed image results.
- All36 config.json / decisions.jsonl / timeline.txt / state.json /
  forecasts.npz / held_scenes.npz: authentic closed acquisition artifacts.
- runs/phase5/event-audit.json and event-failure-audit.json: complete event-only
  comparisons and descriptive temporal failures. Original log is retained at
  runs/phase5-pipeline.log; no automatic pipeline remains alive.

Important known results: s2/B27 paired-common raw-hold MSE is PHOTON
0.006764643617763716 vs fixed0.006863698660076684 on218 targets, but OWN-withheld
MSE reverses that ranking: PHOTON0.006847225856928299 vs fixed0.006734736906330803.
PHOTON Gaussian forecast0.02026135787759542, held Gaussian0.02019323943815579,
raw hold0.006847225856928299. Retain the raw baseline and both target sets;
conditional matched-target gains do not establish general accuracy superiority.
At B54, both embryos' divisions at100 are covered by fixed capture101 but missed
by PHOTON97/102 at the declared tolerance (11 s2 /7 s3 events). At100, logged
PHOTON priorities0.8937/0.8877 are below threshold1 and pacing also disallows
another discretionary capture. No parameters or timing offsets were changed.

## Phase 6 authorization and data rules

Start frontend work only; do not resume Phase 5 automatically or alter its
scientific implementation. Use saved authentic artifacts. Label image metrics
for the two completed conditions **first-pass / source rerender pending**;
label the other four image conditions **pending / not computed**. Event-only
results cover all6 conditions; the overall benchmark remains **partial**.
Pending values are null with reasons, never fabricated zeros or guessed scores.
No global benchmark/card/chart generation has been completed yet.

Keep MEASURED, PREDICTED and GROUND TRUTH (EVAL ONLY) displays distinct. Canonical
annotations/future pixels never enter controllers. Ground-truth reveal is an
explicit evaluation view. Trusted data QA decodes full windows beforehand but
passes no future pixels to controllers. Acquisition count is an exposure proxy;
no biological phototoxicity improvement or calibrated event detector is proven.
Random has equal capture count but no adaptive gap constraint. Two embryos and
three random seeds do not support significance/generalization claims.

Do not edit frozen photon modules, services/science/tests, the protocol,
run_phase5.py, report_phase5.py, inspect_phase5_failures.py or other files listed
in protocol.implementation_hashes. Guards reject changes. Frontend files/tests
can live outside those paths. Keep s1 development and s2/s3 held out; do not tune
on these known held-out outcomes. GPT-6.1 Sol Medium is sufficient for routine
frontend work; model choice remains manual.

## Manual Phase 5 resume - only when the user explicitly resumes it

The user requested a standalone background runner. **`PHASE5_RUN.md`** now
contains the PowerShell start/watch/stop instructions. `scripts/finish_phase5.py`
runs resume scoring, ledger verification, full recomputation, report and case
panels sequentially, stopping on failure. It appends progress/errors to
`runs/phase5-runner/latest.log` and writes `status.json`; a Windows process lock
rejects duplicate wrapper launches. No computation was launched while preparing
these files. The guide explains restart granularity and that full recomputation
restarts from the beginning. Frozen scientific scripts remain unchanged.

From the existing workspace:

```powershell
.venv/Scripts/python.exe -u scripts/run_phase5.py evaluate
```

It checks frozen sources and saved ledgers, skips the two completed summary
conditions, restarts s2/B89 at0 and then scores all three s3 conditions. Policies
and fitting are not rerun. TIFF integrity loading is repeated; completed score
groups are reused. No re-download, freeze, acquire or automatic all-stage chain
is needed. Do not use --recompute to resume the unfinished first pass.

After all four pending groups finish, explicitly run the remaining gates:

```powershell
.venv/Scripts/python.exe scripts/run_phase5.py verify
.venv/Scripts/python.exe -u scripts/run_phase5.py evaluate --recompute
.venv/Scripts/python.exe scripts/report_phase5.py
.venv/Scripts/python.exe scripts/inspect_phase5_failures.py
```

The full recomputation intentionally verifies every saved source/scene target.
It was not launched at pause. Inspect real charts/failures and update the build
tracker before declaring Phase5 verified. The frozen protocol/source snapshot
is authoritative; the Phase6 sequencing waiver does not waive scientific gates.

## GPU/background context to preserve

Phases0-4 and the CUDA latency audit are verified. CPU remains default. The
optional CudaRustRunner(persistent=True) is verified; real-volume predictions
were slower on GPU. No GPU code/setup was rewritten for Phase5. Do not redo it.
RTX4070 Laptop/sm89, driver581.57, WSL Ubuntu-22.04, CUDA13.3, Rust1.98.0,
pinned NVIDIA SDK fc747196f2d46dce41bd844e3f5b1c5882751f2b under .tools/cuda-rust.
Historical GPU verifiers enforce their old package-wide science hashes; use
archived source for strict historical verification. Old runs/source archives
remain under runs/cuda-latency-audit/ and runs/phase4-source-snapshot.zip.
The GPU kernel/native binary and the acquisition scientific implementation are
unchanged. Dataset is real MSKCC-CONFOCAL C. elegans, Zenodo6460303, CC BY4.0;
CHO was replaced with user approval. Spatial lineage scores remain deferred
because s2/s3 TSV/XML positions disagree despite matching temporal graphs.
