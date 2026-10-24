# PHOTON session handoff

The next task is **Phase5: scientific benchmark and post-hoc validation**.
Phases0–4 and the subsequent CUDA latency investigation are verified. Phase5
has not started; do not mark it complete based on development-only evidence.
Read `AGENTS.md`, `PHOTON_SPEC.md` and `BUILD_PHASES.md` before implementation.

## Workspace and persistence

- Local checkout: `C:\Users\gael8\Coding\gator-hack-26`.
- GitHub remote: `https://github.com/GG1627/gator-hack-26.git`, branch `main`.
- Changing Codex accounts on the same computer does not require recreating the
  repository or environment. Reopen this existing directory.
- Source, tests, lockfiles and documentation are versioned. `.venv/`, `.tools/`,
  `data/`, `runs/`, caches, native binaries and credentials remain ignored.
  Do not force-add these directories. A fresh clone needs its own environment,
  dataset downloads and regenerated experiment artifacts.
- Use `.venv/Scripts/python.exe` from PowerShell. Python3.13.5, NumPy2.5.4,
  SciPy1.18.1; installed dependency versions are in `requirements-dev.lock`.

## Scientific state to preserve

- CHO was unreachable and was replaced with user approval by **MSKCC-CONFOCAL**,
  real3D+t C. elegans confocal microscopy, Zenodo6460303, CC BY4.0.
- Frozen experiment window: source frames0..269,41x512x512 uint16 volumes,
  75-second cadence, XYZ spacing0.15/0.15/0.75um. A capture is a complete volume.
- `mskcc_confocal_s1` is development. `s2` and `s3` are held out. The full s1
  image window is local under
  `data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1/images/`.
  s2/s3 have audited annotations and image samples; verify and download their
  complete declared windows before evaluation. Start with
  `scripts/download_mskcc.py --help` and `docs/mskcc-audit.md`.
- Canonical event definition is a binary division in the curated MaMuT graph:
  first daughter frame of a parent with exactly two immediate children. The
  first270 frames contain568/560/567 events in s1/s2/s3. These counts are dataset
  annotation facts, not PHOTON detection results. Spatial annotation differences
  mean positional tracking scores remain deferred.
- Controller: frozen default `paced_robust` in `photon/adaptive.py`, exact budget
  including frame0, min gap2/max gap12 with terminal coverage and an integer
  feasibility check. Review configuration/feasibility before each chosen budget.
- Policies see metadata and acquired observations only. Future pixels and
  annotations stay in the sealed oracle/offline evaluator. Evaluate only after
  replay closure. Keep predictions distinct from measured images.
- Development refinement improved the original controller but did not establish
  universal superiority to fixed sampling. Gaussian forecasts are weaker than
  holding the last raw observation in existing development tests. Retain fixed,
  random, image-change and raw-hold comparisons; report losses honestly.
- Freeze the evaluation protocol (budgets, seeds, event tolerance, normalization,
  masks and metric definitions) before reading held-out outcomes. Do not tune on
  s2/s3 or feed evaluation results back into their controller trajectories.
- Acquisition count is an exposure proxy. No biological phototoxicity benefit
  or held-out adaptive improvement has been established.

## Latest verified implementation

- 85 Python tests passed in63.34s. Native `cargo fmt --check` and one checked-input
  unit test passed. `scripts/verify_gpu_latency.py` independently passed.
- A real270-step replay preserved54 acquisitions, all decision fields and final
  state. GPU/CPU prediction max difference1.79e-7; map difference8.94e-8.
- The actual scheduler and acquired-image fitting remain CPU. Decision median
  0.0234ms; fitting median1282.6ms. Rendering is not in the acquisition score.
- Optional `CudaRustRunner(persistent=True)` retains WSL process/CUDA context/
  cuTile cache; vectorized host packing and1MiB output buffering are implemented.
  The Rust CUDA kernel itself is unchanged. CPU remains the default and `auto`
  fallback is logged; explicit CUDA errors are not presented as CPU success.
- Dense64x64 synthetic full-caller warm crossover lies between400–600 Gaussians.
  Real-volume CPU rendering/prediction wins in every measured case. Do not infer
  application speedup from resident graph/kernel timing. See
  `docs/cuda-latency-audit.md` for raw-sample methodology and median/p95 results.
