# PHOTON — Living Build Plan and Test Gates

> **Active checkpoint — 2026-10-24:** **Phase 5 manually resumed by the user; INCOMPLETE / NOT VERIFIED.** The standalone runner was observed at step1/5, PID55068, with evaluation progress t100/269. Check `runs/phase5-runner/status.json` and `latest.log` for current progress; do not start a duplicate evaluator or modify frozen science. Phase 6 Glimpse E / Contact is implemented and browser-verified; human comprehension remains open. Research-only next-step priorities and account-switch prompt: [`docs/GLIMPSE_ELEVATION_RESEARCH.md`](docs/GLIMPSE_ELEVATION_RESEARCH.md). Existing partial/pending frontend exports remain snapshots until explicitly refreshed.

> GatorHack V · 48-hour build · Started: 2026-10-23  
> Project contract: [`PHOTON_SPEC.md`](./PHOTON_SPEC.md)  
> **Prior verified milestone:** **Phase 4 + CUDA latency audit verified (2026-10-24 12:43 -04:00).**85 Python tests, native validation/format checks and independent artifact verification pass. Opt-in persistent CUDA worker and vectorized host packing improve dense small-output rendering end to end; current real-volume predictions remain faster on CPU. Actual controller decisions/fitting stay CPU. Full270-step causal replay reproduces54 acquisitions, every decision and final state; max prediction difference1.79e-7. Eight-size cold/warm/transfer/full-call median/p95 report and six actual prediction probes complete. CPU stays default. Phase5 is now paused/incomplete by user request; no biological benefit or whole-experiment speedup claimed.

> Additional CUDA check: official SAXPY example exited 0; all 32 GPU results matched CPU assertions exactly.

> **CUDA latency follow-up complete:** Original Phase4 bridge timings below remain historical evidence. See the additional audit record and [full latency report](docs/cuda-latency-audit.md) for current behavior, reproduction commands, measured crossovers and limitations.

> **Account-switch handoff:** `docs/HANDOFF.md` records the continuation prompt, frozen science, local artifacts and Phase5 gates. Source/tests/lockfiles/docs are checkpointed on `main` at `GG1627/gator-hack-26`; historical "untracked/no HEAD" notes describe the earlier verification sessions. Raw datasets, environments, binaries and generated runs remain ignored and available in this existing workspace. Phase5 is paused/incomplete; Phase6 early start is explicitly authorized; see the checkpoint below.

## Current authorized branch — bounded controlled event focus

Latest frontend direction: the controlled replay is now the primary demo. Reaching
frame 239 automatically stops playback, opens the saved evidence and scrolls to a
large results panel. Cards show the selected run's division coverage versus fixed,
40 images taken, the exposure-count reduction versus all-frame imaging (same for
both schedules), and final simulated nuclei/divisions. Cell health remains unmeasured.
Replay clears the results and restarts at zero; unfavorable/quiet cases retain
accurate values. Real microscopy is preserved in an expandable research archive;
the main demo can load independently of the real-data manifest.
Production build and full-playback Chromium completion checks passed, including
five viewport widths, automatic reveal/scroll, replay/reset, abrupt/quiet results,
and archive navigation. Desktop/mobile completion screenshots were inspected.
No new scientific benchmark or full-volume work was run for this frontend change.

User authorized ambitious controller/scenario redesign with accurate measurements
and clearly labeled synthetic demonstrations, and explicitly requested no hour-long
new tests. This branch supplements the real-data protocol without changing frozen
sources or claiming completion of Phase 5 / the Phase 6 comprehension gate.

- Implemented `experiments/controlled/{event_focus,benchmark}.py`: Gaussian
  morphology from acquired pixels triggers bursts; exact-budget/gap guards retained.
- `scripts/run_controlled_benchmark.py`: development seeds 7/42, unchanged settings
  on evaluation seeds 101–105/2026; three fixed phases, old/new adaptive, three
  conditions, 40/240 captures each. 120-second per-batch deadline.
- Executed development 30 comparisons in 6.2s; evaluation 90 in 19.3s.
- Measured precursor coverage new 24/24, fixed 12/24 (shifted 13/24,12/24), old 12/24.
  Abrupt coverage new 6/24, fixed 12/24. Quiet coverage undefined. Synthetic only.
- Six focused tests passed in 4.45s. Export checked all metric rows,
  source image/code hashes and trace consistency; 54 native CUDA Rust Gaussian-fit
  render batches passed CPU sample comparisons, completing in 55.6s internally.
- `ControlledLab.tsx` provides clearly separated controlled replay with all seeds,
  conditions and fixed phases, source-pixel/model views and gated evaluation.
  Production build and seven Node tests pass. Chromium lab interactions, evidence
  gating, unfavorable controls and five responsive widths pass; screenshots inspected.
  Original real-data replay regressions pass. Full Phase 5 registration still passes.
- Evidence and limits: [docs/CONTROLLED_EVENT_FOCUS.md](docs/CONTROLLED_EVENT_FOCUS.md).
  Original Phase 5 runner remains untouched in its independent source verification.

## Operating instructions for Codex (read first)

1. Read `PHOTON_SPEC.md` and this file before modifying code. **Inspect existing files before scaffolding**; do not overwrite prior work.
2. Work **one phase at a time**. Implement, run tests, inspect actual outputs, then check off the acceptance criteria. Do not begin the next phase until the current phase is verified, unless a blocker is explicitly recorded and a fallback is selected.
3. After each phase, update: status checkboxes, implemented paths, exact test commands, observations/metrics, known limitations, and the decision log below. Use `YYYY-MM-DD HH:MM` local time if available; don't invent timestamps.
4. Keep the runnable end-to-end experiment alive at all times. Favor reversible, small code changes and atomic commits where practical.
5. **No scientific leakage:** the decision policy may access a frame only after an `acquire` action. Ground truth, future frames and post-hoc labels must remain sealed in the oracle/evaluator.
6. **No fabricated results:** UI and README must derive benchmark cards from actual experiment files. If a result is unknown, display "not measured" instead of numbers.
7. **No fake GPU work:** verify that a native Rust-written GPU kernel runs, numerically matches a CPU reference, and does useful batched Gaussian/candidate computation. A Python/CUDA wrapper alone does not count.
8. If a phase is blocked for more than a reasonable focused attempt, document cause and minimal fallback; move forward without abandoning the validated science MVP. Prioritize a complete judged demo.
9. The app must never conflate synthetic data, real captured frames, reconstructed predictions, or revealed offline ground truth.
10. Whenever the plan changes, modify this file, explain the choice, and keep old completed verification evidence rather than resetting it.

### Critical path

**Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 5 → Phase 6 → Phase 7**  
**Phase 4 (CUDA Rust)** starts with a setup/smoke test in Phase 0, then can be built in parallel once the CPU Gaussian computation is correct. Do not let GPU setup block a working policy baseline. Phase 8 is stretch only.

## Dashboard

| Phase | Outcome | State | Exit gate |
|---|---|---|---|
| 0 | Repo & environment verification | ✅ Verified | CLI/test smoke runs; CUDA feasibility recorded |
| 1 | Real data + sealed replay oracle + baselines | ✅ Verified | Real270-frame replay; equal54 captures; repeat identical; causal API tests |
| 2 | Gaussian observation model + predictions | ✅ Verified | Numerical/causality tests; real sparse prediction; post-hoc errors verified |
| 3 | PHOTON adaptive acquisition policy | ✅ Verified + refinement | 71 tests; paced/robust default; five-run s1 ablation; exact real rerun; causal/gap/budget checks |
| 4 | New CUDA Rust scientific kernel | ✅ Verified | Native kernel;80 tests; real parity/fallback; measured timings/chart; CPU default |
| 5 | Rigorous evaluation and reproducibility | 🔄 User-launched background runner; incomplete | Check live runner status; full verification/recomputation and result review pending |
| 6 | Stunning interactive demonstration | 🔄 Implemented; user playthrough approved | User ran playback and approved appearance; automated checks pass; formal unfamiliar-viewer comprehension check remains open |
| 7 | Final validation & submission | ⬜ Not started | Fresh-machine instructions, all evidence verified |
| 8 | Stretch: 3D/PSF/multi-well/microscope adapter | ⬜ Optional | Only if all core gates passed |

> **Status convention:** `⬜ Not started` / `🔄 In progress` / `⏸ Paused (user request)` / `✅ Verified` / `⚠️ Blocked (fallback recorded)`. A paused or partially completed phase has not passed its gate.

---

## Phase 0 — Bootstrap, scientific feasibility, and toolchain spike

**Goal:** Repository is runnable and we know whether the intended 2026 GPU toolchain works on this machine. **Do not try to develop the full engine yet.**

**Tasks**

- [x] Inspect repository; choose a minimum viable folder structure from the spec; create `README.md`, `.gitignore`, test setup.
- [x] Establish Python environment and a tiny `pytest` smoke test; establish a reproducible CLI entry point `python scripts/run_experiment.py --help`.
- [x] Inspect OS, NVIDIA GPU name, driver, CUDA availability, Rust toolchain; **record facts**, not assumptions. On Windows, test WSL2 CUDA access if using native Rust GPU kernels.
- [x] Attempt a small official `cutile-rs` example from NVIDIA's docs. Document exact tested version/command and whether it ran. For `cuda-oxide` only if necessary, follow its current official requirements.
- [x] Prepare a tiny synthetic microscopy clip and distinct `ObservedFrame`/`PredictedFrame` types or tagged JSON structures.
- [x] Start `docs/experiment-log.md` or use the logs below; record research references from spec.

**Verification commands (adapt to actual environment and update them here)**

```bash
python --version
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe scripts/run_experiment.py --help
nvidia-smi                   # where available
rustc --version
cargo --version
```

**Pass criteria**

- [x] Smoke test passes, no secret token/downloaded raw dataset is committed.
- [x] Clear commands in README run the current CLI.
- [x] CUDA Rust feasibility classified **working**, **blocked with cause**, or **not yet attempted**. No unsupported claim of GPU success.

**Record (2026-10-23 22:05 -04:00):** Implemented `.gitignore`, `README.md`, `pyproject.toml`, `requirements-dev.lock`, `services/science/photon/{__init__,schemas,synthetic,cli}.py`, `services/science/tests/test_bootstrap.py`, `scripts/run_experiment.py`, and `docs/experiment-log.md`.

- **Tests:** Isolated Python 3.13.5 environment installed; **3 passed in 4.02s**. CLI help and seeded synthetic NPZ export succeeded. Initial checks ran before pip finished and failed on missing imports; rerun passed. Ignore checks passed; Git has no tracked files/HEAD. No raw dataset or credentials created.
- **Environment:** Windows build 26200; RTX 4070 Laptop GPU, 8188 MiB, sm_89, driver 581.57; native toolkit 12.0, Rust/Cargo 1.91. WSL2 Ubuntu 22.04.5 sees GPU, but Linux rustc/cargo/nvcc/tileiras absent from PATH.
- **CUDA classification:** **Blocked with cause.** Official `cargo run -p cutile-examples --example hello_world` attempted in WSL against NVIDIA revision `fc747196f2d46dce41bd844e3f5b1c5882751f2b`; failed before compilation (`cargo: command not found`). No kernel executed. Native CUDA 12.0 is below documented Ada Tile IR requirements.
- **Decision:** CPU fallback for Phase 1; retain Phase 4 GPU gate. Fixture generator is synthetic test data, not a reconstruction algorithm. Frame containers do not yet enforce an oracle boundary.
- **Next:** Phase 1 real CTC training archive/terms/annotation audit, sealed replay and equal-budget baselines. No scientific acquisition experiment or benchmark exists yet. Exact commands, dependency versions, failures, references and GPU retry prerequisites: [experiment log](docs/experiment-log.md).
- **CUDA follow-up (2026-10-23 22:17 -04:00):** Corrected initial PATH diagnosis: Linux Rust 1.99.1 is installed at `~/.cargo/bin`; `source ~/.cargo/env` makes it available. Retried official example; upstream auto-installed its pinned Rust 1.98.0 and compilation reached `cuda-bindings v0.5.0`, which failed with no Linux CUDA toolkit found. CUDA toolkit installation requires interactive Ubuntu sudo (password required). Phase 1 remains unstarted while user resolves setup.
- **CUDA resolution (2026-10-23 22:31 -04:00):** User installed Linux toolkit; independently verified `cuda-toolkit-13-3` 13.3.1-1, nvcc 13.3.73, tileiras 13.3.36, libclang-dev 14, Rust/Cargo 1.98.0 in upstream workspace. With `source ~/.cargo/env` and `CUDA_TOOLKIT_PATH=/usr/local/cuda-13.3`, official hello-world exited 0 and printed from GPU: `Hello, I am program <0, 0, 0> in a kernel with <1, 1, 1> programs.` Same upstream revision and driver 581.57. **Current classification: working (official hello-world); original missing-toolkit blocker resolved.** This does not complete Phase 4 scientific kernel/parity/benchmark gates.

---

## Phase 1 — Real data ingest and sealed acquisition replay

**Goal:** A fair scientific experiment exists *before* the clever model.

**Tasks**

- [x] Download the complete **MSKCC-CONFOCAL s1 development window, source frames 0..269**, outside Git; verify metadata, images and curated lineage annotations. This replaces unavailable CHO with user authorization. Prepare s2/s3 image windows before Phase 5; metadata/label audits already done.
- [x] Implement `load_sequence()` for TIFF images/stacks and a tiny fixture that requires no real dataset download for tests.
- [x] Implement `ReplayOracle` that withholds `X[t]` unless `acquire(t)` is invoked. Ground truth accessible only to `Evaluator` after the run ends.
- [x] Implement `fixed_interval` and `seeded_random` policies at same frame budget `B`. Include frame 0 within `B` and document interval rounding.
- [x] Implement `RunRecord`, decision trace, and JSON export to `runs/<id>/`.
- [x] Track metadata: sequence ID, time interval, observed vs withheld indices, random seed, acquisition budget.
- [x] Build minimal terminal output / plot showing selected time points and raw observed images.

**Required tests**

