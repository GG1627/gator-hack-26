> This preserves the detailed pre-submission README as an engineering record. Commands run from the repository root unless stated otherwise. Phase-specific statuses and older Glimpse interface instructions are historical; use the [current README](../README.md) for the primary Peekaboo demo and [current results](PHASE5_RESULTS.md) for completed real-data findings.

# Scientific implementation and reproduction notes

**See more. Illuminate less.**

Research prototype for causal, budget-aware microscopy acquisition. The hypothesis
is that adaptive sampling can preserve useful observations at equal exposure
counts. The completed held-out benchmark favors fixed sampling on event coverage
in all six conditions; exact source-score recomputation is verified. Biological
benefit has not been measured. See [Phase5 results](PHASE5_RESULTS.md).
Read [PHOTON_SPEC.md](../PHOTON_SPEC.md) and [BUILD_PHASES.md](../BUILD_PHASES.md) for
requirements and verified progress.

Phase 0 is verified. Phase 1 implements validated TIFF loading, causal replay,
fixed/random baselines, JSON traces, timelines and acquired-image contact sheets.
**Phase 1 is verified.** MSKCC-CONFOCAL replaces unavailable CHO with user approval.
The complete 270-volume development window is validated; fixed and random policies
each acquire 54 volumes, with identical repeated artifacts. **Phase 2 is verified:**
observed-pixel Gaussian fitting, CPU rendering, causal tracking/prediction and
heuristic uncertainty work end to end. A real withheld
development-frame preview loses to holding the last image; no forecasting
advantage is claimed. **Phase 3 is verified:** PHOTON and an image-change baseline
make causal, exact-budget decisions with gap constraints. The suite passes 85
tests. A bounded s1 refinement addresses early spending with pacing and robust
features; it improves the original controller but has tradeoffs against fixed
sampling. **Phase 4 is verified:** native CUDA Rust Gaussian rendering, numerical
parity and real-data CPU fallback work. The latency audit adds an optional
persistent GPU worker and faster packing. Dense small-output batches benefit
end to end; real-volume predictions remain faster on CPU, which stays default.
The85-test milestone is historical; Phase5's36-run evaluation and full source
recomputation are now complete and verified. For continuing in a new session, read
[the handoff](HANDOFF.md). The implemented Glimpse frontend and isolated
[perception experiments](PERCEPTION_EXPERIMENT.md) have separate verification
records; experimental improvements are not part of the frozen benchmark.

A separate [controlled event-focus experiment](CONTROLLED_EVENT_FOCUS.md)
now tests a redesigned controller: **24/24 synthetic precursor events captured,
versus 12/24 for standard fixed imaging**, at 40 images each across six evaluation
seeds. Shifted fixed schedules capture 13/24 and 12/24. Without warning cues the
new controller loses, 6/24 versus 12/24. The Glimpse lab exposes every seed and
condition, with actual CUDA Rust Gaussian-fit renders and separately revealed
evaluation. These controlled results do not change the real-data findings above.

The default [lower-capture demo](LOWER_CAPTURE_DEMO.md) now shows a measured
synthetic precursor example: **4/4 divisions with32 adaptive images versus1/4
with40 fixed images**,20% fewer exposures. The featured seed304 was selected after
evaluation; all six seeds remain accessible. Their aggregate is23/24 versus11/24,
and sudden-event performance is unfavorable (4/24 versus11/24). The original
equal-budget mode and fixed32 comparator remain available. Reduced imaging light
assumes equal illumination per capture; no cell-health benefit has been measured.
Both primary synthetic demos ship portable assets and need no Python/GPU at replay.

