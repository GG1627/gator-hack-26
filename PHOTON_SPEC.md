# PHOTON — Project Specification

> **See more. Illuminate less.**  
> GatorHack V 2026 · Fresh off the Frontier · Working specification · 2026-10-23
>
> Companion build tracker: [`BUILD_PHASES.md`](./BUILD_PHASES.md)

## 0. Instructions for Codex

This document defines the project's intent, technical contracts, scientific claims, scope, and acceptance criteria. **Read this and `BUILD_PHASES.md` before coding.** Treat the build plan as a living execution log; update it after each tested phase. Do not replace verified experiments with impressive-looking simulations. If an implementation decision changes the scientific claims, update this spec and record the reason in the build plan.

**Priority order:** (1) credible end-to-end science, (2) verifiable experimental improvement, (3) use of frontier technology, (4) polished interactive demonstration, (5) extras. A beautiful demo with leaked future frames or fictitious results is a failure.

## 1. Elevator pitch

Repeated fluorescence microscopy can expose living specimens to light that causes **photobleaching and phototoxic effects**. To avoid missing events such as cell division, researchers frequently image on a fixed schedule, including when little is changing.

**PHOTON is a software-only, uncertainty-aware acquisition controller.** Given sparse real microscopy observations, it maintains an evolving Gaussian representation of cells, estimates what may happen next, and chooses **when another observation is worth its light-exposure cost**. It tests itself against withheld frames from real microscopy time-lapse data.

**Ten-second explanation:** "A microscope shouldn't have to photograph living cells all the time. PHOTON predicts when to look, so it can use fewer exposures while still catching the important changes."

**Intended users:** microscopy researchers performing live-cell, time-lapse experiments; later, microscope automation platforms. **Hackathon output:** runnable replay/controller + measured results + reproducible acquisition schedule. No microscope hardware is required.

## 2. What makes this more than an AI video interpolation demo?

The hard question is **decision-making under incomplete information**, not simply filling in pretty missing frames.

1. At time `t`, the controller only knows acquired frames at times `<= t`.
2. It maintains estimated biological state and uncertainty (with a causal Gaussian-based model).
3. It ranks a future acquisition by its expected usefulness for tracking/event coverage versus exposure budget.
4. It either **ACQUIRE**s the true frame or **SKIP**s and continues with a prediction.
5. A sealed replay evaluator later reveals the withheld real frames and scores the choices.
6. At identical acquisition counts, compare adaptive sampling with fixed intervals and other honest baselines.

**Hypothesis to test (not a promised result):** PHOTON retains more annotated events and/or lower reconstruction error than fixed-interval acquisition at the same number of exposures.

**Novelty claim for the hackathon:** closed-loop, risk-aware acquisition scheduling over a sparse spatiotemporal Gaussian cell model, with a custom CUDA-Rust implementation of performance-critical evaluation. We do **not** claim to have invented event-driven microscopy or 4D Gaussian splatting.

## 3. Fresh off the Frontier: concrete grounding

The challenge requires a technology, resource, or discovery first made public in the last 12 months, **central** to the build. Our primary candidates:

| Recent resource | Public date | Why it matters to PHOTON |
|---|---|---|
| **CellSplat4D: PSF-Aware 4D Gaussian Splatting for Sparse Robotic Live-Cell Imaging** | **Oct. 3, 2026** (arXiv) | Direct research inspiration: an evolving 4D Gaussian representation reconstructs cellular volumes at missing time points. We implement a scoped, independently testable model inspired by the concept; do not falsely claim to reproduce the full paper. |
| **NVIDIA CUDA Rust: `cutile-rs` / `cuda-oxide`** | **Sept. 8, 2026** (NVIDIA announcement; constituent tooling may predate it) | Native **Rust-written GPU kernels** for batched candidate scoring / Gaussian evaluation. We demonstrate correct results and benchmark the kernel against its CPU equivalent. |