- [x] Test that a policy cannot retrieve future `X[t+1]` or target event labels through its allowed API.
- [x] Test `B=1`, `B=T`, short sequences, invalid `B`, and deterministic `seed` behavior.
- [x] Test that policies given identical budgets capture the same **count** (or log precise and justified constraints).
- [x] Test corrupt/missing TIFFs and unexpected array shapes fail with useful messages.
- [x] Test JSON traces match exactly what the oracle acquired.
- [x] Manually review real archive: **how many cell divisions/lineages are actually annotated?** MSKCC first270: s1 568, s2 560, s3 567; temporal graphs cross-checked and spatial discrepancies documented.

**Demo gate:** From a CLI, run two acquisition schedules on the complete *MSKCC s1 development window* with the same number of volume acquisitions; create a timeline and valid JSON. This is the authorized replacement for the original CTC training-sequence gate.

**Implementation history (earlier blockers below are superseded by the final verification record):**

**Record (2026-10-23 22:41 -04:00):**

- **Files:** `photon/data.py`, `policy.py`, `oracle.py`, `replay.py`, `audit.py`; updated frame schemas/CLI; `scripts/inspect_dataset.py`, `tests/test_replay.py`; pinned installed tifffile 2026.10.15 and Pillow 13.0.0. README and `docs/dataset-notes.md` document usage and limitations.
- **Tests:** `.venv/Scripts/python.exe -m pytest -q`: **18 passed in 3.30s**. Earlier increments: 13 passed, then 16 passed. Package reinstall, `pip check` (no broken requirements), both CLI help commands and generated synthetic comparison succeeded. Contact sheet visually inspected and labeled SYNTHETIC. Ignore checks confirm raw/generated paths excluded.
- **Contracts:** Exactly B captures including frame 0. Fixed indices `floor(k*(T-1)/(B-1))`, B=1 -> [0]. Random = frame 0 plus B-1 seeded unique samples. Trusted runner advances clock; policy sees frozen metadata and earlier observations only. Oracle rejects future/duplicate/budget-invalid acquisition and early/mismatched evaluation. Isolation is an API contract, not a hostile-code Python sandbox. Loader validates/hashes source before the run; replay reads pixels only upon acquisition. Annotation audit is separate and never passed to policy.
- **Example (synthetic only):** 8 frames, B=3, seed 42: fixed `[0,3,7]`, random `[0,1,6]`; each count 3, exposure-count proxy 0.375. `runs/phase1-fixture/comparison/{fixed_interval,seeded_random}` contains configs, decision JSONL, metrics, text timelines and acquired-image contact sheets. Reconstruction/event coverage null with explicit reasons; no performance comparison claimed.
- **Dataset/events audit:** Official metadata and conditions reviewed; actual archive **not obtained**. HTTPS timed out from Windows and WSL, HTTP retry and official public-host probe also timed out. Actual shapes/counts/divisions unknown. `audit_lineage()` tested on controlled fixtures; real mask/lineage review pending. Public non-CTC scientific use requires organizer permission; public demo permission is not established. Keep local; do not redistribute images.
- **Gate:** **NOT PASSED.** Need official training archive, audit real frames and annotations, run both baselines on a real sequence and inspect artifacts. Phase 2 remains closed. See [dataset notes](docs/dataset-notes.md) for download/resume steps and [experiment log](docs/experiment-log.md) for evidence. No scientific methodology or core frontier technology replaced.
- **Alternative data investigation:** Author-deposited Figshare division/tracking archive downloaded successfully (175060057 bytes; MD5 matches depositor). Raw TIFFs and annotation files confirmed. Limited to 19 frames/video at a documented 4-hour cadence; not yet ingested or scored. LFCT offers potentially better 10–15 minute time series through author-linked Box downloads, not yet locally verified. See dataset notes. CTC requirement has not been silently replaced; Phase 1 remains incomplete.
- **Candidate comparison:** LFCT Box access now verified: FLD_3 original RFP ZIP + XML downloaded; 433 contiguous 904x1224 uint8 frames, matching annotation dimensions, 17 binary graph branches; sampled position overlays align. FLD_4 XML downloaded: 433 declared frames and 44 reported splits. Figshare division audit: 418 numeric event rows across ten 19-frame movies; independently verified after accounting for headerless CSVs and six empty rows. LFCT recommended primary; Figshare secondary. XML physical timing is uncalibrated; preserve frame indices. No replacement replay or spec amendment yet. [Full comparison](docs/dataset-comparison.md), reproducible script `scripts/audit_candidate_datasets.py`, outputs `runs/candidate-audit/`.
- **3D-priority follow-up (23:11 -04:00):** Independent 3D+t sources found: MSKCC-CONFOCAL C. elegans (three 400-frame embryo movies, 75s cadence, curated lineages, 26.1GB), organoid OME-Zarr (contiguous ~50-frame subset 2.4GB, raw volumes/timestamps/GEFF), and Ultrack neuromast streaming data. Zenodo API licenses CC BY 4.0 and archive byte-range downloads verified for first two. Prefer auditing MSKCC next to preserve 3D scope; LFCT recommendation was limited to comparing the two 2D candidates. No full 3D archive or annotations audited, no gate passed or spec changed.
- **MSKCC audit (23:25 -04:00):** Completed user-requested candidate audit; strong 3D+t replacement recommended if CHO unavailable. ZIP inventory confirms 400 volumes/embryo; downloaded all 3 main TSV/XML lineages plus 15 sampled volumes using bounded HTTP ranges (433089383 cached bytes, selected-entry CRC checks). Samples all 41x512x512 uint16; calibrated Z conversion verified. Actual divisions fully inside first270 frames: s1 **568**, s2 **560**, s3 **567** (total1695). IDs/frames/edges agree exactly across TSV/XML; spatial positions differ for 163 s2 and 102 s3 spots, so defer spatial tracking scores. Full archive MD5/full-image integrity not verified; no complete replay performed. Added `scripts/audit_mskcc_dataset.py` and range-integrity tests: **22 passed in 2.36s**. [Full audit and limitations](docs/mskcc-audit.md). CHO remains primary pending user's search; Phase 1 gate remains open.
- **Replacement implementation (23:35 -04:00):** User confirmed CHO unavailable and authorized replacement selection. Chose one required dataset family: MSKCC; s1 development, s2/s3 evaluation, all first270. Spec explicitly amended. Native TIFF/window/metadata support and offline canonical MaMuT importer added. Resumable four-worker downloader started; full s1 ingestion in progress. **34 tests passed in 3.63s**; missing frames cannot silently shorten the window, out-of-window TIFFs ignored, malformed temporal graphs rejected. Real-data demo gate still pending download. 2D datasets optional only.

---

### Phase 1 final verification — 2026-10-24 00:00 -04:00

**GATE PASSED.** All Phase1 tasks and required tests are satisfied for the authorized MSKCC replacement.

- **Real input:** 270 TIFFs0..269, 5849694836 bytes, all decoded/validated as 41x512x512 uint16. Author cadence75s; XYZ spacing0.15/0.15/0.75um; s1 development. Source ZIP CRC verified per selected file; full26.1GB archive MD5 not claimed. Download manifest records selected/original counts.
- **Canonical annotations:** Production importer reproduces s1 568 binary divisions in the window; every requested frame has annotations. Missing IDs, gaps, duplicate edges, merges and nonbinary graphs fail usefully. s2/s3 label counts560/567 also reproduced; full evaluation-image ingestion remains Phase5 work. Spatial differences remain documented; no positional accuracy score produced.
- **Commands (venv Python):** `scripts/download_mskcc.py --sequence s1 --workers 4`; `scripts/inspect_dataset.py data/mskcc-audit/mskcc-confocal --output runs/mskcc-phase1-audit.json`; `scripts/run_experiment.py --sequence data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1 --budget 54 --seed 42 --output runs/mskcc-phase1`; repeated with `--output runs/mskcc-phase1-repeat`.
- **Actual results:** fixed_interval54/270 and seeded_random54/270; each exposure-count proxy0.2 and270 decision records. Both include frame0. Independent assertions checked trace budgets, last-observation fields, acquired/withheld indices and text timelines. Configs record metadata, source/code hashes, CPU backend, seed42, original400 frames and selected window0..269. Real measured-image MIP contact sheets visually reviewed. Reconstruction and event scores null with reasons; no adaptive-quality claim.
- **Reproducibility:** All five exported files per policy (`config.json`, `decisions.jsonl`, `metrics.json`, `timeline.txt`, `observed.png`) are byte-identical to repeat outputs. Evidence: `runs/mskcc-phase1-verification.json`.
- **Tests/checks:** Final `.venv/Scripts/python.exe -m pytest -q`: **34 passed in 3.28s**. `pip check`: no broken requirements. `git diff --check`: clean. Raw/generated ignore checks pass. Tests cover causal API/history, oracle clock/budget/closure, future perturbation, seeded schedules, boundary budgets, TIFF errors/native window and malformed graphs.
- **Source SHA256:** `6d53d2e92fb3a452bdba32e13cadc8ae2b7521ffc7460a9913414ad2fdca6917`; code SHA256 `a9392d99895f45f25635d5a215598cf5138c64c8742d76c49a24c36020362f8c`.
- **Next:** Phase2 Gaussian fitting/rendering and causal tracking/prediction. No adaptive scheduler, reconstruction-quality comparison, scientific GPU kernel or biological benefit claimed in Phase1. Frozen split and oracle/annotation isolation carry forward.
- **User-suggested alternatives audit (2026-10-24 00:09 -04:00):** BBBC035 Broad host reachable; full GT ZIP CRC checked, two lineage tables audited (150/80 frames,37/40 binary divisions), six synthetic raw/mask volume pairs decoded and visually checked. Synthetic29-minute sequences offer no replacement for the real-data gate. Zenodo4630932 resolves to4630933: CE image files total4.77GB, not the entire15.9GB bundle. Downloaded/checksummed XMLs and CE01 Mastodon, inspected CE01 HDF5 metadata/patch; binary graph not decoded, license description BY-NC-ND4.0. Retain MSKCC; no primary dataset, split, controller or benchmark changes. HTTP `readinto` added for audit tooling; isolated h5py/imagecodecs only. **34 tests passed in2.69s**; current science-code hash and original/repeated artifacts unchanged. [Detailed audit](docs/bbbc-ce-audit.md). Phase1 remains verified; no real replay redo needed.

---

## Phase 2 — Dynamic Gaussian representation and prediction

**Goal:** Make a real cell-state model that can estimate missing frames based only on observed ones.

**Tasks**

- [x] On acquired microscopy images, normalize intensity and extract bright nuclei/cell regions (start with threshold+components or blob detection).
- [x] Fit each component with an anisotropic Gaussian (center, covariance, intensity, size) from **observed** pixels/voxels.
- [x] Implement a documented CPU Gaussian renderer with predictable clipping and intensity scaling.
- [x] Associate bright-component candidates between acquired frames; damp centroid velocity and hold last size/intensity; track births/unmatched objects explicitly. These are not validated nucleus identities.
- [x] Implement temporal uncertainty that increases after a skipped observation; calculate uncertainty from a small predictor ensemble or covariance propagation.
- [x] Add `predict(t) -> PredictedFrame`, with tags identifying reconstruction and uncertainty; never read actual withheld `X[t]` while predicting.
- [x] Preview the Gaussian model side-by-side with acquired real frames and withheld frame only in the offline evaluation view.

**Required tests**

- [x] Gaussian fitting recovers known synthetic center and covariance within stated tolerance.
- [x] CPU renderer's output is finite, nonnegative where expected, and correct on simple analytic fixtures.
- [x] Time predictions are reproducible and depend only on previous observations; audit the call graph for leaks.
- [x] With no new observations, scalar position uncertainty does not *artificially shrink* as predicted horizon increases. Image ensemble disagreement is a different, nonmonotonic heuristic.
- [x] Synthetic split/birth input doesn't produce a crash or silently change past identities; limitations documented.

**Demo gate:** Select sparse acquired images from a real microscopy sequence; display measured observations and a distinctly labeled Gaussian-based prediction at one withheld time.

**Record — 2026-10-24 08:58 -04:00: GATE PASSED.**

