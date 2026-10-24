# PHOTON

**See more. Illuminate less.**

Research prototype for causal, budget-aware microscopy acquisition. The hypothesis
is that adaptive sampling can preserve useful observations at equal exposure
counts. Held-out adaptive performance and biological benefit remain unmeasured.
Read [PHOTON_SPEC.md](PHOTON_SPEC.md) and [BUILD_PHASES.md](BUILD_PHASES.md) for
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
The complete suite passes85 tests. Independent quality/event evaluation is next
in Phase 5. For continuing in a new session, read [the handoff](docs/HANDOFF.md).

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
[audit](docs/mskcc-audit.md) for annotation limitations. No CTC image-use permission
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
policy. [Build evidence](BUILD_PHASES.md).

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
[model, tests and limitations](docs/gaussian-model.md) and [phase evidence](BUILD_PHASES.md).

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
benefit is claimed. See [controller details](docs/acquisition-controller.md).

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
[measured report](docs/phase3-refinement-results.md).

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
[CUDA latency audit](docs/cuda-latency-audit.md). Use
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
[kernel contract and limits](docs/cuda-rust-kernel.md), including the fixed
full-volume launch-grid failure and CPU repair behavior, are documented.

Do not commit raw datasets, credentials, or generated runs. Local datasets and
audit artifacts have been downloaded. No held-out adaptive-policy benchmark or biological
benefit has been established.