**Important:** Original 3D Gaussian splatting dates to 2023, so "we used Gaussian splatting" alone is **not** a qualifying new technology. The 2026 microscopy-specific work and CUDA Rust must do important actual work. We should be able to show a function/result that would be absent without each component.

References:
- CellSplat4D paper: https://arxiv.org/abs/2610.04199
- NVIDIA announcement: https://developer.nvidia.com/blog/introducing-cuda-rust-two-tracks-for-writing-gpu-kernels
- NVIDIA implementation: https://github.com/NVIDIA/cuda-rust
- `cutile-rs` docs: https://nvlabs.github.io/cutile-rs/main/guide/introduction.html
- Cell Tracking Challenge: https://celltrackingchallenge.net/datasets/
- Pycro-Manager adaptive acquisition: https://pycro-manager.readthedocs.io/en/latest/adaptive_acq.html

**Use-case qualifier:** Phototoxicity is real, but our offline replay can only measure a **proxy for optical exposure** (image count, or an explicitly parameterized dose per capture). It cannot establish improved cell viability without a hardware/biological experiment.

## 4. The product experience / magic moment

A two-panel time-lapse experiment:

- **Left: conventional microscope.** Fixed-rate exposures, shown as illuminated dots on a timeline.
- **Right: PHOTON.** Captures when predicted event risk / uncertainty justifies it, shown as irregular exposure dots.
- Center stage: authentic microscopy frames and the current Gaussian prediction. Acquired images have an unmistakable **MEASURED** marker; inferred frames have **PREDICTED** plus uncertainty.
- As a cell prepares to divide, PHOTON schedules a higher density of observations **if its model actually predicts increased risk**. Stable phases can use fewer acquisitions.
- Click **Reveal ground truth** after the run to expose withheld frames, annotated events, and measured quality.
- Show a benchmark card: same image budget, event coverage, reconstruction error, and count of exposures. **Never hard-code favorable numbers**.

A judge should understand in ten seconds: fewer photographs, same budget constraints, and evidence of which strategy catches more scientifically useful events.

## 5. v1 scope (required), v2 (stretch), explicitly excluded

### Required / v1

- Work **offline on a time-lapse dataset**: no microscope hardware and no inaccessible cloud research models.
- Load at least one real **MSKCC-CONFOCAL 3D+t** sequence and its available curated lineage annotations; keep raw data outside Git. This replaces the unavailable CTC CHO requirement with user authorization (2026-10-23).
- Causal acquisition environment: future frames are inaccessible to the policy, except through the explicit `acquire(t)` interface.
- At least 3 acquisition policies: **fixed interval**, **seeded random**, **PHOTON adaptive**. A simple image-change heuristic is a useful fourth baseline.
- Respect equal frame budgets and log every acquired index. Handle initial observation and mandatory maximum-gap logic without overspending.
- A compact evolving Gaussian scene model (2D+t is an acceptable integration stepping stone, 3D+t is preferred for the final research narrative).
- One **real CUDA Rust GPU kernel** for batched Gaussian/candidate evaluation with CPU parity tests and honest timing.
- Measured results: count of acquired frames, an exposure-count proxy, withheld-frame reconstruction loss, and event coverage **only where annotations genuinely support it**.
- Interactive demonstration and reproducible JSON run artifacts, with dataset ID, split, policy, seed, config, metrics, and acquisition timeline.

### Optional v2 (only after the required gates are green)

- Full 3D+t volume rendering / PSF-aware fitting / temporal lifespan for Gaussians.
- Per-well budget allocator for multiple cultures with fairness and maximum-gap constraints.
- Uncertainty-calibrated event predictions and better nucleus identity/lineage inference.
- Export an acquisition plan to Pycro-Manager's **simulation / no-hardware** adapter.
- Agent-assisted hypothesis creation/experiment setup; agent never overrides a validated acquisition policy.

### Explicitly out of scope

- Actual live microscope controls during the hackathon.
- Claims of reduced measured toxicity / better clinical outcomes.
- Reproducing all the CellSplat4D training, microscopy PSF calibration, and 3D U-Net pipeline in 48 hours.
- General-purpose medical diagnoses, autonomous biological experiments, or undocumented "self-learning" claims.
- A large multimodal LLM, Muse, or A2A without a concrete nonreplaceable role.