- **Files:** `photon/{gaussian,tracking,schemas,oracle}.py`; `scripts/{run_prediction_demo,verify_prediction_demo}.py`; `tests/test_{gaussian,tracking,prediction_causality}.py`. Model formulas, axes, tolerances and limitations: [Gaussian model](docs/gaussian-model.md). README usage updated. Added/pinned SciPy 1.18.1; editable package reinstalled successfully.
- **Architecture:** First acquisition freezes median/99.99th-percentile signal normalization and MAD noise scale. Physical smoothing + threshold-connected components; weighted moments, positive covariance floor and least-squares amplitude; local additive Gaussian CPU rendering with radius-4 truncation/final clipping. Physical gated assignment, explicit birth/retirement and candidate-split IDs; source-gap damped velocity, held shape/intensity. No learned appearance, PSF deconvolution or full CellSplat4D reproduction.
- **Uncertainty:** Nondecreasing heuristic position scale in micrometers; optional deterministic +/-axis common-motion ensemble pixel standard deviation. Neither is calibrated. Empty scenes still have increasing scalar uncertainty, but image disagreement can be zero. No unseen birth/division forecasting is claimed.
- **Causality audit:** Model accepts only acquired `ObservedFrame`; no source/oracle/label imports. Trusted runner acquires 0,5,10 and predicts 12 before closure. Evaluator requires closed replay, matching acquisition history and first-frame calibration before revealing withheld truth. Read-spy tests reject early scoring before any target read; perturbing all unseen frames leaves predictions/maps bit-identical while changing post-hoc errors. Prior IDs/snapshots remain unchanged. Isolation remains a cooperative Python API contract.
- **Tests:** `.venv/Scripts/python.exe -m pytest -q`: **48 passed in 4.46s**. Synthetic full-mask center/covariance/amplitude tolerances 2e-4; thresholded covariance 1.5% for truncated tails. Independent rotated-Gaussian renderer formula rtol 2e-6/atol 1e-7; empty/thin/boundary/invalid values, physical spacing, true time gaps, deterministic maps, monotone scalar uncertainty and split/birth cases covered. A controlled translating Gaussian beats hold-last; this is synthetic evidence only.
- **Real demo command:** `.venv/Scripts/python.exe -u scripts/run_prediction_demo.py` (stdout saved to `runs/mskcc-phase2-stdout.txt`), exit 0. Full s1 window validated, 270 decisions, exactly three acquired volumes 0/5/10; five final bright-component tracks; target 12 withheld. `runs/mskcc-phase2/` contains config/state/trace/metrics, separate prediction/evaluation NPZs and visually inspected six-panel `comparison.png`. All computation/scoring is 3D; preview panels are MIPs. No RNG; seed field 0 is provenance only.
- **Actual errors:** Normalized 3D forecast MSE **0.0011492511713106393**, MAE **0.016446842166130262**; hold-last MSE **0.0010383232654541978**. Common evaluation-only ROI union >0.1 has 465551 voxels: forecast MSE **0.012568739149017037**, hold-last **0.010504868602816072**. **Forecast is worse on both comparisons.** No parameters changed after inspecting this target to manufacture improvement. Scalar uncertainty 0.28292126898563924 um is heuristic. Event coverage remains null with reason; this is one development-frame preview, not adaptive-policy evaluation.
- **Artifact verification:** `.venv/Scripts/python.exe scripts/verify_prediction_demo.py` exited 0: complete trace, exact budget, history/tags, finite normalized volume/maps, saved truth against source TIFF, science-code hash, and independent whole-volume/ROI recomputation all pass. Evidence `runs/mskcc-phase2-verification.json`. Both CLI help commands pass; post-reinstall `pip check` clean, ignore checks pass, `git diff --check` clean (repository still has no tracked files/HEAD).
- **Provenance:** Source SHA256 unchanged `6d53d2e92fb3a452bdba32e13cadc8ae2b7521ffc7460a9913414ad2fdca6917`; current science-code SHA256 `73e6fb3172e29ed78868c76c8feb3066b5a1c48d7c0497f152aafe7ebca1ee31`. NumPy 2.5.4/SciPy 1.18.1, CPU only. Historical Phase 1 hashes refer to that earlier implementation.
- **Limitations/blockers:** No blocking Phase 2 gate remains; predictive quality is a known weakness. Thresholded moments miss texture/diffuse signal and merge touching objects; components are not validated nuclei. Sparse association and split hints may be wrong. Fitting-only versus motion ablation remains needed before attributing errors. No GPU scientific kernel, calibrated event predictor, policy advantage or biological phototoxicity benefit claimed.
- **Next:** Phase 3 causal budget/gap-safe scheduler and explainable trace; treat event hints as heuristics. Preserve raw hold-last baseline in later evaluation. Phase 5 must evaluate frozen settings on independent s2/s3 windows and report losses as well as wins. Phase 3 has not started in this increment.

---

## Phase 3 — Decision intelligence: adaptive sampling controller

**Goal:** PHOTON actually decides when to turn the virtual microscope on.

**Tasks**

- [x] Define interpretable decision components: uncertainty, predicted event interest, acquisition gap pressure, and budget remaining.
- [x] Implement a controller that scores future usefulness from its **current estimated Gaussian state** (no future truth).
- [x] Add minimum-gap, maximum-gap, and remaining-budget feasibility; handle impossible combinations with explicit errors.
- [x] Log for every timestep: score, predicted risk (explicitly uncalibrated priority), uncertainty, last acquired time, remaining budget, decision, why.
- [x] Implement one additional honest heuristic baseline: normalized pixel change between acquisitions.
- [x] Build a replay animation: fixed vs PHOTON; controller chooses acquisitions and receives only frames it requested. Completed-run GIF holds each policy's past measurements and labels that display.

**Required tests**

- [x] Exactly B acquisitions; mandatory initial image included; no budget under/overflow due to guardrails.
- [x] Given an identical observed history and seed, controller makes the same decision.
- [x] **Leakage regression:** perturb/change all unseen future frames without modifying past observations; decisions up to the next acquisition remain exactly the same.
- [x] Synthetic known-event fixture: observed pre-split elongation can increase capture density before a scripted split; no claim of biological predictive validity.
- [x] Constrained-gap tests, including insufficient/excessive `B`, report explicit failure; exhaustive enumeration checks integer-horizon feasibility.

**Demo gate:** A real, completed PHOTON run produces nonuniform acquisition markers **and explainable decision logs**; there is no lookup of future frames except on acquisition.

**Record — 2026-10-24 09:12 -04:00: GATE PASSED.**

- **Files:** `photon/adaptive.py`; replay/CLI integration; `tests/test_adaptive.py`; `scripts/{build_schedule_replay,verify_adaptive_runs}.py`; [controller formulas, feasibility derivation and limitations](docs/acquisition-controller.md). Historical Phase 2 verifier now reports code-version differences instead of rejecting valid old artifacts by default; `--require-current-code` remains available. No core scientific model/renderer or data split changed; no dependencies added.
- **Architecture:** Deterministic priority from growing heuristic uncertainty, observed physical velocity, observed morphology/candidate-split hints, gap pressure and remaining-budget desired spacing. Threshold1; weights/scales exported before evaluation. Event interest is not a probability. Image-change baseline uses first-calibration normalized MAE rate between acquired volumes only; shares budget/gap guard, no Gaussian fitting.
- **Constraints:** Exactly B captures including0. Min/max constrain inter-acquisition source gaps; terminal measurement age <=max_gap. No required final capture. Each decision tests feasibility of acquire and skip using an integer-interval completion condition. Impossible budget/gap combinations fail during reset; all policies prevalidated before comparison starts. Real-data physical spacing required; synthetic unit-spacing fallback explicit.
- **Tests:** `.venv/Scripts/python.exe -m pytest -q`: **59 passed in 5.83s**. Phase 3 increment11 tests (initial10 passed in1.69s; final targeted11 in2.34s). Exhaustive combinations for horizons1..8 independently match the planner. Boundary budgets/gaps with tiny/default/huge thresholds preserve exact counts and terminal coverage. Controlled shape cue increases capture density before a synthetic split; high uncertainty, empty state, unexpected changes and lifecycle errors covered.
- **Causality:** Only metadata/history enters decide; only pending acquired `ObservedFrame` enters observe. Read spies confirm exact acquisition-only reads for both new policies. Perturb all unacquired frames -> identical full decisions; changing the next acquired frame leaves decisions through that acquisition unchanged and affects only later state. No annotations/evaluator/source imports in controller. Scores captured before observe, with distinct pre/post last-index/budget fields. Supported API isolation, not hostile-code sandboxing.
- **Real command:** `.venv/Scripts/python.exe -u scripts/run_experiment.py --sequence data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1 --budget 54 --seed 42 --policy all --min-gap 2 --max-gap 12 --output runs/mskcc-phase3` (stdout `runs/mskcc-phase3-stdout.txt`), exit0. All four policies exactly54/270, count proxy0.2;270 decisions each. Config/state/metrics/timelines/contact sheets exported. Full source validated before replay. Settings fixed before run; no label or quality-based tuning performed.
- **Actual PHOTON gaps:** 2:13,3:16,4:12,5:1,10:1,12:10; last capture257, terminal age12. Reasons: mandatory_initial1, priority_threshold43, max_gap_due10; skips minimum_gap53, below_priority_threshold42, reserve_for_future_coverage109, budget_exhausted12. Image-change gaps4..12, terminal age12. Fixed gaps5/6; random retains original unconstrained1..18 gaps. Equal budgets verified, equal gap constraints across all baselines not claimed.
- **Known weakness:** PHOTON spends many captures early, then uses mostly maximum gaps late. Feasibility protects coverage but does not establish scientifically good allocation. Maximum component elongation is sensitive to debris/merged objects, motion may reflect association mistakes, and Phase 2 forecasting already lost to hold-last. No reconstruction/event/accuracy gain is measured here; these scores remain null with reasons. Do not describe priority as calibrated biological risk. Development-only allocation/feature ablations and frozen held-out evaluation remain needed.
- **Repeat:** Re-ran same PHOTON command with `--policy photon_adaptive --output runs/mskcc-phase3-repeat`, exit0. All six files (`config.json`, `decisions.jsonl`, `metrics.json`, `timeline.txt`, `observed.png`, `state.json`) byte-identical. `.venv/Scripts/python.exe scripts/verify_adaptive_runs.py --repeat runs/mskcc-phase3-repeat --require-current-code` exit0 independently verifies counts, chronological pre/post budgets, score arithmetic, gap/terminal limits, source/current-code hashes and repeat bytes. Evidence/hashes `runs/mskcc-phase3-verification.json`.
- **Animation:** `.venv/Scripts/python.exe scripts/build_schedule_replay.py` exit0, creates270-step `runs/mskcc-phase3/replay.gif` (16581567 bytes), PNG preview and manifest. Visually inspected first differing capture. Only acquired images read after completed replay; each panel holds its own last measurement, explicitly labeled; per-image scaling display-only. Synthetic animation test verifies read-index union and exact preview-panel pixels against each policy's own past image. No hidden truth or unmarked prediction shown.
- **Other checks/provenance:** Post-reinstall environment still `pip check` clean; CLI/animation/verifier help pass; raw/generated ignore checks and `git diff --check` clean (files remain untracked, no HEAD). Historical Phase 2 metrics recompute unchanged via `--output runs/mskcc-phase2-postphase3-verification.json`; earlier science hash reported as historical. Source SHA256 `6d53d2e92fb3a452bdba32e13cadc8ae2b7521ffc7460a9913414ad2fdca6917`; Phase 3 science SHA256 `424ba895efc8d551be29a79543c0d938329eecedea0cc9d92eb022f27026a323`; CPU NumPy2.5.4/SciPy1.18.1.
- **Blockers/next:** No blocking Phase 3 gate remains. Phase 4 meaningful batched Gaussian CUDA Rust kernel with CPU parity/actual timing is next; do not accelerate a scalar policy condition. Phase 5 must investigate early spending on development data and evaluate frozen settings on s2/s3 with proper same-budget errors/event coverage. No GPU, phototoxicity or adaptive-quality advantage claimed. Stop this increment at the verified Phase 3 boundary.

---

### Phase 3 bounded refinement — verified, 2026-10-24 10:11 -04:00

- User approved one development comparison before Phase4. [Protocol](docs/phase3-refinement-plan.md) written before event/reconstruction scores: fixed, original, pacing only, robust features only, both. Same s1 first270/B54/seed42/min2/max12. No s2/s3 data or results accessed.
- Pacing limits discretionary count to uniform allowance+2, with feasibility override logged. Robust features use mean clipped elongation and median matched-track speed. Legacy behavior remains available; no default changed during experiment.
- Added saved causal forecast/held-scene archives, raw post-closure evaluation access, canonical +/-1-frame event coverage, whole3D/foreground errors on own and exact common withheld targets, Gaussian forecast/held-fit/raw-hold estimators. Every oracle must close before any label/truth scoring. Adoption rule fixed in protocol: more covered events than original and no higher common-target raw-hold MSE, ranked by event coverage then raw-hold MSE/name; otherwise keep original.
- **Files/architecture:** Added `photon/development.py`, post-closure raw evaluation access, optional pacing/robust presets in `adaptive.py`, CLI `--controller-variant`, `scripts/{run_phase3_refinement,verify_refinement,build_refinement_report}.py`, tests and [measured report](docs/phase3-refinement-results.md). Geometry freezes causally at withheld times; full3D pixel rendering/scoring occurs offline. All five oracles close before any scoring label/truth access. No dependencies added or core Gaussian renderer replaced. Source/labels/evaluator remain isolated from policy inputs; calibration comes from the first acquisition only.
- **Tests:** First69 passed in7.81s. New deployment integration test initially wrote unsupported float TIFFs (70 passed/1 failed in24.40s); fixed fixture to supported uint16 without relaxing loader. Final `.venv/Scripts/python.exe -m pytest -q`: **71 passed in25.35s**. Pacing/extreme budgets/feasibility overrides, outlier resistance, simultaneous events/missing labels, direct voxel arithmetic, early evaluation rejection, future perturbation, saved-geometry reproduction and selected-default CLI/legacy preset pass. Refined default still increases density on a controlled observed pre-split cue.
- **Actual experiment:** `.venv/Scripts/python.exe -u scripts/run_phase3_refinement.py` exited0, stdout `runs/mskcc-phase3-refinement-stdout.txt`. All five54/270, first270 s1 only. Original indices exactly match historical run. All216 withheld volumes per variant scored for Gaussian forecast, held Gaussian fit and raw hold-last. Exactly110 targets withheld by every method form the matched comparison; own-withheld scores also retained. Foreground is common evaluation-only truth>0.1, first-frame calibration frozen.
- **Event coverage +/-1:** fixed334/568 (58.80%), original192/568 (33.80%), paced324/568 (57.04%), robust285/568 (50.18%), combined325/568 (57.22%). Simultaneous divisions counted separately. These are retrospective observation-coverage counts, not event-classifier recall or biological protection.
- **Common-target raw-hold MSE:** fixed0.002593877198638001, original0.0030148813707635102, paced0.002396484938248152, robust0.0027727098039323065, combined0.00239686669592595. Combined improves original by20.50% on this metric. Common foreground raw MSE original0.02117596602982864→combined0.015423441381577004; fixed0.01705148542039333.
- **Counterexamples/limits:** Own-withheld raw MSE: fixed0.002112048451820563 versus combined0.0021630874284391992 (original0.002712791182792161). Fixed wins own-target error and event coverage; combined wins common-target hold-last error. Matched-target selection is schedule-dependent; no overall superiority claim. Gaussian forecast common MSE combined0.009422673762121025, held Gaussian0.009407540063153719, raw hold0.00239686669592595: appearance model remains much worse, and motion extrapolation slightly hurts. Most coverage gain comes from pacing; robust aggregation adds only one covered event over pacing-only here. No post-score parameter search or hidden losses discarded.
- **Adoption:** Declared rule selects `paced_robust`; made it API/CLI default only after comparison and verification. `--controller-variant original` preserves legacy; separate paced/robust presets expose ablations; image-change defaults unchanged. Original first-half43 captures→combined29, gaps3:1/4:7/5:41/6:4, terminal age9. Hard min2/max12 remains enforced; discretionary lead2 is soft only when feasibility forces acquisition. No labels/results read by deployed controller.
- **Independent checks:** `.venv/Scripts/python.exe scripts/verify_refinement.py --prepare-probes --sequence data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1` prepared source rerenders after all runs closed. Then `scripts/verify_refinement.py --source-probes runs/mskcc-phase3-refinement/source-probes.json` exited0: all trace/budget/gap/calibration/version accounting, exact common intersection, all per-frame metric aggregation, independent vectorized event counts and declared selection rule agree. First/middle/last common targets1/174/268 rerender exactly for all five variants and all three estimators (15 target checks/45 estimator comparisons). This is full metric accounting plus source spot checks, **not a second complete rerender**. Full rerender available with `run_phase3_refinement.py --recompute`; strict version check optional, actual metric equality mandatory.
- **Real deployment rerun:** `.venv/Scripts/python.exe -u scripts/run_experiment.py --sequence data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1 --budget 54 --seed 42 --policy photon_adaptive --min-gap 2 --max-gap 12 --output runs/mskcc-phase3-refined`, exit0. Default's decisions.jsonl/state.json byte-identical to selected experimental variant; acquired indices, controller/fit/tracking settings and source fingerprint identical. Evidence `runs/mskcc-phase3-refinement/selected-default-verification.json`. Only deployed default/CLI changed after frozen comparison; model state/decisions reproduce exactly.
- **Artifacts/provenance:** Summary, all ablations, causal scene archives, per-frame errors, verification and source probes under `runs/mskcc-phase3-refinement/`; exact source snapshot ZIP matches comparison hash `8adcdf673fc787fb58629db6b77ac7471a334f16c778fde18e755d33666fd162`. Current deployment hash `2a18c9d18c8f9e27055a21303df11afafe720f8321c12ce9558ecd933db1a0f6`; source unchanged `6d53d2e92fb3a452bdba32e13cadc8ae2b7521ffc7460a9913414ad2fdca6917`. CPU NumPy2.5.4/SciPy1.18.1. `scripts/build_refinement_report.py` derives readable tables directly from JSON, including own-target reversal.
- **Preview/checks:** Built/visually inspected `fixed-vs-combined.gif` and PNG via `scripts/build_schedule_replay.py --runs runs/mskcc-phase3-refinement --fixed-name fixed --adaptive-name paced_robust --output runs/mskcc-phase3-refinement/fixed-vs-combined.gif`, exit0; completed-run acquired images only, held display explicit. `pip check`, experiment/refinement help, ignored-data checks and `git diff --check` clean. Historical artifacts preserved; repository remains untracked/no HEAD.
- **Blockers/next:** No blocking Phase3 refinement gate remains. Frozen selected preset is development-derived; s2/s3 untouched. Phase5 still requires independent embryos/multiple budgets and should investigate Gaussian appearance/motion errors before forecasting claims. Stop bounded search here and proceed next to Phase4's meaningful CUDA Rust kernel/parity/timing work; no scientific GPU kernel, speedup or biological benefit yet claimed.

