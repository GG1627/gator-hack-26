# PHOTON / Glimpse session handoff

**Latest UI statistic:** the final-specimen/cell-health card is now **Less imaging
light:20% versus fixed**, derived from32/40 captures with equal illumination per
capture assumed. Copy mentions phototoxic stress without assigning a health
percentage. Equal-budget comparators correctly show0% less light versus fixed.
Build, seven Node tests and targeted Chromium QA pass; screenshots captured at
desktop/mobile, mobile inspected; no overflow at1440/390/320. No science changed.

## Lower-capture mode — latest checkpoint, 2026-10-25

User authorized showing a favorable measured scenario with fewer images. Default
**Fewer images** now replays saved32-image adaptive versus40-image fixed runs.
Featured precursor seed304:4/4 divisions versus1/4,20% fewer exposures. It was
selected after evaluation for demonstration; seed selector/cohort disclosure say
so. All six seeds301–306 and three scenarios remain accessible. Cohort precursor
23/24 versus11/24; sudden4/24 versus11/24. Fixed32 comparator and original40/40
**Equal budget** mode remain. No algorithm/scenario/results were changed.
Cell health is unmeasured;20% less imaging light assumes equal dose per capture.

`scripts/export_controlled_budget_demo.py --cuda` verifies the portable probe and
exports committed `apps/web/public/demo/controlled/budget32/` assets.72 rows checked,
36 actual GPU batches/sample CPU parity passed (max1.19e-7),26.7s internally.
Production build, seven Node tests,14 focused Python tests and Chromium QA pass.
Browser QA checks all18 metric combinations, modes/comparators/resets/evidence
gating/causal displays/model view/reduced motion/five widths. Default playback22.069s;
desktop/mobile screenshots inspected. Phase5 frozen registration still passes.
Full evidence and reproduction: [LOWER_CAPTURE_DEMO.md](LOWER_CAPTURE_DEMO.md).
No new long benchmark launched; existing preview on127.0.0.1:5174 may be reused.
Phase6 human comprehension, real archive refresh and Phase7 readiness remain open.

## Latest simplification — 2026-10-25

User approved the capture animation and requested removing recent-capture strips.
Strips and their styles are removed. Constant-speed shared-clock playback is now
default; optional capture pauses are explicitly a viewing aid. Introductory
comparison copy says both methods share240 frames and40 images while differing
in acquisition timing. Both still use the original saved schedules/metrics.
Build, seven Node tests and targeted Chromium checks pass (full playback21.091s,
shared clocks, capture animation, evidence gating, resets, adverse/quiet scenarios,
reduced motion, five widths320–1440). Desktop/mobile screenshots inspected.
Local checker: `.tools/glimpse-clock-check.cjs`; screenshots `glimpse-clock-*.png`.
This supersedes the recent-capture/guided-default descriptions below.

## Capture-clarity update — 2026-10-25

User requested clearer/smoother captures and asked about fewer images and estimated
health. Approved styling is preserved; capture sweeps, guided dwell, capture numbers,
explicit no-exposure states, four inspectable acquired-image thumbnails, timeline
marker, Quick playback and end-result exposure bars are implemented. Original
40-image experiment/metrics unchanged. Guided completion28.919s. Production build,
seven Node tests, six focused Python tests and the complete Chromium interaction
loop pass; five widths320–1440, reduced motion and unfavorable conditions checked.
Screenshots inspected. See [DEMO_CAPTURE_CLARITY.md](DEMO_CAPTURE_CLARITY.md).
Preview server started at `http://127.0.0.1:5174/`; reuse if still listening.

A predeclared separate probe used32 adaptive images versus fixed32/fixed40,
unchanged algorithm, new seeds301–306 and all three conditions. Precursor23/24
versus8/24 and11/24; abrupt4/24 versus8/24 and11/24.72 comparisons completed16.3s;
all rows/source/metrics independently checked12.8s; compact source/results preserved.
See [CONTROLLED_BUDGET_RESULTS.md](CONTROLLED_BUDGET_RESULTS.md). No lower-budget
mode has been substituted into the demo. No published cell-health coefficients
transfer to these data; UI states equal-light-per-capture dose assumption and leaves
health unmeasured. Frozen Phase5 registration still passes. Phase6 human comprehension,
research archive refresh and Phase7 readiness remain outstanding.

## Reviewed continuation checkpoint — 2026-10-25

**Phase 5 is complete and verified.** The user-run wrapper finished all five
stages at 00:47:23 EDT. Full source recomputation is exact across six conditions /
36 runs, all 36 generated report cards match the benchmark, and a fresh
`scripts/run_phase5.py verify` passed during continuation. The comparison chart
and representative win/loss panels were inspected. No benchmark was restarted.
See [PHASE5_RESULTS.md](PHASE5_RESULTS.md) for results, evidence and limitations.