## Setup (PowerShell, Python 3.11+)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/run_experiment.py --help
.\.venv\Scripts\python.exe scripts/run_experiment.py --synthetic-output runs/phase0/synthetic.npz --seed 42
```

Choose a new output path if the fixture already exists. The NPZ contains `frames`
(8 x 32 x 32 float32 values in [0,1]) and a JSON `metadata` string declaring its
synthetic origin, seed, and scripted split index. Load with
`numpy.load(path, allow_pickle=False)`. This is simulated Gaussian test data,
not acquired living cells or an acquisition experiment. Full fixtures must never
be passed to a future controller; only the oracle may expose requested images.

On Linux use `.venv/bin/python` in place of `.venv\Scripts\python.exe`.
The lock records dependencies tested on Windows / Python 3.13.5; other platforms
have not been verified. Scientific dependencies will be added as needed.

## Phase 1 replay

Primary source: [MSKCC-CONFOCAL author deposit](https://zenodo.org/records/6460303),
CC BY 4.0. Credit Anthony Santella, Ismar Kovacevic, Zhirong Bao and Peter Hirsch
and cite the dataset DOI and associated publications. Read the
[audit](mskcc-audit.md) for annotation limitations. No CTC image-use permission
is needed for this independently licensed dataset; historical CTC-specific notes
apply only if CTC images are used later.

The following resumable download fetches only frames 0..269 and the main lineage
files from the 26.1 GB author ZIP. It uses four independent HTTP range readers,
checks exact responses and each entry's ZIP CRC, and rechecks cached files. The
development window is about 5.8 GB; allow storage and download time. Interrupted
downloads can be rerun. A corrupt existing cache fails explicitly.

```powershell
.\.venv\Scripts\python.exe scripts/download_mskcc.py --sequence s1
.\.venv\Scripts\python.exe scripts/inspect_dataset.py data/mskcc-audit/mskcc-confocal --output runs/mskcc-phase1-audit.json
.\.venv\Scripts\python.exe scripts/run_experiment.py --sequence data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1 --budget 54 --seed 42 --output runs/mskcc-phase1
```

MSKCC is the default `--dataset-id`. All 270 frames must exist and pass TIFF
validation; missing data cannot silently shorten the experiment. Native filenames
are preserved. Each image is a real 41x512x512 uint16 volume; cadence is 75 seconds,
with XYZ spacing 0.15/0.15/0.75 um from author metadata. One acquisition means
one full 41-plane volume. The loader validates/hashes the whole declared window
before creating an oracle and streams acquired volumes during replay.

The frozen split is **s1 development**, **s2/s3 evaluation**, each source frames
0..269. Later data are excluded following the authors' published motion caveat.
To prepare evaluation images later, use `--sequence s2` or `s3` in the downloader.
Do not tune using those evaluation outcomes. Only this 3D dataset family is
required; LFCT and Figshare remain optional fallback archives.

Verified local outputs: `runs/mskcc-phase1/`; source/annotation audit:
`runs/mskcc-phase1-audit.json`; artifact checks:
`runs/mskcc-phase1-verification.json`. Budget 54 includes the initial image;
both policies report an exposure-count proxy of 0.2. This measures simulated
acquisition count, not biological toxicity or a quality advantage of either
policy. [Build evidence](../BUILD_PHASES.md).

The default `--policy both` compares
fixed interval and seeded random, each acquiring **exactly B including frame 0**.
Fixed scheduling uses `floor(k*(T-1)/(B-1))`, with B=1 acquiring only frame 0.
Random scheduling samples B-1 distinct indices uniformly without replacement
from 1..T-1. Both schedules are precommitted using public metadata; neither uses
unseen image content. Seed 42 is the default. Adaptive policies are described below.

Each policy directory contains `config.json`, `decisions.jsonl`, `metrics.json`,
`timeline.txt` (`|` acquire, `.` skip), and `observed.png` (at most eight acquired
images; 3D volumes shown as maximum-intensity projections). Contact sheets use
per-acquired-frame min/max scaling only for display, not scoring. Reconstruction
and event metrics are null with reasons until their later phases.

The trusted runner owns the replay clock/oracle and gives policies only frozen
metadata and past observation history. Only the current frame can be acquired;
duplicate captures, overspending and evaluation before completion are rejected.
This isolates the supported policy API, not hostile Python code. Source files
must stay unchanged during a run. Full data validation/hashing occurs before
policy execution; within replay, only acquisitions read pixels. Annotations are
read only by the separate offline audit tool and are absent from policy inputs.

## Phase 2 Gaussian prediction

After downloading s1, run the predeclared sparse preview and offline artifact checks:

```powershell
.\.venv\Scripts\python.exe scripts/run_prediction_demo.py --output runs/mskcc-phase2
.\.venv\Scripts\python.exe scripts/verify_prediction_demo.py
```

Choose a new output directory if it already exists and pass that directory to the
verifier with `--run`. Acquisitions are frames 0, 5, 10; prediction is frame 12.
The complete replay closes before the evaluator reveals frame 12. All fitting,
tracking, prediction and error calculations use 3D volumes. `comparison.png` shows
maximum-intensity projections with measured, predicted and evaluation-only labels.
Normalization is fixed by frame 0. `prediction.npz` and `evaluation_truth.npz`
are separate; neither full sequences nor labels reach the model.

Actual single-frame normalized MSE: Gaussian forecast **0.00114925**, hold-last
**0.00103832**. On the common foreground ROI: **0.01256874** versus **0.01050487**.
The forecast is worse on both. Simplified Gaussians miss texture/diffuse signal;
uncertainty is heuristic, and bright components are not validated nucleus counts.
This preview is not an adaptive-policy benchmark. See the
[model, tests and limitations](gaussian-model.md) and [phase evidence](../BUILD_PHASES.md).

## Phase 3 adaptive acquisition

```powershell
.\.venv\Scripts\python.exe scripts/run_experiment.py --sequence data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1 --budget 54 --seed 42 --policy all --controller-variant original --min-gap 2 --max-gap 12 --output runs/mskcc-phase3
.\.venv\Scripts\python.exe scripts/verify_adaptive_runs.py --require-current-code
.\.venv\Scripts\python.exe scripts/build_schedule_replay.py
```

Choose a new experiment output if it already exists; pass that root to subsequent
commands using `--runs`. For the animation also choose a new `--output` GIF path.
`--policy all` runs fixed, seeded random, PHOTON and image change with exactly the
same B including frame 0. Adaptive policies enforce inter-capture min/max gaps and
terminal age <=max_gap; impossible settings fail before any run begins. The
original random baseline remains unconstrained by those gaps. Physical spacing
is required for real adaptive microscopy; synthetic fixtures may use unit spacing.

The controller scores heuristic position uncertainty, observed motion, unvalidated
morphology/split hints, elapsed gap and budget remaining. It receives only acquired
observations. Every decision records its pre-acquisition inputs, priority and
reason; the feasibility guard can override priority to reserve future coverage.
Image change is a separate baseline using changes between acquired pixels only.
Scores are not biological event probabilities. Configuration/model state and
source/code versions are saved with each run.

Historical original run: all four acquire **54/270**. PHOTON gaps range **2–12 frames**,
and a repeated run produces six byte-identical artifacts. Its many early captures
leave mostly maximum-gap captures later; this is a known weakness. Quality/event
scores in those scheduling artifacts remain null. The development refinement below
adds actual evaluation without replacing historical evidence. No biological
benefit is claimed. See [controller details](acquisition-controller.md).

Open `runs/mskcc-phase3/replay.gif` for the completed fixed/PHOTON animation.
Each panel shows its own last acquired measurement, explicitly held at skipped
times; these are neither predicted images nor revealed withheld truth. The
animation manifest records all image indices read. Full interactive UI remains
Phase 6. Repeat verification can be requested with
`--repeat runs/mskcc-phase3-repeat` after rerunning PHOTON there.

### Bounded refinement and current default

The current PHOTON default is `paced_robust`. It limits discretionary budget lead
to two captures, replaces maximum elongation with mean clipped elongation, and uses
median speed from repeatedly observed tracks. Hard feasibility overrides pacing
when required. `--controller-variant original` retains the first controller;
`paced` and `robust` expose the two ablations. Image change keeps its original settings.

Actual s1 development comparison, B54, event tolerance +/-1 source frame:

| Method | Event coverage | Common-target raw hold MSE | Own-withheld raw hold MSE |
|---|---:|---:|---:|
| Original PHOTON | 192/568 (33.80%) | 0.003014881 | 0.002712791 |
| Refined PHOTON | 325/568 (57.22%) | 0.002396867 | 0.002163087 |
| Fixed | 334/568 (58.80%) | 0.002593877 | 0.002112048 |

Common errors use the exact110 times withheld by all five compared schedules.
Own-withheld errors use216 times per method with differing timestamps. Fixed has
better event coverage and own-withheld error; refined PHOTON has better common-target
hold-last error. There is no overall superiority claim. Gaussian forecasts remain
much worse than raw hold-last and slightly worse than holding a Gaussian fit.
All labels/truth were revealed only after all five causal runs closed. No s2/s3
evaluation or post-score parameter search was used. The declared selection rule,
all ablations, foreground errors and limitations are in the
[measured report](phase3-refinement-results.md).

```powershell
.\.venv\Scripts\python.exe scripts/run_experiment.py --sequence data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1 --budget 54 --seed 42 --policy photon_adaptive --output runs/mskcc-phase3-refined
.\.venv\Scripts\python.exe scripts/run_phase3_refinement.py
.\.venv\Scripts\python.exe scripts/verify_refinement.py --sequence data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1
```

Choose fresh output paths for reruns. The five-run development experiment exports
causally saved Gaussian geometry and full3D per-frame scores. To rerender all saved
geometry and verify every score, use `run_phase3_refinement.py --recompute` with
the same `--output` root. The executed verification independently aggregated all
scores and exactly rerendered targets1/174/268 for all five variants. A second full
rerender was not performed. Exact comparison source is preserved in the ignored
`runs/mskcc-phase3-refinement/source-snapshot.zip`. The deployed default reproduced
the chosen variant's decisions and final state byte-for-byte.

`runs/mskcc-phase3-refinement/fixed-vs-combined.gif` shows the real completed
comparison using acquired measurements only. This experiment is development
selection, not a held-out benchmark or evidence of improved cell viability.

Historical artifact verifiers report whether their recorded code hash matches the
current source; `--require-current-code` enforces a match. Phase 2's stored forecast
remains valid historical evidence as the controller code evolves.

## Layout and GPU status

- `services/science/photon`: importable science code.
- `services/science/tests`: synthetic and CLI checks.
- `scripts/run_experiment.py`: repository entry point.
- `docs/experiment-log.md`: commands, environment, failures, references.
- `data/`, `runs/`, `.tools/`, and environments: ignored local artifacts.

CUDA Rust **hello-world and SAXPY execution are verified** on the RTX 4070 Laptop GPU in
WSL2 using Linux CUDA Toolkit 13.3 and NVIDIA's pinned Rust 1.98.0 toolchain.
The initial missing-toolkit blocker is resolved. To reproduce from the ignored
upstream checkout:

```bash
source ~/.cargo/env
export CUDA_TOOLKIT_PATH=/usr/local/cuda-13.3
cd /mnt/c/Users/gael8/Coding/gator-hack-26/.tools/cuda-rust/cutile-rs
cargo run -p cutile-examples --example hello_world
cargo run -p cutile-examples --example saxpy
```

SAXPY passed all32 exact CPU/GPU assertions and was rechecked in Phase4. PHOTON
now also has its own native Rust-written Gaussian accumulation kernel, using
the pinned cuTile0.5.0 upstream revision. It supports checked2D/3D batches,
anisotropic covariance and the original normalization/truncation/clipping.

```powershell
.\.venv\Scripts\python.exe scripts/build_gpu.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/benchmark_gpu.py --output runs/phase4-benchmark-verified
.\.venv\Scripts\python.exe scripts/run_phase4_experiment.py --backend cuda-rust --output runs/phase4-real-gpu-verified
.\.venv\Scripts\python.exe scripts/verify_phase4.py
```

The build helper requires the working Linux Rust/CUDA13.3 setup above; it fetches
NVIDIA's pinned source if absent, verifies the revision, and builds the release
binary. Use `--offline` only if Cargo dependencies are cached. `--debug` is for
development, not benchmark reports. Windows uses WSL Ubuntu-22.04 by default;
override `PHOTON_WSL_DISTRO` if appropriate. The built binary/cache stays under
ignored `.tools/`. Fresh output directories are required for each experiment.
The benchmark's real-state case uses the Phase3 saved s1 state at260, so that
development artifact must exist first.

`photon.gpu.render_gaussian_batch(..., backend="cuda-rust")` explicitly requests
the native engine; `backend="auto"` permits a logged CPU fallback. The default
is CPU. `model.predict(t, include_uncertainty_map=True, backend="cuda-rust")`
batches mean/ensemble rendering and records actual backend on `PredictedFrame`.
The kernel receives Gaussian parameters only; it never sees raw frames or labels.

Historical one-shot bridge medians on this RTX4070 Laptop via WSL2 (milliseconds):

| Workload | CPU reference | Warm CUDA device interval | Full Python/WSL caller |
|---|---:|---:|---:|
|100 Gaussians,64x64 |33.24 |0.214 |1984.30 |
|10000 Gaussians,64x64 |3087.02 |19.82 |5291.01 |
|Real s1 state,41x512x512,17 Gaussians |85.68 |49.30 |5335.46 |

**The original one-shot bridge had no measured end-to-end speedup.** Warm GPU arithmetic is faster, but context,
JIT/cache preparation, packing, files and transfers dominate this bridge.
Production renders once; warm profiling repetitions are a separate mode. CPU
uses local bounding boxes while GPU evaluates the full grid, so work counts
differ despite equivalent outputs. Raw timing samples, compilation/transfer
details, memory counters and the standalone chart are in
`runs/phase4-benchmark-verified/`. Kernel-only ratios must not be shown as app speedups.

For repeated rendering, an opt-in persistent worker retains the CUDA context and
cuTile process cache. Keep the runner alive for the whole prediction workload:

```python
from photon.gpu import CudaRustRunner