## Phase 4 — Frontier kernel: Rust + NVIDIA GPU

**Goal:** Prove native CUDA Rust is doing actual scientifically relevant computation and not decorating the stack.

**Implementation:** Native Rust cuTile Gaussian accumulation on2D/3D grids. FP64 geometry protects anisotropic shape/cutoff decisions, FP32 exponential/value accumulation, original radius4 clipping convention. Flagged boundary voxels use the exact original CPU scene renderer, preserving array-layout-dependent FP64 reduction order. Actual repair counts/cost recorded. Checked protocol/shape/domain/buffer limits; up to10000 Gaussians per scene, empty scenes, bounded128M-voxel batches. Python mean/uncertainty-scenario integration batches actual scientific rendering; it does not change controller features/decisions. [Kernel contract](docs/cuda-rust-kernel.md).

**Kernel target (pick one with evidence):** batched Gaussian accumulation for many candidate projected states **or** parallel per-pixel uncertainty comparison across predicted cell states / candidate capture times. Prefer a tile-friendly workload for `cutile-rs`. Report kernel design and data layout.

**Tasks**

- [x] Confirm Phase 0 `cutile-rs` smoke test. Reviewed/re-ran pinned official SAXPY;32 exact GPU assertions.
- [x] Implement CPU-reference-equivalent Rust GPU rendering; rtol2e-4/atol2e-5, original CPU implementation retained.
- [x] Checked binary-file batch integration between Python and Linux native Rust (WSL on Windows).
- [x] Numerical parity across1/100/10000 Gaussian inputs, empty batches/scenes, rotated/thin matrices, clipping and cutoff adversaries.
- [x] Warm CUDA graph event interval, host dispatch, context/JIT/cache, H2D/D2H, allocation and full single-render caller times measured separately. Limits documented; no instruction-profiler timing claimed.
- [x] Requested/actual backend and toolchain/binary/source/timing/memory metadata logged. CPU remains default.

**Required tests**

- [x] All tested supported GPU outputs agree within declared tolerances; exact inclusion at rotated cutoff adversaries uses CPU reference repair.
- [x] Invalid dimensions/resource sizes/nonfinite payload/unsupported numerical domain rejected; explicit/automatic fallback semantics tested.
- [x] Machine-readable five-case benchmark and inspected standalone Matplotlib chart separate CPU/device/full caller costs.
- [x] Real s1 GPU and deliberate unavailable-GPU fallback runs reproduce CPU54/270 acquisitions and exact decisions/state.

**Demo gate:** Show *actual* Rust-written CUDA kernel output and correctness validation; speedup is a measured bonus, never invented. If blocked, mark **⚠️** with an honest backend limitation and keep shipping the CPU science prototype.

**Record — 2026-10-24 11:28 -04:00: GATE PASSED.**

- **Paths:** `crates/photon-gpu/{Cargo.toml,Cargo.lock,rust-toolchain.toml,src/main.rs}`; `photon/gpu.py`, prediction/schema integration; `tests/test_gpu.py`; scripts `build_gpu.py`, `benchmark_gpu.py`, `plot_gpu_benchmark.py`, `run_phase4_experiment.py`, `verify_phase4.py`. Added/pinned Matplotlib3.11.2 dev plotting dependencies after actual installation. No new runtime service, agent, frontend or hardware control.
- **Environment:** RTX4070 Laptop8188MiB/sm89, driver581.57, WSL2 Ubuntu22.04, CUDA13.3/nvcc13.3.73/tileiras13.3.36, Rust1.98.0, pinned NVIDIA revisionfc747196f2d46dce41bd844e3f5b1c5882751f2b/cuTile0.5.0. Official SAXPY recheck passed. Upstream tracked working tree clean. Rust release build recorded76091.5513ms, compile cache not assumed empty.
- **Tests:** Final `.venv/Scripts/python.exe -m pytest -q`: **80 passed in50.45s**. Includes rotated/anisotropic covariance,1/10000 component native fixtures plus100 in benchmark, empty scenes/batches, non-power tile lengths,7-state uncertainty batch, explicit fallback, nonfinite/resource guards, full-volume grid regression and high-amplitude rotated cutoff inclusion. Rust `cargo fmt --check` and `cargo test --locked --offline` return0; one checked-input/resource unit test passes. Native exit verified via captured Python subprocess (`runs/phase4-rust-checks.json`), avoiding PowerShell's native-stderr error formatting.
- **Failures resolved:** Initial offline resolution selected uncached futures-macro0.3.34; reused pinned upstream lock, then `--locked --offline` succeeds. Kernel prototype required explicit tile/scalar broadcasts and importing native error-conversion trait. First full-volume benchmark hit CUDA grid-Y limit (83968>65535), despite small cases passing; remapped output to[B,ceil(P/8192),8192]/tiles[1,1,128], safe3D grid, added above-limit regression. Preserved failed/partial logs at `runs/phase4-benchmark*`. Cutoff repair strengthened to call the original full-scene CPU renderer when any flags occur; only flagged voxels substituted, overhead logged. Initial chart margins clipped labels; regenerated from the same JSON with explicit margins and visually verified.
- **Final benchmark command:** `.venv/Scripts/python.exe -u scripts/benchmark_gpu.py --output runs/phase4-benchmark-verified`, exit0. Five CPU repetitions/five warm graph device intervals/three separate single-render full callers per case. Fixed seed42, no overlapping validation jobs during measurements, active laptop/no clock lock. CPU uses local bounding boxes; GPU evaluates full grid, so work counts differ. Profile warm repeats are separate from normal single-render requests. JSON/raw samples/chart under that run root.

| Measured case | CPU median ms | Warm device interval ms | Full Python/WSL caller ms | Max abs error |
|---|---:|---:|---:|---:|
|G1/B1,64x64 |0.260200 |0.045056 |1857.918600 |2.98e-8 |
|G100/B1,64x64 |33.241900 |0.214016 |1984.296300 |1.49e-8 |
|G10000/B1,64x64 |3087.018400 |19.818497 |5291.007200 |4.47e-8 |
|G100/B6,64x64 |194.339700 |1.199104 |2127.439800 |1.49e-8 |
|Real observed s1 t260,G17/B1,41x512x512 |85.679400 |49.300480 |5335.463800 |1.19e-7 |

- **Interpretation:** Every full caller is slower than CPU. No end-to-end speedup claimed; CPU default retained. Warm GPU arithmetic advantage is real but insufficient through current subprocess/WSL/context/JIT/transport overhead. Initial fresh cache compiled3 backends; main-render JIT preparation1613.011631ms, later same-case processes0 compiles/3 disk hits but cache/AST/context cost persists. All benchmark repair counts0; boundary-heavy cases can incur full CPU scene render and are tested separately. Transfer numbers are synchronized allocation/copy wall times, not isolated PCIe bandwidth; memory snapshots are observed free bytes, not claimed peak VRAM.
- **Real GPU command:** `scripts/run_phase4_experiment.py --backend cuda-rust --output runs/phase4-real-gpu-verified` (venv Python), exit0. Full270-step causal s1 replay/B54/seed42/default paced_robust; freeze geometry at all withheld times. After closure, batch-render targets1/134/268; no labels opened and no true images passed to native worker. CPU-reference max errors1.7881393432617188e-7/1.1920928955078125e-7/1.1920928955078125e-7. Same source, controller parameters, acquired indices, decisions.jsonl/state.json as historical CPU run.
- **Real unavailable-GPU fallback:** Set `PHOTON_GPU_BINARY` to deliberately missing local file, run same script with `--backend auto --output runs/phase4-real-cpu-fallback-verified`, exit0. Actual backend CPU, missing-binary reason recorded, no kernel execution, zero pixel difference to CPU. Same54 acquisitions/decisions/state. Scientific acquisition behavior unchanged by renderer backend. GPU and fallback pixels/source errors exported honestly; event score null with reason, annotations not accessed.
- **Independent evidence:** `.venv/Scripts/python.exe scripts/verify_phase4.py` exit0 checks all five timing-accounting cases, single-render mode, binary/current-code hashes, saved real predictions/history/tags, CPU scene rerenders, target source MSE recomputation and exact GPU/fallback decisions/state. `runs/phase4-verification.json` confirms all caller speedups<1. Native/Rust and Python evidence retained. Completed chart `runs/phase4-benchmark-verified/timings.png` inspected after margin fix.
- **Provenance:** Science SHA2560427bc5620e65b1e37bf87b98ccd81e6b00b396d5f770ad4f8e1d1c8d25a7fff; binary2f0ee563a2bd0b76d2638e4f7f1f58506579ba1a05eea4200a77b197908e833f; Rust-source80369c56f763a0f57bbff3a55878b0b446db7b751f76f4e21b60f6a2e1480bd0. Source microscopy fingerprint unchanged6d53d2e92fb3a452bdba32e13cadc8ae2b7521ffc7460a9913414ad2fdca6917. NumPy2.5.4/SciPy1.18.1/CPython3.13.5. Cargo lock/toolchain and build metadata pinned.
- **Final checks:** `pip check`, build/benchmark/experiment/verifier help, raw/generated ignore checks and `git diff --check` pass. Exact Python/Rust/manifest/lock/script snapshot saved to `runs/phase4-source-snapshot.zip`, CRC checked and source hashes matched to final benchmark. No raw images or credentials included. Repository still untracked/no HEAD; no commits or publication performed.
- **Blockers/next:** No blocking Phase4 correctness/integration gate remains. App latency is a measured limitation; persistent engine/transport optimization is unmeasured future work. Preserve CPU default and frozen controller; Phase5 should evaluate independent s2/s3/multiple budgets and retain fixed/raw-hold baselines. Gaussian appearance/motion quality remains weak; GPU parity is not an accuracy or biological benefit. No Phase5 work started here.

---

### Phase 4 latency investigation — verified 2026-10-24 12:43 -04:00

**Outcome:** Setup/cache/packing/transport costs explained the discrepancy; no GPU kernel or acquisition-method rewrite. CPU remains the correct default for the current real experiment. Repeated dense small-output rendering now has a measured full-caller GPU benefit. This is not a scheduler or whole-experiment speedup.