- Same-machine GPU setup already works: RTX4070 Laptop, sm89, driver581.57,
  WSL Ubuntu-22.04, CUDA13.3, Rust1.98.0, pinned NVIDIA SDK revision
  `fc747196f2d46dce41bd844e3f5b1c5882751f2b` under `.tools/cuda-rust`.
  Do not reinstall or redo this audit without a concrete new failure/change.

Important local artifacts (ignored, still present on this computer):

- `runs/mskcc-phase3-refined/photon_adaptive/`: original refined CPU trajectory.
- `runs/mskcc-phase3-refinement/`: five development ablations and frozen scenes.
- `runs/phase4-real-gpu-verified/`, `runs/phase4-real-cpu-fallback-verified/`.
- `runs/cuda-latency-audit/`: eight-size cold/warm/transfer/full caller matrix,
  crossover sweep, packing/I/O ablations, actual causal prediction benchmark,
  saved trace/state, verification, native checks and inspected chart.
- `runs/cuda-latency-audit/source-and-evidence.zip`: CRC-checked audit snapshot.
- `runs/phase4-source-snapshot.zip`: original pre-worker implementation. The old
  `verify_phase4.py` deliberately enforces its historical source/binary hashes;
  use `verify_gpu_latency.py` for current evidence.

## Continue with Phase5

1. Read the primary docs and Phase5 completion gates in full. Inspect existing
   oracle, development evaluator, annotations, metric/export and replay code.
   Reuse it instead of scaffolding a competing pipeline.
2. Confirm local state and baseline tests. Inspect held-out image completeness
   and downloader integrity/resume behavior; obtain the full declared s2/s3
   windows before replay. Raw data stays outside Git.
3. Predeclare evaluation settings and retain the frozen controller. Compare all
   applicable policies at equal feasible budgets on held-out sequences, with
   reproducible seeds where relevant. Include raw-held observation reconstruction
   alongside Gaussian forecasts so a weak prediction model cannot be hidden.
4. Compute honest withheld-frame MAE/MSE and supported event coverage offline;
   document masks/normalization/tolerance and failure cases. Export authentic
   run configs, timelines, decisions, metrics, provenance and charts.
5. Test budget fairness, causality, missing-annotation handling, exact artifact
   metric recomputation and determinism. Update `BUILD_PHASES.md` with actual
   commands/results/blockers/decisions. Do not start Phase6 before Phase5 passes.

Useful checks (run from the existing workspace):

```powershell
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe scripts/verify_gpu_latency.py
.venv/Scripts/python.exe scripts/download_mskcc.py --help
```

Model selection is manual. Follow `AGENTS.md`; Phase5's evaluation design warrants
GPT-6.1 Sol High. Routine downloading, scripting and integration can use Sol Medium.
Do not assume a model switch occurred without user confirmation.

## Starting prompt for the new session

```text
Continue PHOTON in C:\Users\gael8\Coding\gator-hack-26 on branch main.
Read AGENTS.md, PHOTON_SPEC.md, BUILD_PHASES.md and docs/HANDOFF.md in full
before writing code. Phases0–4 and the CUDA latency audit are verified;
Phase5 scientific evaluation is next and has not started.

Use the existing workspace, environment, data and ignored run artifacts.
Inspect current code and verify the baseline, then implement Phase5
incrementally through its completion gates. Use s1 only for development;
complete and validate the held-out s2/s3 windows before evaluation. Freeze
the protocol and controller before inspecting held-out outcomes. Compare
fixed, random, adaptive and image-change policies at equal feasible budgets,
and retain raw-hold reconstruction baselines. Keep future pixels and labels
sealed from the controller, compute metrics offline after closure, and
report wins and losses honestly. Run relevant tests and update
BUILD_PHASES.md with real evidence before marking anything complete.

Keep CPU as default. The optional persistent CUDA Rust worker is verified,
but real-volume predictions remain slower on GPU. Do not redo setup or
rewrite the kernel without evidence. Do not start Phase6 until Phase5 passes.
Follow the model recommendation policy in AGENTS.md; recommend Sol High
for evaluation design, and continue useful authorized work autonomously.
```