with CudaRustRunner(persistent=True) as runner:
    prediction = model.predict(t, include_uncertainty_map=True,
                               backend="auto", runner=runner)
```

`auto` records unavailable-worker CPU fallback. Explicit `cuda-rust` raises when
unavailable. CPU remains the default; the acquisition controller's scalar scores
and acquired-image fitting remain CPU in either mode. Worker startup/first JIT
costs must be amortized. Reproducible cold/warm/p95/full-caller and causal-path
benchmark commands, protocol and limitations are in the
[CUDA latency audit](cuda-latency-audit.md). Use
`scripts/verify_gpu_latency.py` for that follow-up's evidence. The original
`verify_phase4.py` enforces the original snapshot's exact code/binary hashes.

On real withheld targets1/134/268, maximum GPU/CPU pixel difference is1.79e-7
(tolerance rtol2e-4/atol2e-5). GPU and deliberate unavailable-GPU fallback runs
each acquire54/270 with byte-identical decisions/state to the CPU experiment.
The renderer uses FP64 geometry and FP32 values. Hard-cutoff ambiguity triggers
the exact original CPU scene routine for reference repair; that cost is logged.
This does not improve forecasting accuracy or change the controller.

To exercise fallback on the same real input without changing the binary:

```powershell
$env:PHOTON_GPU_BINARY = Join-Path (Get-Location) '.tools/photon-gpu/intentionally-unavailable'
.\.venv\Scripts\python.exe scripts/run_phase4_experiment.py --backend auto --output runs/phase4-real-cpu-fallback-verified
Remove-Item Env:PHOTON_GPU_BINARY
.\.venv\Scripts\python.exe scripts/verify_phase4.py
```

The verifier expects the GPU run, fallback run and benchmark roots shown above;
use its arguments for other output roots. It independently checks recorded
latencies, saved predictions, source-frame errors, exact schedules/state and
binary/code versions. All truth reads happen after replay closure. Detailed
[kernel contract and limits](cuda-rust-kernel.md), including the fixed
full-volume launch-grid failure and CPU repair behavior, are documented.

## Held-out scientific evaluation (Phase 5)

**Paused / incomplete by user request:** all36 acquisition trajectories and
event audits are saved; image scoring is complete for s2/B27 and s2/B54 only.
Global verification and full source recomputation have not started. See the
[current checkpoint and manual resume instructions](HANDOFF.md).
Phase6 may start early with authentic artifacts labeled partial/pending.
Do not launch further scoring automatically.

The [frozen evaluation plan](phase5-protocol.md) uses s1 for development
and reserves s2/s3 for independent evaluation. Complete their source windows
with the existing downloader before validating and freezing a new benchmark:

```powershell
.venv/Scripts/python.exe scripts/download_mskcc.py --sequence s2 --workers 4
.venv/Scripts/python.exe scripts/download_mskcc.py --sequence s3 --workers 4
.venv/Scripts/python.exe scripts/run_phase5.py validate-data
.venv/Scripts/python.exe scripts/run_phase5.py freeze
.venv/Scripts/python.exe -u scripts/run_phase5.py acquire
.venv/Scripts/python.exe -u scripts/run_phase5.py evaluate
.venv/Scripts/python.exe scripts/run_phase5.py verify
.venv/Scripts/python.exe -u scripts/run_phase5.py evaluate --recompute
.venv/Scripts/python.exe scripts/report_phase5.py
```

The default output is ignored `runs/phase5/`. Freeze refuses to overwrite an
existing protocol. Acquisition can resume completed, hash-checked trajectories;
partial outputs require inspection. Evaluation starts after all36 runs close.
It writes trusted `benchmark.json`, per-run metrics/error sums and a standalone
chart/report; full recomputation uses saved causal scenes and source volumes,
without executing policies. The report's card data is checked directly against
the trusted JSON. No Phase6 UI is implemented by these commands.

Three budgets27/54/89, two embryos, all three random seeds and raw-hold/held-fit/
Gaussian forecast estimators remain visible. Random shares capture counts but
has no adaptive gap constraint. Reconstruction target-set caveats and event
coverage definitions are explicit in the protocol. No biological phototoxicity
benefit is established by capture counts.

Historical GPU verification scripts enforce the science/binary hashes recorded
in their audit snapshots. Phase5 adds scientific source files, changing the
package-wide science hash; use the corresponding archived source for strict
historical verification. The GPU implementation and native binary are unchanged.

Do not commit raw datasets, credentials, or generated runs.

## Local interactive replay (Phase 6)

The React + TypeScript viewer consumes the existing closed Phase 5 artifacts.
It does not resume Phase 5, fit models, execute policies, or recompute metrics.
Both held-out embryos, budgets 27/54/89, fixed/image-change/random comparisons,
and saved causal PHOTON Gaussian predictions are supported.

From the repository root, export authentic local assets once:

```powershell
.venv/Scripts/python.exe -u scripts/build_phase6_assets.py
.venv/Scripts/python.exe -u scripts/build_glimpse_spatial.py
```

This checks frozen source, closed-run and paused-checkpoint metric hashes, then
projects the source volumes and renders saved full 3D Gaussian scenes on CPU.
It can take several minutes. It writes only ignored `apps/web/public/demo/`;
raw data, original run artifacts and scientific modules remain untouched.
The exporter refuses an existing output directory. To regenerate, move the
old export to another local directory first, or choose a fresh `--output`.
An interrupted export has no `manifest.json` and is not usable by the viewer.

With Node.js 22.12+ or 24 installed:

```powershell
cd apps/web
npm ci
npm test
npm run dev -- --port 5173 --strictPort
```

Open <http://127.0.0.1:5173>. The **Glimpse** demo implements the selected
[E / Contact design](design/glimpse/round-2/README.md). The initial screen
is explicitly labeled a recorded midpoint preview; the first **Play** starts
at frame 0. Scrub, click an acquired thumbnail, or open **Experiment settings**
to choose an embryo, budget and comparison. Both acquisition strips use the
same moving 72-frame window and source clock. Sequence/budget changes pause
playback, reset to frame 0 and close evaluation.

**Spatial** shows a deterministic sample of actual acquired voxels, held until
the next acquisition. **Gaussians** shows the saved model fit or causal forecast
with full physical covariance: GPU-projected splats and shaded 2-sigma component
contours. These contours are model geometry, not validated cell boundaries.
**Microscope** and **Show acquired image** expose the policy's own last measured
maximum projection. Drag/scroll or use arrow keys and +/- to inspect the 3D view;
Home resets it. Missing 3D assets or WebGL retain the microscope fallback.

The spatial exporter reads saved fits/forecasts without executing fitting or
policies. It checks frozen hashes and exports physical XYZ micrometers. Source
voxel sampling uses ZYX stride 1/3/3, first-image normalization, signal threshold
0.2 and a deterministic cap of 12,000 points. Depth colors and transparency are
display choices. This orthographic browser projection differs from the frozen
CPU full-volume renderer used for scores; original CPU projections remain linked
under **Research details**. See the [rendering contract](design/glimpse/implementation.md).

**Reveal evidence** explicitly opens evaluation-only images, annotations,
differences and metric tables; **Close evidence** seals the display again.

Image scores exist only for s2/B27 and s2/B54 and are labeled **first-pass /
source rerender pending**. The other conditions show **pending**, not zero.
All event audits are real: fixed sampling covered more annotated divisions than
PHOTON in all six held-out conditions. Own-withheld and matched-target scores
are separate. Capture savings are relative to imaging every source volume;
fixed and PHOTON have equal image budgets. No biological benefit is measured.

Build and serve without a science backend after export:

```powershell
npm run build
npm run preview -- --port 4173 --strictPort
```

The build includes the local export. Keep generated microscopy assets out of
Git; no hosted deployment is required. Dataset attribution and source JSON
links are available under **Research details & provenance**. Missing exports
produce a setup message; missing images produce an explicit error state.

Exporter tests (from the repository root; authentic-export check requires assets):

```powershell
.venv/Scripts/python.exe -m pytest -q tests/phase6
```

The human ten-second comprehension check remains a Phase 6 acceptance gate.

The UI bundles Three.js 0.186.1 and Manrope Variable 5.3.0; licenses are included
under `apps/web/public/third-party/`. `apps/web/tests/browser-geometry.cjs` is a
Playwright CLI `run-code --filename` fixture for a running dev preview: it checks
the actual GPU shader against an independent analytic covariance projection.