- **Trace/evidence before changes:** Every original `CudaRustRunner.render()` spawned WSL and a new CUDA context. Historical cached calls paid roughly340–410ms context,240–290ms output allocation/fill preparation and850–910ms main-kernel preparation despite disk hits. Real-volume subprocess wall exceeded native compute by about3.3s. G10000 had several seconds of Python overhead. `AdaptivePolicy.decide()` never called the renderer; fitting/tracking and scalar priorities were CPU. Reported these bottlenecks before implementation.
- **Small justified changes:** Optional managed `CudaRustRunner(persistent=True)` uses one native `--worker`, context/stream and cuTile in-process cache, retaining the validated file payload and JSON control/completion channel. Per-request buffers remain independently checked; timeout/death closes the worker and `auto` records CPU fallback; subsequent calls can restart. Vectorized NumPy packing retains domain checks and bit-identical inverse payloads. Output buffering8KiB→1MiB gives a modest measured improvement. One-shot path and CPU default retained. CUDA kernel text is identical to the original snapshot (kernel-block SHA256 `b710984c6fd9196e5a39800fb73eb8a0e3643f1cccb326377a75709433e20041`). No buffer pool, FFI framework, GPU score replacement or future image access added.
- **Measurement:**15 warmed CPU, resident graph-kernel, synchronized GPU-plus-transfer, cached one-shot and persistent full-caller repetitions per each of8 cases;5 fresh-process/context/empty-JIT-cache cold repetitions each. CUDA events/end-event synchronization for graph intervals; `sync_on` for production transfers/render. External Python wall timing includes packing/files/WSL or worker IPC/context when first used/readback/reference repair/hash/cleanup. Worker startup and first request separately recorded. WSL VM stays running; OS/driver caches are not purged. No host Cargo compile occurs at request time. Median/p95 use NumPy linear percentile; cold p95 is exploratory with n5. Active laptop, no locked clocks/exclusive GPU; host Intel Core Ultra9 185H/16GB, same RTX4070/toolchain as original Phase4. Full definitions and all8 rows: [latency report](docs/cuda-latency-audit.md).

Selected **full-caller median / p95 ms** (kernel-only timing is not used for these speedup conclusions):

|Workload |CPU |Persistent GPU |Cached one-shot GPU |Fresh process/JIT cold GPU |
|---|---:|---:|---:|---:|
|64x64,G100/B1 |31.236 /35.402 |110.230 /120.153 |1922.042 /2016.238 |2841.435 /2897.111 |
|64x64,G1000/B1 |294.675 /334.492 |129.097 /170.928 |2012.089 /2225.416 |2857.071 /2951.118 |
|64x64,G10000/B1 |2913.980 /3080.486 |230.120 /290.729 |2062.454 /2141.119 |3027.844 /4793.808 |
|64x64,G100/B7 |223.177 /283.633 |130.827 /243.374 |1917.755 /2089.119 |2971.589 /3164.345 |
|Real s1 t260,G17/B1,41x512x512 |99.823 /115.877 |1501.052 /1924.154 |3178.821 /3958.306 |4085.807 /4124.527 |
|Real geometry,seven-state ensemble |627.122 /770.205 |9147.040 /10085.138 |10091.474 /10527.325 |11198.666 /11608.145 |

- **Attribution:** WSL `/bin/true` median284.497ms; native `--ping`290.374ms without CUDA. Warm worker render preparation0.012–0.04ms with0 backend compiles/0 disk hits. For real B1, response writing846.52ms and Python read/validation211.24ms dominate its1501ms full call; real B7 writes4913.56ms, reads/validates1368.99ms and D2H alone takes750.16ms. Payload53.74MB/B1 and376.18MB/B7. Its synchronized GPU-plus-transfers median1366.44ms already exceeds CPU627.12ms. Native production dispatch/sync also exceeds resident graph intervals; direct launch overhead is included in full timing. Residual bookkeeping/hash and filesystem costs are not falsely called PCIe or startup. Component medians are not additive totals.
- **Controlled ablations:** Packing10000 descriptors before2855.405 /3113.220ms versus after64.747 /68.507ms,10 repetitions, packed values bit-identical. Real B1 output buffer8KiB full median1198.887ms versus1MiB1083.902ms; fixed-order/variable laptop conditions limit causal precision of that modest difference. Major gains come from context/cache reuse and packing. Historical original release binary/build metadata preserved as `.tools/photon-gpu/{photon-gpu-before-worker,build-before-worker.json}` and original source archive unchanged.
- **Crossovers/batching:** Alternating CPU/GPU order,15 repetitions: synthetic64x64 G400 CPU124.912ms vs GPU131.932ms; G600184.988 vs137.696ms. Observed warm crossover bracket400–600, geometry-specific. G1000 full caller2.28x and G10000 full caller12.66x; these are dense synthetic rendering results. G100/B4 is effectively tied126.004 vs123.140ms; B7 gives clearer223.177 vs130.827ms. Seven separate warm synthetic calls823.008ms, but real seven-call8360.837ms is actually faster than real batch9147.040ms. No universal batching win. Startup/first JIT must amortize (synthetic B7 first request1839.665ms); cold G10000 median still loses to CPU.
- **Actual adaptive path:** Full270-step s1 replay,54 captures, exact old acquisitions/every decision field/final state. No annotations or withheld pixels read. Decision median/p950.023400 /0.061485ms over4050 same-causal-state calls. Acquired-image fitting/tracking1282.634 /4050.994ms and acquisition I/O61.340 /306.811ms across54 captures. Fitting dominates controller computation; GPU rendering does not accelerate it. Six actual `model.predict()` comparisons at predeclared1/134/268, with7/87/17 tracks, alternate CPU/GPU order15 times each and verify no state mutation. CPU mean medians62.318/534.257/137.980ms versus GPU1142.038/1639.342/1986.145ms. CPU mean+map1522.725/5993.239/2095.996ms versus GPU9621.192/15167.662/14779.392ms. All p95/raw samples retained; no observed real prediction or acquisition-score crossover. Numerical maxima: pixels1.7881393432617188e-7, maps8.940696716308594e-8.
- **Executed commands:** venv Python `scripts/diagnose_gpu_io.py --output runs/cuda-latency-audit/io-ablation.json`; `scripts/benchmark_gpu_latency.py --output runs/cuda-latency-audit/matrix`; `scripts/benchmark_gpu_crossover.py --output runs/cuda-latency-audit/crossover.json`; `scripts/benchmark_adaptive_latency.py --output runs/cuda-latency-audit/adaptive`; `scripts/verify_gpu_latency.py`; `scripts/plot_gpu_latency.py`. All exit0. Do not overlap benchmark jobs. Raw samples/metadata, saved causal trace/state, verification and inspected chart under `runs/cuda-latency-audit/`.
- **Tests:** Targeted GPU suite13 passed in33.28s. Final full `.venv/Scripts/python.exe -m pytest -q`: **85 passed in63.34s**. New tests cover exact vectorized payload/domain checks, worker same-process reuse with changed data/shapes, boundary repair, clean close, timeout fallback, killed-worker recovery and a guard prohibiting rendering in controller execution. Initial full run found a missing import in that new guard (1 failed/84 passed in67.26s), corrected and rerun successfully. Native `cargo fmt --check` and `cargo test --locked --offline` exit0; one native validation unit passes, captured command/exit/stdout/stderr at `rust-checks.json`. Independent verifier recomputes every median/p95, checks GPU-plus-transfer accounting, current source/Rust/binary hashes, cold compile/warm cache behavior, saved exact trajectory/state and causal histories.
- **Provenance:** Science SHA256 `463ff1c1502cedf304d121a84a949066cca2d6503533c3eb69c8bc8f5c054f27`; binary `ebf988dec8ddd1f35b3f55e5dfa40fb9a5f84dc8b406fbcf322d39ce7db7fa8a`; Rust source `d45b951c21a9045486cccd6e1df825c50b0185ffb4f8f1b8bdf912cbeaf241e6`. Source microscopy fingerprint unchanged. Incremental release build21430.2244ms, not claimed cold. Original Phase4 evidence remains valid for its archived source; its verifier intentionally enforces that old snapshot. Use `verify_gpu_latency.py` for current evidence.
- **Limitations/next:** CPU default retained. Host memory pressure, large output files, batch-backed mean views and active-laptop variability affect long tails; no peak-RAM/VRAM or isolated PCIe throughput claim. Probe validation retains reference/warmup/previous outputs; timings apply to that recorded harness. No whole-experiment, biological or reconstruction-quality gain is inferred from rendering speedups. No audit blocker remains; Phase5 held-out evaluation is next. Keep controller frozen, report fixed/raw-hold baselines and pursue further GPU work only when a real workload justifies it. No Phase5 implementation begun here.
- **Final packaging/checks:** Python source/script compilation, `pip check` and `git diff --check` pass (repository remains untracked/no HEAD). Current source, documentation, frozen benchmark input/evidence and the original source archive are preserved in CRC-checked `runs/cuda-latency-audit/source-and-evidence.zip`; raw microscopy images and credentials are excluded. The standalone full-caller chart was visually checked; legend moved outside data without changing measurements.

---

## Phase 5 — Scientific benchmark and post-hoc validation

**Goal:** Determine whether PHOTON genuinely offers better **information per acquired frame**.

**Tasks**

- [x] Run fixed, seeded random, adaptive (and heuristic if available) under the **same `B`**, dataset sequences, and repeated seeds as appropriate.
- [ ] Compute acquisition count, dose proxy, withheld-frame reconstruction MAE/MSE (and SSIM if well-defined) with masks/normalization documented.
- [x] Where real lineage/event labels are available, compute event coverage within a **predeclared** ±`k`-frame tolerance. Do not derive eval-time target events from unseen frames and feed them into the controller.
- [x] Evaluate multiple budgets (suggested 10%, 20%, 33% of time points where constraints allow) and more than one sequence or seed.
- [ ] Export `config.json`, `decisions.jsonl`, `metrics.json`, figures/plots and version metadata for every run.
- [ ] Inspect failure cases: missed divisions, false event alerts, cases where uniform sampling beats us; document them.

**Required tests**

- [x] Same-budget rule asserted automatically for every policy comparison.
- [x] No annotations available → `event_coverage = null` with reason, not zero or fabricated result.
- [ ] Metrics exactly reproducible from run artifacts and fixed seeds.
- [ ] Recompute benchmark from withheld data in evaluator and verify UI cards match generated JSON.

**Demo gate:** There is one trusted benchmark JSON and one chart comparing fixed versus PHOTON, with clear caveats, **whether it wins or loses**. If there is no improvement, investigate honest tuning only on development sequences, then rerun a held-out evaluation; don't tune on a displayed test trace.

**Incremental record (2026-10-24; evaluation outcomes not yet computed):**

- Inspected clean `main`, all primary documents and existing ignored evidence. Baseline `.venv/Scripts/python.exe -m pytest -q`: **85 passed in56.64s**. No GPU setup or kernel changes.
- s1 remains development; initial s2/s3 image counts were five sampled volumes each (including out-of-window399). Existing `download_mskcc.py --sequence s2/s3 --workers 4` CRC-checked resumable downloads running, logs `runs/phase5-download-s{2,3}.log`. Full window validation is pending.
- Added protocol/staged runner and independent statistic/ledger checks in `photon/benchmark.py`, `scripts/run_phase5.py`, `scripts/report_phase5.py`, `docs/phase5-protocol.md`. Reuse existing causal scene recorder/evaluator; explicit scope, provenance and text timeline added. Controller/model/GPU implementations unchanged; CPU default retained.
- Predeclared plan: s2/s3 first270, B27/54/89, fixed/PHOTON/image-change plus random seeds7/42/2026 (36 trajectories), event tolerance+/-1, first-acquisition normalization, truth>0.1 offline foreground, own/common/pairwise-fixed targets, forecast/held-Gaussian/raw-hold. Random is equal-count but retains unconstrained gaps. Full source rerender and direct card-to-JSON checks planned. No held-out selection/tuning.
- Targeted `.venv/Scripts/python.exe -m pytest -q services/science/tests/test_benchmark.py services/science/tests/test_development.py`: **19 passed in9.24s**. Controlled cases cover no extra acquisition reads, future perturbation, exact-budget feasibility, random determinism, missing labels, matched targets, tampered ledgers/metrics and exact source/scene recomputation without policy calls. Compilation check passed.
- Full pre-freeze suite: **93 passed in84.50s**, stdout `runs/phase5-tests-before-freeze.log`; `pip check` clean. Includes a complete controlled36-run staged pipeline, exact full source recomputation, chart/card generation and closed-file tamper rejection. An earlier integration run reached its final tamper assertion but hit the source-hash guard because source was edited concurrently; no real held-out outcome was involved. Stable-source rerun passed. Real data validation/freeze/acquire/evaluate/verify/full-recompute/report stages are queued in `runs/phase5-pipeline.log`, stopping on any nonzero exit.
- Final source before real registration: **93 passed in81.47s**, `runs/phase5-tests-registered-source.log`. Added independent vectorized event arithmetic, exact seed/schedule/controller/exposure checks and sign-correct win/loss selection. Missing-label report/plot/card behavior also tested (null, never fabricated zero). `inspect_phase5_failures.py` exports explicitly post-hoc measured/predicted/eval-only MIP panels after verification; source scores remain full3D. No scientific model, controller or GPU changes.
- **Data/freeze gates passed, 2026-10-24 13:30 -04:00:** s2/s3 each270 decoded41x512x512 uint16 volumes, all selected images and main annotations match source ZIP CRCs. Image bytes5849610913 /5849623218; window0..269,75s, XYZ0.15/0.15/0.75um, extra399 samples excluded. Full archive MD5 not claimed. `runs/phase5-data-validation.json`; source hashes s2 `d5dfabc8f2a7446c0a937cf41ec9ce9a189b76e74fe2481c5ca922fc6fa91a47`, s3 `efefbed147e1f67c2991eb577a7667fe42244bb62698f03f0f5f8364aaaf4587`.
- **Registered before outcomes:** `runs/phase5/protocol.json` SHA256 `7e675b6569a82dbf8fff4ac59fbcaf950e7f4dd21d1e3a5b6bd08a861a794b73`; CRC-checked frozen source ZIP `ed21533fecf4533b2d8b5d94f2656eb88040dc97a33e75a0a7ad0c02d7ff8067`. Exact controller/fit/tracking settings, all source/test/runner hashes, data fingerprints, Git HEAD/dirty state and dependency versions captured. Acquisition started after registration, no held-out scores computed yet. Implementation/protocol remain immutable for this matrix.
- **Acquisition gate passed, 2026-10-24 14:22 -04:00:** all36 trajectories closed under the registered settings,2040 whole-volume captures total, exact B27/54/89 per method/condition. CPU default; all PHOTON/image-change inter-capture/terminal gap checks passed. `runs/phase5/all-trajectories-closed.json`, immutable per-run `closed.json` hashes, configs/states/scenes/traces/timelines. All trajectories completed before the first outcome-scoring stage. Source-integrity QA decodes full windows in trusted loaders before controllers run; only acquired observations reach controllers. The stdout sentence about no withheld reads refers to replay loops, not that separate QA. Offline scientific scoring has started; metrics/recomputation gates remain open.
- **Post-closure event-only audit:** `runs/phase5/event-audit.json`, same registered protocol, all36 closed-file hashes and budgets checked before labels; canonical helper agrees with independent nearest-capture vector arithmetic. Fixed beats PHOTON on event coverage in all6 conditions. At B27/54/89: s2 fixed176/352/557 of560 versus PHOTON140/325/544; s3 fixed150/348/558 of567 versus PHOTON131/332/546. Deficits36/27/13 and19/16/12 events respectively. All random/image-change results retained in the audit. This is +/-1 source-frame retrospective coverage, not classifier recall. No held-out tuning or controller changes; full-volume reconstruction metrics and their full source recomputation remain pending.
- **Temporal failure inspection:** `runs/phase5/event-failure-audit.json`. At B54 both embryos have fixed capture101 versus PHOTON97/102 around daughter frame100: fixed covers11 s2 divisions (mother IDs2414,2416,2417,2427,2437,2439,2444,2445,2446,2447,2448) and7 s3 divisions (2485,2486,2500,2510,2513,2548,2551) that PHOTON misses at the declared+/-1 tolerance. PHOTON covers161 clock timestamps versus fixed160 here, yet fewer labeled divisions, showing the temporal allocation/phase issue. At B89 both embryos: PHOTON261 covered clock timestamps versus fixed265, terminal ages5 versus0. These are descriptive post-hoc failure cases; no timing offsets/parameters were tuned to test outcomes.
- **First full-image condition scored (source rerender still pending):** s2/B27 all6 methods/243 withheld targets each; all-method common147, fixed/PHOTON paired common218. Paired raw-hold MSE PHOTON0.006764643617763716 vs fixed0.006863698660076684; own-withheld raw MSE PHOTON0.006847225856928299 vs fixed0.006734736906330803, a ranking reversal. PHOTON own Gaussian forecast0.02026135787759542, held Gaussian0.02019323943815579, raw0.006847225856928299. Independent `verify_statistics` passed every sum/aggregate/target/seed/controller/exposure/event field; events equal the separate event audit. `runs/phase5/mskcc_confocal_s2/b27/early-verification.json`. Do not interpret conditional matched-target gains as general accuracy superiority; full matrix/full source recomputation remain pending. Observed available RAM below1GB during this CPU pass; no timing-speedup claim or scientific approximation introduced.
- Gates still open: finish/validate held-out windows; freeze hashed protocol before outcomes; complete matrix; score and independently recompute source metrics; inspect chart/failure cases; final tests. No scientific wins/losses claimed; Phase6 remains unstarted. Model recommendation issued: GPT-6.1 Sol High for evaluation design (manual switch not confirmed).