## 6. Scientifically honest data plan

### Primary dataset: `MSKCC-CONFOCAL` C. elegans (3D+t)

- User-approved replacement for unavailable CHO (2026-10-23); author source: https://zenodo.org/records/6460303, DOI 10.5281/zenodo.6460303, CC BY 4.0.
- Three independent real confocal embryo movies, 400 source volumes each, 41x512x512 uint16; documented cadence 75 seconds, XYZ spacing 0.15/0.15/0.75 um.
- Freeze development sequence `mskcc_confocal_s1`; reserve `mskcc_confocal_s2` and `mskcc_confocal_s3` for held-out evaluation. Dataset QA inspected their labels; do not use held-out outcomes for model/controller tuning.
- Use the common **source frames 0..269 inclusive**. This follows the authors' existing caution about later embryonic twitching; do not select windows after observing which favors PHOTON. Download and validate all frames of each declared experiment window before replay.
- Curated binary divisions fully inside these windows: s1 568, s2 560, s3 567. These are annotation counts, not PHOTON detection results. See `docs/mskcc-audit.md` for audit scope and reproducible evidence.
- Use the MaMuT temporal graph as the canonical event definition: an event occurs at the first daughter frame for a parent with exactly two immediate children. Reject malformed graphs. Keep all annotation information in offline audit/evaluation, never controller inputs.
- TSV and MaMuT IDs/frames/edges agree; some s2/s3 positions differ. Positional accuracy scoring remains deferred. Point/lineage annotations are not full segmentation ground truth.
- One acquisition means one complete 41-plane source volume. Count volumes equally across policies; dose and biological viability remain unmeasured. Embryo results do not establish generalization to mammalian cultures.
- Phase 1 requires a full development window and a reproducible equal-budget real replay. Evaluation-window downloads may wait until Phase 5. LFCT and Figshare are optional backups, not extra required integration work.

### Historical target: Cell Tracking Challenge `Fluo-N3DH-CHO` (3D+t)