Fixed covers more real annotated divisions in all six conditions. PHOTON's
raw-hold MSE is lower on pairwise-common withheld targets in five of six conditions,
but fixed wins on each schedule's own withheld targets in all six. Gaussian
forecast MSE loses to raw hold in all 36 runs. This is the older frozen controller;
the newer controlled-demo controller has not been validated on these held-out embryos.

The approved primary synthetic demo and sculptural hero remain unchanged.
The optional real-data archive still uses a partial export; do not claim it now
displays the complete benchmark. Next useful implementation: update/test the
checkpoint-bound exporter to consume verified completed results, then refresh
research evidence without repeating full-volume scoring. Phase 6's human
comprehension gate remains open; Phase 7 submission/reproducibility work remains.
No model escalation is needed for documentation or routine export integration.

This checkpoint supersedes historical live/paused/incomplete Phase 5 status below.

## Account switch checkpoint — start here

The user approved the current appearance and flow and requested committing/pushing
all work before switching accounts. Continue in the same workspace if possible:
`C:\Users\gael8\Coding\gator-hack-26`, branch `main`, remote
`https://github.com/GG1627/gator-hack-26.git`.

- **Approved product:** sculptural 3D hero; controlled synthetic replay is the main
  demo. At frame 239 a large results panel opens automatically. Default seed 2026
  captures 4/4 divisions vs fixed 3/4, with 40 images each, 83.3% fewer captures
  than all-frame imaging for both, and eight final simulated nuclei. Health is
  unmeasured. All six seeds, phase controls and unfavorable scenarios remain available.
- **Measured cohort:** cued events new 24/24 vs fixed 12/24 (shifted 13/24,12/24)
  and old controller 12/24. Abrupt events new 6/24 vs fixed 12/24. These are
  controlled observations, not biological/real-microscopy claims.
- **User constraint:** do not start hour-long tests. New benchmark batches are
  bounded to 120 seconds. The user has not requested stopping the existing Phase 5
  process; do not duplicate/restart/interrupt it.
- **Live Phase 5:** wrapper PID55068 was confirmed alive at this checkpoint,
  step 3/5 independent score recomputation. The log records s3/B27 complete,
  followed by another scoring group at t125/269. Check current status/log rather
  than trusting these historical indices: `runs/phase5-runner/status.json` and
  `latest.log`. Frozen source registration last passed. Do not modify/add files in
  `services/science/photon` or `services/science/tests` while it remains registered.
- **Completed experiments:** watershed and appearance probes are complete; do not
  restart them. Sources/results/limitations are in the linked research documents.
- **Verified frontend:** production build, seven Node tests, full-playback automatic
  completion, replay/reset, accurate adverse/quiet results, gated evidence,
  real archive navigation and mobile widths down to 320 passed. Screenshots inspected.
  Local browser scripts/screenshots live in ignored `.tools/`.
- **Portable demo:** the 56 files in `apps/web/public/demo/controlled/` are intentionally
  included in Git (about 10 MB). Only this generated demo directory is unignored.
  `docs/evidence/controlled-heldout-v1/` preserves compressed measured results,
  source archive, protocol and export verification. The main demo works independently
  of the optional real-microscopy manifest.
- **Local-only state:** `.venv`, `.tools`, `data`, `runs`, `node_modules`, GPU binaries
  and the large real-microscopy display exports remain ignored. Account switching
  on this laptop preserves them. A fresh checkout needs dependencies and real-data
  assets rebuilt only to use the optional research archive or rerun experiments.

Run the portable frontend with `npm.cmd ci` followed by `npm.cmd run dev -- --port 5174`
from `apps/web` (reuse the existing server if already listening). Existing local URL:
`http://127.0.0.1:5174/`. See README for Python/data setup. For the small scientific
check use `.venv/Scripts/python.exe -m pytest tests/test_controlled_event_focus.py -q`;
do not launch the full registered runner again. Next work should follow the user's
next request; the approved demo needs no further redesign or speculative features.

Sections below retain historical checkpoints; this account-switch checkpoint
supersedes conflicting statements about paused/running/completed jobs or next steps.

## Current instruction and phase status