---

### User-requested pause checkpoint — 2026-10-24

**Stopped:** Ctrl+C to the running execution session stopped the evaluator and its automatic orchestrator. Confirmed no PHOTON scoring/orchestrator Python processes remain. No later scoring stage or full recomputation was launched. Scientific source, parameters, frozen protocol/source archive, raw datasets, acquisition traces and original logs are unchanged.

**Finished and preserved:**

- Complete validated s1 development and s2/s3 held-out windows; s2/s3 selected270 volumes each are decoded and source-ZIP-CRC checked.
- Registered protocol/source snapshot and all36 closed acquisition trajectories,9720 decisions,2040 simulated whole-volume captures. Current frozen source hashes and all36 closed-file hash ledgers rechecked successfully during checkpointing; source ZIP CRC passes.
- Event-only coverage audit for all36 runs/all6 conditions, independently cross-checked with nearest-capture arithmetic. Fixed covers more events than PHOTON in every condition; all random/image-change scores and temporal failure cases retained.
- Full-image **first-pass** MAE/MSE and foreground errors for all6 methods at **s2/B27 and s2/B54**:12 scored runs,2754 withheld-frame rows, all3 estimators. Configs/traces/timelines/scenes/state remain available for every run. Completed metrics/evaluation files match their saved group summaries structurally.
- s2/B27 additionally passed independent scalar accounting/target/seed/controller/budget/event checks (`early-verification.json`). s2/B54 has not yet had that independent accounting pass. Neither condition has been independently rerendered from source a second time.
- Latest full tests on the frozen scientific implementation: **93 passed in81.47s**. No scientific implementation changes occurred after registration or during this pause.

**Incomplete / unverified:**

- **s2/B89** was interrupted; the last logged source frame was100. Actual in-memory progress beyond that marker is unknown. No image metric/evaluation export or per-frame checkpoint exists for this condition; it resumes from0.
- **s3/B27, s3/B54, s3/B89** image scoring has not started. Their event audits and all acquisition artifacts are complete.
- No complete `benchmark.json`, global `verification.json`, full `recomputation.json`, generated report/chart/cards, or post-hoc image case panels exist. Full source recomputation has **not started**. Phase5 remains incomplete and must not be presented as verified.

**Checkpoint files:** `runs/phase5/checkpoint.json` is the machine-readable partial-results index. `runs/phase5-paused-checkpoint.zip` is a CRC-checked17348462-byte copy of every current Phase5 run artifact, frozen source/protocol, data validation, pipeline/download logs and final pre-registration test log; raw microscopy files are excluded and remain in `data/`. ZIP SHA256 `42a73b943ae4e1ea5b7ebbaf8f03c466af36ef6e1d355cfe45a9e4c04ce68b05`; sidecar `runs/phase5-paused-checkpoint-manifest.json`. Original artifacts and `runs/phase5-pipeline.log` are retained in place. These directories remain Git-ignored.

**Manual resume only after the user resumes Phase5:**

```powershell
.venv/Scripts/python.exe -u scripts/run_phase5.py evaluate
```

This checks the frozen implementation/closed artifacts, reuses both completed summaries, and scores only s2/B89 and the three s3 conditions. It reconstructs evaluation ledgers from saved acquisition indices without running policies or refitting models. Initial TIFF integrity loading is repeated; completed scoring groups are skipped. Do not re-freeze, download, reacquire, or restart the old automatic stage chain.

After those four groups finish, run these **separate, explicitly manual** completion steps when authorized to finish Phase5:

```powershell
.venv/Scripts/python.exe scripts/run_phase5.py verify
.venv/Scripts/python.exe -u scripts/run_phase5.py evaluate --recompute
.venv/Scripts/python.exe scripts/report_phase5.py
.venv/Scripts/python.exe scripts/inspect_phase5_failures.py
```

The full recomputation intentionally revisits all saved source/scene targets as a verification gate. No command above was launched during checkpointing. Keep registered scientific modules, science tests, protocol and frozen runner/report scripts unchanged so resume hash checks continue to pass. Phase6 can add frontend files outside those frozen paths.

**User-approved sequencing exception:** Phase6 may start while Phase5 is paused. Use actual saved configurations, timelines, causal scenes and the12 completed image metric exports plus the36-run event audit. Label image scores **first-pass / source rerender pending**, other image scores **pending / not computed**, and the whole benchmark **partial**. Use null plus reasons for pending values; preserve own-versus-matched target caveats and measured/predicted/eval-only labels. This authorization changes phase order, not the frozen methodology or Phase5 completion criteria. No UI work has begun here.

---

## Phase 6 — Judge-facing 10-second experience

**Goal:** Make the science instantly understandable and the output undeniably real.

**Suggested UI (Next.js + Tailwind)**

- [x] Above the fold: **"The microscope that knows when to look."** Subtitle **"See more. Illuminate less."**
- [x] Main comparison: conventional fixed schedule vs PHOTON, playback synced to the exact same recorded sequence and acquisition budget.
- [x] Large authentic fluorescent-cell images with **MEASURED**, **PREDICTED**, or **GROUND TRUTH (EVAL ONLY)** watermarks/labels.
- [x] Timelines: gray fixed-interval exposure ticks, distinctive PHOTON ticks, highlight annotated events **only in evaluation mode**.
- [x] Toggle **Reveal hidden frames**; show true withheld frames vs predicted states and differences.
- [x] Cards from actual JSON: `X / T` images, exposure proxy, event coverage if valid, reconstruction loss; show provenance. Implemented as a comparison table.
- [x] Interactions that work: play, pause, scrub, policy/budget selection, replay/inspect decision rationale.
- [x] Include an explainer for why skip/acquire decisions happened and a simple legend.
- [x] Small "research mode" panel: saved Gaussian state/component count, scalar heuristic uncertainty and measured GPU kernel benchmark; no invented uncertainty map.

**Required tests**

- [ ] A teammate unfamiliar with the algorithm can say what it does after watching 10 seconds.
- [x] UI updates faithfully to the selected authentic experiment (no hard-coded scores or fictional acquisition traces).
- [x] Skipped future frames are not exposed to the policy during simulated "live" execution; evaluation reveal is a distinct user action. UI only views closed causal runs; no policy executes here.
- [x] Dev/build commands work, no missing assets, animation stable on laptop, backend absence handled if using precomputed run results.

**Demo gate:** Start page → press play → see PHOTON reduce light exposure → reveal withheld cells → show real measured comparison in under 30 seconds. Every visible number traceable to a run file.

**Implementation record — 2026-10-24 (in progress):**

- Local React/Vite/TypeScript app in `apps/web/`, with a pinned npm lockfile. Static viewer of completed causal runs; no policy, fitting, annotation parsing or scoring executes in the browser. No hosted deployment.
- `scripts/build_phase6_assets.py` validates all36 closed artifact ledgers, frozen implementation hashes and the paused checkpoint's approved metric hashes. It writes only ignored `apps/web/public/demo/`: real normalized volume MIPs, exact CPU-rendered saved3D Gaussian forecast MIPs, replay JSON, separate evaluation JSON, original source JSON copies and source hashes. Metric values are copied, never rescored. Manifest is written last; existing outputs are refused.
- Implemented synchronized play/pause/scrub, budget/embryo/comparison selectors, held-measurement versus causal forecast switch, exposure timelines/tick inspection, recorded decision rationale, heuristic state/uncertainty, explicit reveal/hide evaluation, genuine metric tables and matched-target caveats, dataset attribution/source links and original measured CUDA benchmark. Pending image metrics are null with reasons. Equal-budget exposure proxy is compared with all-source imaging, not portrayed as a PHOTON advantage over fixed.
- Design concept and tokens: `docs/design/phase6-{concept.png,design.md}`. Concept cells are illustrative and never shipped as scientific imagery; UI assets derive from actual source TIFFs and saved geometry. Responsive desktop/laptop/mobile layouts, focus states, reduced-motion rules and missing-data/image states included.
- **Final automated verification:** production TypeScript/Vite build passed with complete exported assets;3 Node replay tests passed;6 Python exporter/integration/pixel tests passed in8.03s. All36 exported configs/traces and every approved metric/event field match original saved files; all frozen implementation hashes remain unchanged. Independently calculated actual TIFF projections (t1/269) and rerendered saved3D forecasts (t1/268) exactly match exported PNG pixels. This is display-asset validation, not Phase5 full metric recomputation.
- Export complete:6 conditions/36 runs,540 authentic source-volume previews plus1280 saved causal forecast projections =1820 PNGs;88 original source JSON copies with hashes;128119505 bytes total. Raw images and run artifacts remain untouched and ignored; no exporter/controller/scorer processes left running after completion.
- **Chromium QA:** official Playwright CLI, because browser inventory returned no surfaces. Passed all6 conditions, all comparison selectors, play/pause/scrub/tick inspection, hold/forecast toggle, explicit evaluation reveal/hide, selection resets, exact displayed event/MSE parity against JSON, historical CUDA timing, reduced motion and layouts at1440x1000/1366x768/390x844. No console errors, failed HTTP responses, missing images or mobile page overflow. Play is above the laptop fold. Setup message was verified with the manifest absent. Screenshot review fixed unintended tick-hitbox outlines; concept vs authentic implementation inspected. Initial browser assertions needed state-aware waits/role selectors; final actual-manifest flow passed without mocks.
- **Timed demo gate:** default s2/B54 at12 source steps/s completed all270 source steps, then explicit reveal displayed the real evaluation table in **22.79s** in local Chromium. This measures the precomputed UI replay path, not scientific compute/GPU speed or biological benefit. Human ten-second comprehension remains untested.
- Initial restricted-shell build/test attempts hit Windows child-process/temp permissions; authorized reruns passed. Dependency installation succeeded and exact installed versions are locked. No production deployment, scientific code modification, held-out tuning or resumption of Phase5 occurred.
- Commands: root `.venv/Scripts/python.exe -u scripts/build_phase6_assets.py`; `cd apps/web`, `npm ci`, `npm test`, `npm run dev -- --port 5173 --strictPort`, `npm run build`. Local preview `http://127.0.0.1:5173/`. See README for standalone preview and regeneration instructions.
- **User review — 2026-10-24:** The user reports running the playthrough and approves the appearance: "i ran the play through" and "it looks good to me". Human playback/visual review is accepted. This feedback does not document an unfamiliar viewer explaining the system after ten seconds, so that specific comprehension criterion remains open; no further UI changes requested.
- **Open gate:** formal unfamiliar-viewer ten-second comprehension check remains unrecorded. Phase6 is not marked fully complete. Phase5 remains paused/incomplete; no new scientific claims, held-out tuning or full source metric recomputation.
- **Design reset — 2026-10-24:** User selected **Glimpse** as the demo name and retained the Spatial/Gaussians/Microscope viewer ideas, then rejected the first three themes as generic/AI-looking. No redesign target is approved. Researched and visually inspected actual Eames Institute, FIELD.IO, Isomorphic Labs/Pentagram, Future Observatory and Arc Institute pages; screenshots, source links, inspection limits and proposed specimen-atlas identity are in `docs/design/glimpse/references/README.md`. Research/documentation only; existing UI and frozen scientific artifacts remain unchanged. Phase5 is still paused.
- **Design round 2 — 2026-10-24:** User approved the research direction and particularly liked Isomorphic Labs' 3D presentation. Developed three related compositions (D Window, E Contact, F Study) with a light outlined layout, restrained type, sculptural Gaussian geometry and acquired-image contact strips. Mockups and scientific/interaction constraints: `docs/design/glimpse/round-2/README.md`. E is the recommended composition; user selection remains pending. Generated specimens are illustrative, never run evidence. No app or scientific code changed; Phase5 remains paused.