- Chinese Hamster Ovarian fluorescent nuclei; training archive approximately **98 MB**.
- Description and official links: https://celltrackingchallenge.net/3d-datasets/
- Direct training ZIP (verify access): https://data.celltrackingchallenge.net/training-datasets/Fluo-N3DH-CHO.zip
- Imaging time interval approximately **9.5 min** in the dataset description (use actual metadata and frame numbering; don't invent finer sampling).
- Download a **training** archive, inspect contents and annotation format. Check dataset terms for publication and repackaging.
- Training sequences can have sparse/unreliable division annotations. **First audit actual events.** If no sufficient reliable division labels, report that and evaluate reconstruction/trajectory preservation; select a better annotated data source for division recall.

CHO is not a completion blocker following the authorized replacement. Do not claim this prototype was evaluated on CHO unless it later becomes available and is actually tested.

### Backup / test fixture

- Synthetic, *clearly labeled*, small time-lapse with scripted Gaussian nuclei and known splits: ideal for unit tests, causal-leakage tests, and predictable demo fallback.
- Optional Cell Tracking Challenge `Fluo-N2DH-SIM+` training data (2D+t, simulator-generated with training ground truth), roughly **91 MB**: https://celltrackingchallenge.net/2d-datasets/. Never describe simulated data as live measured cells.

### Train/evaluate discipline

- Record dataset sequence IDs; fit/calibrate only on allowed past frames of the evaluation trajectory or on a **separate development sequence**. Distinguish online unsupervised fitting from training a predictive model.
- Never train on withheld future frames and then present evaluation as online forecasting. Use separate sequences for offline trained event classifiers, if any.
- Ground-truth annotations / future frames stay inside `ReplayOracle` and `Evaluator`; **never pass them to the controller**.
- MSKCC development/evaluation roles are PHOTON's frozen sequence split, not a claimed official CTC train/test split. If using CTC later, use its **annotated training archives** for retrospective evaluation; official test archives usually lack publicly available ground truth.

## 7. Proposed algorithm and computational design

### 7.1 Data and observation model

Frames/volumes `X[t]` represent a fixed experiment trajectory. An acquisition costs a configurable constant `dose_per_capture` unless dataset metadata supports actual exposure differences. We may compute a 2D maximum-intensity projection for quick UI/early milestones while preserving 3D TIFF stacks for later.

For detected nucleus `i`, use a Gaussian with estimated amplitude `a_i`, center `mu_i`, positive-definite shape/covariance `Sigma_i`, and timestamp. Simple empirical moments on segmented bright blobs are acceptable initially.

`G_i(x,t) = a_i(t) * exp(-0.5 * (x - mu_i(t))^T Sigma_i(t)^(-1) (x - mu_i(t)))`

An approximate image can be obtained by accumulating these Gaussian contributions on the pixel/voxel grid, with a documented compositing function and clipping/normalization. This is a **simplified dynamic Gaussian representation**, not a full physically calibrated microscope renderer. Add temporal trajectories by interpolating/predicting centers and widths from observed frames; divisions require **birth/split state**, not only smooth motion.

### 7.2 State estimator / uncertainty

- Detect regions via intensity preprocessing and connected components / peak finding (start simple; only introduce pretrained segmentation if justified).
- Associate observed objects with previous tracks using gated distance or assignment, with unmatched detections/births tracked explicitly.
- Estimate motion, scale, and feature changes from **only acquired** observations.
- Predict forward from last known state. E.g., constant-velocity with damping + uncertainty growth, plus any observed morphology signal.
- Confidence must deteriorate as the gap from last measurement increases. The uncertainty map can use an ensemble of perturbed plausible states; distinguish heuristic disagreement from true calibrated probabilities.
- Inferred mitosis likelihood may be a heuristic initially. Never market it as a trained biological predictor unless validated.

### 7.3 Acquisition controller

At each permitted source time `t`, compute a score from only the current predicted state:

`risk_t = w_u * uncertainty_t + w_e * predicted_event_interest_t + w_g * gap_pressure_t`

Subject to:

- total acquisition allowance `B`
- `min_gap` / `max_gap` constraints where feasible
- no decisions based on actual unseen `X[t]`
- fixed frame interval of the recorded source sequence
- deterministic output for a fixed dataset and seed

Use a budget-aware threshold or finite-horizon planner. Any prediction horizon, threshold, and weighting must be frozen before evaluation on held-out sequences. Evaluate alternatives at **identical acquisition budgets**. If `B` conflicts with a strict maximum-gap guarantee, surface a validation error or relax a documented constraint—never silently break the budget.

The CUDA kernel should evaluate a **batched scientific workload**, e.g., predict/render many candidate Gaussian states across time/regions or evaluate uncertainty masks for multiple hypothesized capture times. Do not accelerate a trivial scalar `if` statement just to say CUDA was used.

### 7.4 Decision/replay interface (logical contract)

```python
class ReplayOracle:
    def public_metadata(self) -> dict: ...  # frame count, voxel size, frame interval; no future content
    def acquire(self, t: int) -> "ObservedFrame": ...  # only way to obtain X[t]
    def evaluate_after_run(self, run: "RunRecord") -> dict: ...

class AcquisitionPolicy:
    def reset(self, metadata: dict, budget: int, seed: int) -> None: ...
    def decide(self, t: int, past_observations: list, state: dict) -> "ACQUIRE | SKIP": ...
    def observe(self, frame: "ObservedFrame") -> None: ...
```

Implementation can adjust the exact signatures, but the sealed-oracle design, budget enforcement, and observation history isolation are mandatory.

### 7.5 Logging / export contract

Every experiment writes `runs/<run_id>/config.json`, `decisions.jsonl`, `metrics.json`, and optional derived preview images. The minimum fields:

```json
{
  "dataset_id": "Fluo-N3DH-CHO",
  "sequence_id": "<actual sequence ID>",
  "policy": "photon_adaptive",
  "seed": 42,
  "budget": 25,
  "acquired_indices": [0, 4, 8],
  "frame_count": 100,
  "metrics": {
    "acquisitions": 25,
    "relative_exposure_proxy": 0.25,
    "reconstruction_mse": null,
    "event_coverage": null
  },
  "hardware": { "gpu": null, "kernel_backend": "cpu" }
}
```

Numbers and indices above are **schema examples only**, not claims/results; actual arrays and counts must agree and be generated from the run. If a metric cannot be computed, record `null` plus the reason. Include provenance and model version. Never ship canned "winning" scores.

## 8. Evaluation criteria and fairness

**Primary tests:**

1. **Equal exposure budgets.** For a given `B`, every policy acquires at most/exactly the same number of frames (define and report which), with any mandatory initial image included in `B`.
2. **Event coverage.** For each *annotated* event at `t_e`, ask whether an acquired frame occurs within ±`k` source frames (choose `k` in advance). Report precision/recall only if the available annotation definitions support them; otherwise state event coverage, not detection sensitivity.
3. **Reconstruction loss.** Compare predicted images or ROIs with withheld frames (MAE/MSE/SSIM where appropriate). Specify that in-sample observed-frame quality may differ from held-out quality.
4. **Track/lineage continuity (optional).** Use actual source lineage annotations if parsed and validated; defer positional metrics where annotation representations disagree.
5. **System performance.** End-to-end policy wall time, GPU kernel latency on sufficiently large batches, peak memory, CPU/GPU numerical agreement. Measure cold versus warm JIT separately and include transfer time in an end-to-end comparison.
6. **Uncertainty calibration (stretch).** Bin predictions by estimated uncertainty and compare with actual error; if not calibrated, call it a heuristic score.

Compare **fixed interval**, **seeded random**, **adaptive** and ideally **motion/change heuristic** over multiple budgets (suggested 10%, 20%, 33% of source frames if feasible) and seeds/sequence IDs. Plot results and show counterexamples; a PHOTON loss in one condition is an engineering finding, not a number to hide.

**Aspirational goals, not guarantees:** statistically meaningful event-coverage gain or lower reconstruction error at the same budget; working Rust CUDA GPU backend with measured performance on a relevant batch size; repeatable demo from one script. No fabricated "50% less damage" language.

## 9. Recommended implementation structure

```text
photon/
├── PHOTON_SPEC.md
├── BUILD_PHASES.md
├── README.md
├── apps/
│   └── web/                   # Next.js + TypeScript: interactive visualization
├── services/
│   └── science/               # Python: microscopy I/O, models, simulation, metrics, API
│       ├── photon/            # importable package
│       │   ├── data.py
│       │   ├── oracle.py
│       │   ├── gaussian.py
│       │   ├── tracking.py
│       │   ├── policy.py
│       │   ├── evaluate.py
│       │   └── schemas.py
│       └── tests/
├── crates/
│   └── photon-gpu/            # Rust/CUDA kernel, CPU equivalent, benchmarks
├── scripts/
│   ├── inspect_dataset.py
│   ├── run_experiment.py
│   └── build_demo_assets.py
├── tests/                     # cross-component / integration tests
├── data/                      # gitignored raw/downloaded datasets
├── runs/                      # gitignored generated experiments
└── docs/                      # figures, benchmark notes, submission materials
```

This is a suggestion, not a demand to scaffold unused directories. Keep the **science in testable Python modules**, the **GPU-native kernel in Rust**, and the **UI as a consumer of real run artifacts**. API option: FastAPI backed by the experiment service; for 48h, static JSON results are preferable to an unreliable live back end. Initially call the Rust executable in batches via a file or well-defined binary protocol; only add PyO3/FFI if proven necessary.

### Tooling decisions

- Python 3.11+ with NumPy, SciPy, tifffile, scikit-image, pytest, matplotlib (optional: imageio, FastAPI, scikit-learn).
- Next.js + TypeScript + Tailwind for a polished comparison dashboard (can be created late).
- Rust stable 1.89+ and NVIDIA `cutile-rs` as the **preferred** first GPU kernel track. For an RTX 4070 (Ada, sm_89), verify the CUDA/driver combination from the exact `cutile-rs` docs; CUDA 13.2+ is listed for sm_8x, with 13.3 recommended. Linux is the supported target; on a Windows laptop use WSL2 Ubuntu if GPU passthrough/toolkit works. `cuda-oxide` is an alternative, but may require pinned nightly/LLVM and has Linux-only support.
- Keep an equivalent CPU code path that the demo can run if CUDA installation or compiler APIs break. If GPU remains unavailable, disclose this limitation and preserve the frontier research narrative through the 2026 Gaussian microscopy method; do not claim a completed CUDA Rust implementation.
- Seed randomness. Pin dependency versions **after actual installation succeeds**; record OS, GPU, toolkit and exact versions. New Rust/CUDA APIs are rapidly changing; rely on official docs rather than invented method calls.

## 10. Demo requirements (not just polish)

- Large original microscopy preview and dual acquisition timelines (Fixed vs PHOTON).
- Distinct **measured** / **predicted** / **ground truth revealed** visual states.
- Interactive play/pause/scrub, budget selector, maybe policy comparison selector. No inoperative controls.
- One-click **Run experiment** (or choose between pregenerated *authentic*, reproducible experiments).
- Confidence bands / uncertainty indicator; acquired frame markers with tooltip showing why PHOTON chose to capture.
- Transparent metrics cards with exact acquisition budget and provenance.
- In the final pitch, run or replay at least one successful autonomous scheduling run, then reveal hidden frames to show whether it caught events.

## 11. Key risks and honest fallback choices

| Risk | First response | Fallback |
|---|---|---|
| Dataset has few reliable division labels | Inspect CTC `TRA` annotation and lineage files in first phase | Evaluate reconstruction, track preservation; use another annotated training set for event recall |
| 4D Gaussian optimization is too hard in 48h | Fit anisotropic nucleus Gaussians from observed frames, project motion forward | 2D+t first, then 3D+t; clearly call it "simplified spatiotemporal Gaussian model" |
| Predictions miss sudden divisions | Include uncertainty + max-gap guardrails and show misses honestly | Fall back to robust interval-based hybrid; no pretense of perfect foresight |
| CUDA Rust toolchain fails | Run GPU toolchain smoke test early, isolate kernel work | CPU path with benchmark; don't block a science MVP |
| GPU offers little speedup for tiny frame counts | Evaluate genuine large candidate batches and report end-to-end wall time | Show latency vs batch size, without claiming speedup not observed |
| Good-looking reconstructions but no event improvement | Precommit comparison metrics and error analysis | Pitch contribution honestly as a predictive reconstruction + evaluation system, not proven optimal sampling |
| Licensing/reuse of source data unclear | Link to original data; document source and conditions | Do not include raw images in public repo; use synthetic preview fixtures |

## 12. Definition of done

PHOTON is demo-ready when another teammate can clone the project and:

- set up a supported CPU environment following README instructions;
- obtain the allowed public dataset using documented steps;
- execute one reproducible experiment with fixed and adaptive policies at an identical `B`;
- inspect an authentic acquisition trace and final scores generated from held-out frames;
- see no future-frame leakage and no mislabeled synthetic measurements;
- open a working comparison UI that accurately represents those outputs;
- run automated tests and see that all critical gates pass;
- optionally run a Rust-written CUDA kernel with correctness parity and benchmarks (required for us to claim CUDA Rust was used in the finished build).

The project need **not** outperform fixed sampling in every condition to be scientifically honest. However, if it never improves any meaningful objective, revise the scheduling strategy and explain the limits before presenting it as a breakthrough.

---

**Maintainer note:** `BUILD_PHASES.md` holds current status, commands, test evidence, blockers, and decisions. Keep this document stable unless the system's actual scientific promise or contracts change.