**Latest frontend update:** controlled replay is the main demo. At frame 239 it
automatically reveals a large run-specific results screen: coverage, image count,
exposure-count proxy and final synthetic specimen state. Results do not substitute
six-seed aggregates for the selected run. Replay resets the result panel. Real
microscopy is preserved in collapsed `#real-study`; Research opens that archive.
Introduction + demo no longer depend on loading the real-data manifest. Production
build and actual end-to-end completion/browser checks pass, including adverse and
quiet scenarios and five widths. Desktop/mobile finish screenshots inspected.
No new scientific jobs were needed. Cell health is explicitly unmeasured.

**Current priority: bounded event-focused controlled demonstration.** User explicitly
authorized controller/evaluation redesign and synthetic demonstrations with accurate
measurements, then required avoiding hour-long tests. New code lives outside frozen
Phase 5 sources. `experiments/controlled` implements image-derived shape-triggered
bursts; `scripts/run_controlled_benchmark.py` limits each batch to 120 seconds.
The completed six-seed run took 19.3 internal seconds: precursor coverage 24/24
versus 12/24 standard fixed, 13/24 and 12/24 shifted fixed, 12/24 old adaptive.
Abrupt events expose the limitation: new controller 6/24 versus fixed 12/24.
See [CONTROLLED_EVENT_FOCUS.md](CONTROLLED_EVENT_FOCUS.md). Six focused tests pass.
All 90 metric rows/source images/traces were checked by the exporter; 54 actual
CUDA Rust fit-render batches passed sampled CPU comparisons. Export took 55.6s.
`ControlledLab.tsx` adds a separate synthetic interactive comparison above real
microscopy. Production build and seven Node tests pass. Chromium checked the lab's
full interaction/evidence flow, five responsive widths, and the original real-data
replay regressions. Desktop/mobile screenshots were inspected. Full Phase 5
registration still passes. Hero appearance is preserved; its CTA now opens the lab.
Original Phase 5 wrapper PID55068 remains untouched, last observed in step 3/5.
Do not restart either completed real-data ablation. Older "next" notes below are historical.

**Latest: the six-target appearance probe has completed.** Source images produced11
eligible comparisons; watershed acquired261, which was excluded as registered.
Appearance correction loses to raw hold on MSE and MAE in all11 cases. Sources,
image hashes, histories and exclusions passed verification;44 baseline scalar checks
match the earlier full-run ledger. See
[APPEARANCE_FORECAST_RESULTS.md](APPEARANCE_FORECAST_RESULTS.md) and
`runs/appearance-forecast-probe/report.md`. Recheck with
`scripts/verify_appearance_probe.py`; no volume rerender is needed for that checker.
Do not rerun either completed experiment. Original Phase5 remains active separately.
The recommendation is a targeted motion/uncertainty/budget review before further
full experiments. Current-controller capture times stayed50/54 identical after the
perception improvement. The historical “not yet run” notes below are superseded.

**Latest checkpoint: watershed ablation is complete.** `runs/perception-controller-ablation`
finished its first pass, and verification.json passes source/ledger/target/event/scalar
checks (24 sealed files). PID54664 is the completed job; do not restart it. No independent
full source rerender has been run for this experiment. Events: fixed334, adaptive325,
watershed326 of568. On212 pairwise-common targets, watershed halves Gaussian forecast
MSE versus original, but raw hold remains better. Scheduling gain is small: one event,
about0.42% lower matched raw-hold MSE. The registered development criterion passes
without establishing broad superiority. Historical live-job checkpoints below are stale.

Next: optionally generate `report_perception_ablation.py`, then run the already
registered six-target `probe_appearance_forecasts.py` against this verified input.
That selected probe has not run on microscopy yet. Avoid another full benchmark for
this next check. Original Phase5 PID55068 remains active independently in step3/5.

**Live scientific work — check before starting anything:** the authorized full detector
ablation is running at `runs/perception-controller-ablation`, PID54664, tool session87658.
All three acquisition runs have now closed. It is currently scoring saved runs
(last observed t25/269); do not duplicate it. A closed-ledger event-only audit reports
fixed334/568, original adaptive325/568, watershed326/568. Full image outcomes are pending.
The earlier acquisition-progress checkpoint below is historical.
Read its status.json/run.log and confirm the live PID. Fixed and original adaptive
acquisition runs have closed; the original schedule exactly matches the saved deployed
s1 run. Watershed was11/54 acquisitions through t41 at the last observation. Do not
start a duplicate or edit its registered sources while running. The plan is
[PERCEPTION_ABLATION_PLAN.md](PERCEPTION_ABLATION_PLAN.md). The separate Phase5 runner
PID55068 is still in step3/5, independent source recomputation.