**Record:** URL: `http://127.0.0.1:5173/` (local dev command above) · User playthrough/visual review: **approved** · Formal ten-second comprehension result: _pending_ · Browser QA: **passed**, three viewports/all6 conditions.

---

## Phase 7 — Final audit, backup plan and Devpost

**Goal:** Shipping-quality prototype with repeatable technical proof.

- [ ] Fresh dependency/install walkthrough verified; `.env.example` if needed; dataset download instructions and terms.
- [ ] Run complete offline experiment and test suite from scratch; record exact commands and outputs.
- [ ] Verify `README` clearly distinguishes scientific hypothesis, measured results, current limitations, and future real-hardware integration.
- [ ] Check data licensing, generated-file provenance, credits for CellSplat4D / NVIDIA CUDA Rust / Cell Tracking Challenge / Pycro-Manager.
- [ ] Confirm Fresh off the Frontier eligibility: name recent publication/release and point to the specific code that uses it.
- [ ] Film 60–90-second backup demo and save **true** run artifacts/screenshots for networking/demo failures.
- [ ] Prepare 3–4-minute pitch: harm from excess illumination → PHOTON's next-exposure decision → real side-by-side proof → novel 2026 technology → where scientific use could go.
- [ ] Explicitly avoid unmeasured biological viability and clinical claims.
- [ ] If benchmarking does not beat baseline, identify valid successes (e.g., faithful causal scheduler, verified GPU kernel, difficult case study) rather than misrepresenting comparative quality.

**Pass criteria:** Presentation works without relying on cloud APIs, tests green or documented limitations, all displayed results reproducible, new-tech claim is concrete.

**Record:** Build commit/hash: _pending_ · Full test command: _pending_ · Demo backup path: _pending_

---

## Phase 8 — Stretch only (prioritize one, not all)

- [ ] **CellSplat4D-adjacent improvements:** fitted 3D+t Gaussians with explicit lifespans and PSF-aware rendering. Test against the simpler model; document approximations.
- [ ] **Multi-well OS scheduler:** multiple tracked wells compete for limited imaging slots; budget- and fairness-aware selection. Demo an actual improvement in aggregate event coverage, not just task cards.
- [ ] **Pycro-Manager export:** map decisions to acquisition events, test with a stub/mock; no real hardware operation promised.
- [ ] **Event classifier:** trained only on a separate development sequence; calibrated and evaluated on a held-out sequence. Track false positives/missed events.

**Exit gate:** At least one stretch capability is real, tested, and adds measurable value. Otherwise drop it and polish Phase 7.

---

## Decision log (update every phase)

### 2026-10-24 — Six-target appearance probe completed: negative accuracy result

User authorized the bounded probe. Executed `scripts/probe_appearance_forecasts.py`
against verified closed acquisition archives, with one numerical-library thread.
Six fixed source targets yielded11 eligible comparisons; watershed's target261 was
excluded because it was acquired. No replacement/tuned targets or mixing weights.

Corrected forecasts lose to raw hold on both MSE and MAE in all11 cases (original0/6,
watershed0/5 wins). This rejects an accuracy-upgrade claim for this selected panel.
`scripts/verify_appearance_probe.py` passed sources/archive/image hashes, causal-history
and exclusion checks; all44 baseline scalar comparisons match the full-run ledger.
Three earlier controlled tests passed. No second independent corrected-volume rerender.
Inspected the t196 watershed comparison. Post-registration execution interval was72.5s,
excluding startup/input checks; not a performance benchmark.

Results: `docs/APPEARANCE_FORECAST_RESULTS.md` and
`runs/appearance-forecast-probe/report.md`. The first full detector comparison still
improves Gaussian MSE but changes only4/54 capture times (50 shared). Next priority is
motion/uncertainty and budget-allocation design, not additional visual complexity.
Original Phase5 remains running separately; no new full benchmark launched here.

### 2026-10-24 — Watershed ablation first pass complete and ledger-verified

PID54664 completed the registered3-schedule s1/B54 comparison at22:39 -04:00.
`scripts/verify_perception_ablation.py` passed source/archive/protocol,24 closed-artifact
hashes, exact budgets/causal ledgers/gaps, target sets, event counts and scalar accounting.
Independent full source rerender remains unperformed; no second full evaluation launched.

Events: fixed334/568, original adaptive325/568, watershed326/568. On212 pairwise-common
adaptive/watershed targets, raw-hold MSE0.00217212286→0.00216290770 (~0.42% lower),
Gaussian-forecast MSE0.00733396278→0.00364671244 (~50.3% lower). Thus the registered
development criterion technically passes, but scheduling gain is only one event and
fixed retains better event coverage. Watershed Gaussian prediction still loses to its
raw hold on the same targets. Own-target raw MSE remains almost unchanged; target-set
conditioning continues to matter. No broad superiority or biological benefit claimed.

Artifacts: summary.json, verification.json, event-audit.json under
`runs/perception-controller-ablation`. Do not restart the completed acquisition job.
Next bounded test is the registered six-target appearance-preserving forecast probe,
using these sealed archives. It is prepared but not yet run on microscopy data.
Original Phase5 PID55068 remains active in step3/5, last observed t150 of its current
group's independent source recomputation. Its frozen implementation remains intact.

### 2026-10-24 — Acquisition ablation closed; image scoring remains active

All three development acquisition runs closed at54 volumes and the original adaptive
schedule exactly reproduced the prior deployed s1 schedule. PID54664 is still running
offline image evaluation in `runs/perception-controller-ablation`; latest observed
progress t25/269. Do not restart or edit its44 registered source files. The independent
Phase5 runner PID55068 remains active in step3/5; this new experiment is3 schedules
on one embryo/budget, not another36-run Phase5 matrix. User asked for clarification;
no request to stop either runner was made.

After closure, an event-only audit of complete traces and the canonical XML graph
reported fixed334/568, original adaptive325/568, watershed326/568. This is one additional
event versus original and eight fewer than fixed, not substantial scheduling progress.
Image-error results and the registered combined criterion remain pending. Event-only
artifact: `runs/perception-controller-ablation/event-audit.json`.

Prepared a separate, parameter-free appearance-preserving forecast probe: acquired
image plus predicted Gaussian change. Three controlled tests passed in24.71s for
zero-change preservation, known model change with static residual texture, clipping,
immutable output and provenance guards. This is synthetic correctness, not microscopy
success. Code under `experiments/forecasting/`; plan `docs/APPEARANCE_FORECAST_PLAN.md`.
`scripts/probe_appearance_forecasts.py` uses only six fixed selected targets and saved
causal archives after the input ablation completes and passes ledger verification.
It has not yet executed on source data. Report/verification tools are prepared.

### 2026-10-24 — Registered full causal detector ablation started

User authorized further scientific implementation/testing. Registered
`docs/PERCEPTION_ABLATION_PLAN.md`: s1 only,270 frames,54 acquisitions,seed42; fixed,
original paced_robust adaptive, and identical adaptive settings with watershed fitting.
Added isolated `scripts/run_perception_ablation.py`, source ZIP/hash registration,
lower Windows process priority, one-thread numerical libraries, and per-frame scoring
only after all three acquisition runs close. No candidate source inside the frozen
PHOTON inventory. Pairwise/common/own withheld targets and losses will all be retained.

11 targeted pipeline/detector tests passed in4.15s, including a future-pixel perturbation
test: randomizing every unacquired image leaves the candidate schedule and forecasts
unchanged. Original controller globals remain isolated. Added verification tooling and
four passing archive/protocol tampering and stage-gate tests in2.61s.

Live experiment: `runs/perception-controller-ablation`, PID54664, tool session87658.
At the latest check, fixed and original adaptive runs were closed, the original adaptive
schedule exactly reproduced the prior deployed s1 run, and watershed had acquired11/54
volumes through t41. No image/event outcome for the new controller is available yet.
Use status.json, run.log and the live PID/session; do not duplicate this experiment.

Supplementary annotation SHA registered while acquisition was active; it matches the
earlier pre-experiment count audit. This is explicitly separate from the original
protocol, whose source path was fixed but omitted the XML byte hash. No labels were
parsed by this supplement or supplied to the controller. Source/ledger/full-rerender
verification is available in `scripts/verify_perception_ablation.py` after completion.

Phase5 PID55068 remains live in independent recomputation step3/5. Its s2/B27 group
completed recomputation and the next group started. No phase gate newly marked complete.
Sol High was recommended for critical pipeline/evaluation review; no switch assumed.

### 2026-10-24 — Final hero choreography after user approval

User approved the sculptural3D scene and authorized remaining hero refinements.
Tied acquisition illumination to the conceptual cycle: Observe sweeps through the
specimen, Estimate turns acquisition light off, Decide emits one brief pulse.
Retained the approved composition, manual controls and reduced-motion behavior.
Production build passed; browser checks passed for drag/keyboard pixel changes,
pause/resume, stages, offscreen suspension, reduced motion, six responsive widths
and context-loss fallback. Inspected the light-off model capture. No scientific
algorithm or result changed. Further hero expansion is not a current priority.

### 2026-10-24 — Replaced flat hero particles with sculptural 3D

User rejected the first right-side illustration as flat/basic. Rebuilt it with
deformed3D nuclei, a transmissive outer membrane, studio reflections, directional
lighting, a moving illuminated slice, restrained bloom and actual drag/keyboard
rotation. Estimate expands the specimen into a wire model, which then reforms.
Retained the explicit problem/approach narrative and conceptual-data label.

Inspected desktop/mobile and close-up captures. Corrected washed-out exposure and
glass depth writing that initially obscured the wire model. Production build and7
Node tests pass; browser checks additionally prove drag/keyboard rotation changes
rendered pixels. Pause, reduced motion, offscreen suspension, fallback, six responsive
widths and replay/evidence regressions pass. No scientific results were changed.

### 2026-10-24 — Explicit hero narrative and interactive WebGL illustration

User requested a more compelling hero with explicit problem/approach and motion
inspired by React Bits/Awwwards. Replaced the small static diagram with a custom,
lazy-loaded Three.js specimen illustration, light sweep, cursor response and selectable
Observe/Estimate/Decide stages. Retained chalk/charcoal/oxide branding. Added explicit
problem/approach explanations, pause/resume, reduced-motion behavior, offscreen/hidden
render suspension and static WebGL/context-loss fallback. No fabricated outcomes or
new animation dependency. Technical/design references are in the implementation brief.

Production build and7 Node tests passed. Browser checks passed for the new motion/
fallback behavior plus existing replay/evidence/budget controls. Screenshots inspected
on desktop/mobile; no overflow at six widths from320 to1440px. The existing Three.js
chunk warning remains. Phase6 human comprehension gate remains open.

Phase5 runner PID55068 remains present, now step3/5: full source-score recomputation.
No scientific or frozen evaluation files were changed for this frontend task.

### 2026-10-24 — Causal perception probes and full freeze validation

Ran the registered three reset histories [0,127,132], [0,188,193], [0,254,260],
forecasting at horizons1/3. Candidate Gaussian MSE improves on the original in all6
probes; raw hold beats both in all6. Candidate MAE improves in3/6. These sparse-history
development probes do not reproduce full policy states or establish acquisition gains.
Artifacts and all outcomes are recorded in `docs/PERCEPTION_EXPERIMENT.md`.

Added a private-tracker isolation/input-boundary test;11 targeted tests pass. Discovered
that adding a module inside the frozen package changes its aggregate/inventory hashes
even if the37 original files match. Relocated the experiment outside that package to
`experiments/perception/watershed.py`. Full `check_registration` now passes, including
aggregate hash and archive. Preserved exact original experiment sources with verified
hashes under each result directory; summaries unchanged. Runner PID55068 remains live,
s3/B89 image scoring, most recently t125/269. No benchmark process interrupted.

### 2026-10-24 — Implemented experimental watershed perception

User explicitly authorized implementing useful tools/approaches. Added isolated
`photon.experimental_perception`: marker-controlled intensity watershed before
Gaussian fitting. This addresses a measured baseline failure: t260's1,762,951-voxel
region contains99.4784% of thresholded foreground and is rejected for size.
`scripts/audit_detection_regions.py` reproduces saved counts on five acquired s1
frames and distinguishes small/large rejections. No s2/s3 model selection.

Registered panel/defaults in `docs/PERCEPTION_EXPERIMENT.md` before candidate volume
execution. `scripts/compare_perception_panel.py` saved source-hashed full-volume
in-sample errors and comparison images. Fitting MSE is equal at t0 and lower on the
other four frames; t2600.02935190→0.00867538,17→263 components. This is not segmentation
recall, forecast performance, acquisition benefit or biological benefit. Inspected
t132/t260 images show remaining merged/broad components.

10 targeted tests passed. scikit-image0.26.0/lazy-loader0.4 installed only under
`.tools/perception-deps`; frozen environment/dependency declarations unchanged.
Main policy does not import the candidate. All37 frozen hashes still match.
PID55068 remains live, step1/5; s3/B54 first pass finished and s3/B89 started.
Phase5/6 gates remain open. Next: isolated causal forecast probes and spatial/manual
validation before controller integration.

### 2026-10-24 — Authorized opening-page elevation and perception preflight

User authorized continued implementation while away. Added an editorial introduction
in the selected chalk/charcoal/oxide theme, an explicitly conceptual acquisition
diagram, and a direct link into the recorded equal-budget experiment. Research details
now explain CUDA Rust's dated releases, actual computation, CPU parity, integration
difficulties, and current limits. No generated specimen images or fabricated metrics.

Production build passed (existing large Three.js chunk warning). All 7 Node tests
passed. Headless Chromium verified initial midpoint preview, no evaluation JSON fetch
before reveal, anchor clearance, playback from zero, evidence open/close, research
navigation, budget selection, and no horizontal overflow at 1440, 1024, 390, 320px.
Desktop/mobile screenshots inspected. Human comprehension remains untested; Phase 6
is not newly declared complete.

Added `scripts/audit_perception_counts.py` and four passing targeted tests. The audit
only reads saved s1 development observations and XML spot counts; no volumes, model
weights, training, inference, or policy changes. At frame260, 17 fitted components
versus541 annotated spots and1954 size-rejected regions warrant a perception audit.
These counts are not segmentation recall and cannot diagnose merging versus small
fragments. Detailed evidence and revised next experiment are in the research brief.

Phase5 runner PID55068 stayed present, step1/5; latest observed progress t175/269 in
the current scoring group. All37 frozen implementation hashes matched. No runner
restart, duplicate evaluation, source regeneration, or heavy experiment was launched.

### 2026-10-24 — Astra frontier research review

Completed a literature/repository and read-only implementation review in
`docs/GLIMPSE_DEEP_RESEARCH.md`. Strongest new candidate: June2026 CellposeDINO
for acquired-volume nucleus perception, subject to a bounded development audit
against current components and a simple watershed baseline. Subsequent proposed
direction: empirical forecast reliability and compact CUDA Gaussian scoring that
feeds acquisition decisions. No scientific adoption or implementation is approved
by this record; all candidate gains, resource requirements and transfer quality
remain untested. Existing frozen protocol, sources, runner and results are unchanged.

Corrected recency interpretation: cell-fate paper public March2026 before October
journal publication; hybrid-EDA public April2025; uncertainty rescanning public
October2023; cuTile Rust has April2026 tagged-release evidence preceding September
announcement. CELLECT is directly relevant to MSKCC but predates the strict current
12-month window and introduces checkpoint-training-overlap questions. Full source
links and limitations are retained in the research brief. User confirmed Astra.

Read-only runner observations: PID55068 present; s2/B89 first-pass scoring finished;
next group advanced to t75/269, still step1/5. Phase5 is incomplete/not verified.
No inference, tests, installation or heavy experiment was launched for this research.
Documentation-only review does not satisfy any new phase acceptance criterion.

### 2026-10-24 — Head-to-head demonstration clarification

Updated elevation notes with the user's requested comparison discussion. Proposed
270-volume reference vs54-volume fixed vs54-volume adaptive distinguishes 80%
capture reduction against every-frame imaging (both sparse schedules) from the
unproven value of adaptive timing at equal budgets. Documented that replay provides
no measured health/death/damage outcomes and cannot support invented biological
comparisons. Added prior-work links (2022 event-driven acquisition,2026 hybrid-EDA)
and accurate contribution positioning. Documentation only; no UI/science changes
or interference with the user-run evaluation.

### 2026-10-24 — Research elevation and account-switch handoff

Saved `docs/GLIMPSE_ELEVATION_RESEARCH.md`: research links, proposed uncertainty/
division-risk/ensemble/CellSplat4D experiments, budget-demo idea, experiment gates,
causality and model-selection guidance. The user agreed to investigate these;
latest instruction remains documentation/discussion only, no code changes.
Updated current handoff to distinguish the historical pause from the user-launched
Phase 5 resume: PID55068 existed and log had reached t100/269 at this check.
No evaluator was started or stopped, and no frozen file or result was modified.
Prior source/UI/runner checkpoint `f77c213` is pushed to origin/main. New research
directions are proposals, not implemented capabilities or measured improvements.

### 2026-10-24 — User-operated Phase 5 background runner

Added `scripts/finish_phase5.py` and root `PHASE5_RUN.md` at the user's request
before closing Codex/VS Code. The wrapper runs the existing frozen evaluate,
verify, evaluate --recompute, report and failure-inspection commands, in order;
stops on a failed exit; logs to `runs/phase5-runner/latest.log`; publishes stage/
PID/state in `status.json`; and uses an OS-released Windows lock against duplicate
wrapper launches. Completed first-pass groups are reused by the existing
evaluator; full recomputation is repeated on a fresh wrapper launch.

Verified `--dry-run` starts no evaluation; 3 runner tests passed in0.04s covering
command order, paths with spaces, failure short-circuiting and side-effect-free
dry-run behavior. `run_phase5.check_registration` passed after these additions:
frozen scientific sources/protocol unchanged. **No Phase 5 computation was
started.** User launch instructions explain standalone PowerShell, avoiding
sleep, watching logs, stop/resume granularity and final scientific review.

### 2026-10-24 — Glimpse E / Contact implementation

The user selected E and authorized execution. The Glimpse wordmark, “A glimpse.
Then a decision.” opening, panoramic three-mode viewer and paired contact strips
supersede the earlier literal Phase 6 heading/two-panel presentation. The
scientific specification, frozen PHOTON identifiers and evaluation criteria remain
unchanged. Phase 5 remains paused; Phase 6's human comprehension gate stays open.

Implemented in `apps/web/`: locally bundled Manrope/chalk/oxide identity,
interactive physical-coordinate Three.js splats and 2-sigma model contours,
authentic sampled acquired voxels, held-image toggle, keyboard/orbit/fullscreen,
shared 72-frame contact window, explicit recorded preview (first Play rewinds to
0), research provenance and evaluation reveal/close. Missing geometry/WebGL falls
back to actual microscope images. No illustrative specimen asset enters the app.

`scripts/build_glimpse_spatial.py` exports saved causal states and sampled source
voxels without fitting, scheduling or scoring: 546 files, six conditions, 1,620
model frames. Physical conversion, full covariance, sampling and file/source
hashes are tested. Scientific paths remain frozen.

Final checks: 9 Phase 6 Python tests passed in29.18s; 7 Node tests passed;
TypeScript/Vite production build passed. Actual GPU shader passed three analytic
129×129 projection comparisons (maximum alpha error1LSB, tolerance2). Chromium
passed all six conditions and metric parity, playback/scrub/contact/image/mode/
research/evidence/fullscreen interactions, and 1440×1000,1366×768,390×844 layouts;
no normal-flow console errors or failed responses. WebGL-disabled/missing-spatial
fallbacks passed. Full3D 270-step playback+reveal23.653s, resource counts bounded
at5 geometries/5 programs. No new scientific performance claim follows.

Accepted E and final browser screenshots were visually compared; actual model
density intentionally differs from the illustrative mockup. Detailed fidelity,
test evidence and limitations: `docs/design/glimpse/implementation.md`.
Sol High recommendation for covariance work is no longer needed; Sol Medium
suffices for remaining UI polish. Manual model switching was not assumed.

| When | Decision | Why | Evidence / consequence |
|---|---|---|---|
| 2026-10-23 | Select **PHOTON**: adaptive light-budgeted microscopy | Clear scientific use, compelling demo, frontier 2026 Gaussian modeling / Rust GPU work | Initial concept / spec |
| 2026-10-23 | Prioritize **causal replay and equal-budget validation** ahead of CUDA and UI | Prevents polished but scientifically invalid demo | Design requirement |
| 2026-10-23 | Start with **simplified Gaussian model**; full CellSplat4D reproduction is stretch | 48-hour constraint and uncertain reproducibility | Technical risk reduction |
| 2026-10-23 22:05 -04:00 | Phase 0 verified with CUDA Rust blocked; select CPU fallback for Phase 1 | WSL GPU visible, Linux build tools absent; native CUDA 12.0 insufficient | Official example failed before compilation; retry compatible Linux toolchain before Phase 4 |
| 2026-10-23 22:05 -04:00 | Minimal Python package and labeled synthetic fixture only | Keep Phase 0 bounded and avoid premature scientific claims | Three bootstrap tests passed; Phase 1 not started |
| 2026-10-23 22:31 -04:00 | Reclassify CUDA Rust toolchain as working | User installed Linux CUDA 13.3; source Rust environment and set CUDA_TOOLKIT_PATH | Official hello-world and SAXPY exited 0 on RTX 4070; 32 exact arithmetic assertions passed. Phase 4 scientific kernel still required |
| 2026-10-23 22:41 -04:00 | Keep Phase 1 in progress despite passing fixture tests | Actual CTC archive unreachable; no real lineage/event audit or real-data demo | 18 tests pass; real-data completion gate remains closed; no Phase 2 work |
| 2026-10-23 22:41 -04:00 | Separate offline annotation audit from replay policy inputs; exact B scheduling | Prevent future/label leakage and unequal-budget comparisons | Trusted replay owns clock; no oracle/sequence passed to policy; documented baseline rounding |
| 2026-10-23 23:25 -04:00 | Audit MSKCC as a 3D+t replacement without silently changing primary data | User requested replacement suitability while independently searching for CHO | Strong candidate: 1695 annotated divisions within common first270 windows; full-window ingestion and replay still pending |
| 2026-10-23 23:25 -04:00 | Separate temporal lineage consistency from spatial coordinate agreement | s2/s3 TSV and XML coordinates differ but IDs/frames/edges match | Event-time counts supported; positional accuracy scoring deferred; exact discrepancies documented |
| 2026-10-23 23:35 -04:00 | Adopt MSKCC as sole required dataset family; s1 development, s2/s3 evaluation, frames0..269 | User authorized replacements after CHO remained unavailable; keep true3D and limit integration scope | Spec/data gate amended; 2D sources optional, no unsupported CHO evaluation claim |
| 2026-10-24 00:00 -04:00 | Verify Phase1 on complete s1 window; reserve full evaluation-image ingest for Phase5 | Authentic same-budget replay required before model work | 54/270 each; 270 decisions each; repeat byte-identical; 34 tests pass |
| 2026-10-24 00:09 -04:00 | Retain MSKCC after auditing user-suggested Broad SIM+ and Zenodo CE sources | Synthetic data cannot replace real evidence; CE adds format/reuse constraints without demonstrated gain | Source access and bounded audits recorded; 34 tests pass, verified Phase1 artifacts unchanged |
| 2026-10-24 08:58 -04:00 | Verify Phase 2 with a simplified causal CPU Gaussian model, held shape/intensity and physical-unit tracking | Establish numerical/causal correctness before adaptive scheduling; avoid unvalidated growth extrapolation | 48 tests; real 3D forecast and independent post-hoc artifact checks; no GPU claim |
| 2026-10-24 08:58 -04:00 | Keep and report the real forecast's loss to hold-last; distinguish heuristic uncertainty from calibrated probability | Phase 2 requires a working truthful prediction, not a fabricated accuracy win | Whole-volume and foreground errors both worse; texture/segmentation limits visible; independent-embryo benchmark and ablations still required |
| 2026-10-24 09:12 -04:00 | Use exact finite-horizon feasibility for both acquire/skip successors, including terminal maximum age | Prevent early budget depletion and impossible late catch-up while preserving exact B | Exhaustive independent schedules agree;59 tests pass; all real adaptive gaps2..12 and exact54 captures |
| 2026-10-24 09:12 -04:00 | Verify Phase 3 scheduling while retaining its early-spending weakness and null quality metrics | Nonuniform sampling is functional evidence, not proof of improved information retention | 109 coverage-reservation skips,10 late max-gap captures; repeated six artifacts identical; quality/event evaluation remains Phase5 |
| 2026-10-24 10:11 -04:00 | Adopt paced_robust after the fixed five-run development comparison | More covered events than original with lower matched-target raw-hold MSE; no s2/s3 feedback | 325/568 versus192/568;0.00239687 versus0.00301488;71 tests and exact deployed rerun |
| 2026-10-24 10:11 -04:00 | Report fixed's wins and Gaussian losses alongside the refinement | Different target sets change rankings; Gaussian appearance/motion remains weak | Fixed334 events and lower own-target raw error; selected lower common-target raw error; no overall/held-out/biological advantage claimed |
| 2026-10-24 11:28 -04:00 | Verify native CUDA Rust Gaussian renderer with conservative boundary repair and3D launch grid | Actual scientific computation must match CPU and work on full volumes, not just smoke fixtures |80 Python tests/native checks; real max error1.79e-7; exact CPU-equivalent acquisition traces |
| 2026-10-24 11:28 -04:00 | Retain CPU default despite faster warmed GPU interval | Measured subprocess/context/JIT/files/transfer overhead makes every caller case slower | Real field85.68ms CPU,49.30ms device,5335.46ms full caller; raw samples/chart retained; no app-speedup claim |
| 2026-10-24 | Pause Phase5 and allow Phase6 before its gate, at the user's explicit request | Continue building with authentic partial artifacts while retaining scientific gates | All36 trajectories/event audits saved; image scores2/6 conditions; evaluator/orchestrator stopped; full recomputation not started; manual resume skips completed summaries |
| 2026-10-24 | Implement Phase6 as a static React/Vite viewer of closed runs | Local replay stays independent of paused science; no backend or cloud dependency | All36 configs/traces and actual metrics/event audits exported; full3D saved forecasts rendered for display only;6 exporter +3 replay tests/build/three-viewport Chromium checks pass. Human comprehension gate still pending |

## Experiment log template (append after every meaningful run)

```text
### YYYY-MM-DD — <experiment name>
- Goal:
- Dataset + sequence + annotation availability:
- Code commit / version:
- Backend, GPU/CPU and toolkit:
- Configuration: budget, seed, method parameters:
- Commands executed:
- Test outcome:
- Measured metrics:
- Failure cases / known limitations:
- Decision / next step:
```

## Fast starting instruction for Codex

> Read `PHOTON_SPEC.md` and `BUILD_PHASES.md` in full. Inspect the repository. Start with Phase 0 only: establish the smallest runnable Python scientific project, smoke-test the official CUDA Rust toolchain if it is available, and report observed environment details. Write tests and actually run them. After completing Phase 0, update the dashboard, checkboxes, evidence, blockers, and decision log in `BUILD_PHASES.md`; then continue to Phase 1 only if the gate passed. Make no fabricated claims or precomputed demo results. Preserve future-frame isolation in all subsequent code.