New pipeline tests passed, including randomizing all unacquired pixels without changing
the candidate's decisions/forecasts. After first-pass completion, run
`scripts/verify_perception_ablation.py` with isolated optional dependencies on PYTHONPATH;
`--full-recompute` additionally reloads closed geometry and rerenders source scores.
Results are pending. An explicit acquisition-stage annotation-hash supplement matches
the earlier count audit. See BUILD_PHASES.md for scope, provenance and test evidence.

After completion, run the fast verifier, then generate the report with
`scripts/report_perception_ablation.py`. Independent source rerender is available via
the verifier's `--full-recompute` flag. A separately registered six-target appearance
correction probe is implemented and synthetically tested but not run on microscopy:
[APPEARANCE_FORECAST_PLAN.md](APPEARANCE_FORECAST_PLAN.md). Its CLI requires the completed
ablation and matching verification.json. It preserves acquired texture and applies
only the Gaussian-predicted change; no success versus raw hold is established yet.

**Latest instruction supersedes the earlier research-only pause:** the user left
the laptop and authorized continued research and implementation. Research/design ran
on Astra Medium; after the limit reset the environment reports GPT-6.1 Sol. The active
model cannot be switched by the agent.
Keep scientific integrity and the running Phase5 evaluator intact.

Read [GLIMPSE_DEEP_RESEARCH.md](GLIMPSE_DEEP_RESEARCH.md) for the completed primary-source
review and latest measured preflight. A new opening page is implemented in the existing
Glimpse theme: problem, conceptual acquisition diagram, experiment anchor, equal-budget
heading, and research details explaining CUDA Rust release dates and actual limitations.
Build, 7 Node tests, and desktop/mobile browser interaction checks passed.

The user's latest frontend request is implemented: a larger “See life. Spend light
wisely.” hero with explicit problem/approach copy and a custom Three.js illustration
inspired by React Bits Particles/Light Rays. It includes cursor response, a light
sweep, selectable stages, pause, reduced motion and static WebGL fallback. Six-width
browser checks, replay regression checks and production build passed. See the
[design implementation brief](design/glimpse/implementation.md) for details.
The initial particle illustration was subsequently rejected as too flat. Its
replacement uses actual sculpted3D nuclei, a transmissive membrane, studio lighting,
a moving light sheet and a wire-model transformation. Drag/keyboard rotation and
the retained motion/fallback behavior pass browser checks; current screenshots are
listed in the design brief. This remains conceptual artwork rather than run data.

New `scripts/audit_perception_counts.py` reads only saved s1 development metadata and
XML spot counts. Four tests passed. At frame260, 17 accepted Gaussian components versus
541 annotated spots, with1954 size rejections, prioritize a detector audit. These are
not segmentation recall or proof of merged nuclei. Before installing CellposeDINO,
separate small/large rejections and inspect intensity/background drift on acquired s1
volumes. No frozen scientific algorithm, pretrained model, or frozen run was modified.

**Subsequent authorized implementation:** the region audit confirmed an oversized
merged region at t260 contains99.4784% of thresholded foreground and gets discarded.
Added an isolated classical watershed candidate in `experiments/perception/watershed.py`;
the main policy does not import it. Five-frame acquired-s1 fitting comparison improved
MSE on four frames and matched t0; t2600.02935190→0.00867538. This is in-sample fitting,
not forecast or scheduling improvement. Initial10 targeted tests passed. See
[PERCEPTION_EXPERIMENT.md](PERCEPTION_EXPERIMENT.md) for defaults, results, caveats,
isolated dependencies and reproducible commands. The subsequent six causal sparse-history
probes improved Gaussian MSE in all six, but raw hold beat both models in all six.
Candidate MAE improved in three of six. The11 targeted tests now include tracker/input
isolation. Full policy ablation and spatial/manual validation remain necessary.
Phase5 has now completed s3/B54 first-pass scoring and
started s3/B89, still step1/5; recheck live status before any further action.

[GLIMPSE_ELEVATION_RESEARCH.md](GLIMPSE_ELEVATION_RESEARCH.md) retains earlier discussion
and historical continuation prompts; its research-only restrictions are superseded
by the latest user authorization. No biological benefit or overall superiority has
been established. Avoid invented damage/death outcomes.

**Phase 5 has been manually resumed by the user**, using the standalone background
runner. At this handoff check, Python PID55068 existed, step1/5 was active, and the
log had reached evaluation t125/269 in s3/B89. Full frozen registration passes,
including complete file inventory and aggregate science hash. An earlier check only
compared the37 original files and missed the additional experimental module; it was
moved outside the frozen package before the next runner stage. Original experiment
source snapshots were preserved with exact recorded hashes. Recheck `runs/phase5-runner/status.json` and
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
