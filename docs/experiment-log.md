# PHOTON experiment log

## 2026-10-23 22:05 -04:00 — Phase 0 bootstrap

Repository initially contained only AGENTS.md, PHOTON_SPEC.md, BUILD_PHASES.md;
all were untracked, and Git had no HEAD commit. Both primary documents were read
in full before code changes. No datasets, policies, evaluations, or benchmarks
exist at this phase.

### Environment observed

| Component | Observation |
|---|---|
| OS | Windows NT 10.0.26200.0; PowerShell 5.1.26100.9711 |
| Python | CPython 3.13.5, base executable in Anaconda; isolated `.venv` created |
| GPU | NVIDIA GeForce RTX 4070 Laptop GPU, 8188 MiB, compute capability 8.9 |
| Driver | 581.57; `nvidia-smi` reports CUDA driver capability 13.0 |
| Native toolkit | `nvcc` release 12.0, V12.0.76 (distinct from driver capability) |
| Native Rust | rustc 1.91.0 (f8297e351 2025-10-28), cargo 1.91.0 (ea2d97820 2025-10-10) |
| WSL | Ubuntu-22.04, WSL version 2; Ubuntu 22.04.5 LTS, kernel 6.6.87.2-microsoft-standard-WSL2 |
| WSL GPU | `nvidia-smi` successfully sees the same GPU and driver |
| WSL tools | `rustc`, `cargo`, `nvcc`, `tileiras` not found on login-shell PATH |

Commands: `python --version`, `py -0p`, `nvidia-smi`,
`nvidia-smi --query-gpu=name,driver_version,memory.total,compute_cap --format=csv,noheader`,
`nvcc --version`, `rustc --version`, `cargo --version`, `wsl --status`,
`wsl --list --verbose`; WSL `uname -a`, `cat /etc/os-release`, GPU query,
`command -v rustc cargo nvcc tileiras`, and version commands.

### Official CUDA Rust spike: BLOCKED WITH CAUSE

Cloned `https://github.com/NVIDIA/cuda-rust.git` with `--depth 1` into ignored
`.tools/cuda-rust`. Tested upstream revision:
`fc747196f2d46dce41bd844e3f5b1c5882751f2b` (no PHOTON GPU crate implemented).

Attempted from PowerShell:

```powershell
wsl -d Ubuntu-22.04 -- bash -lc 'cd /mnt/c/Users/gael8/Coding/gator-hack-26/.tools/cuda-rust/cutile-rs && cargo run -p cutile-examples --example hello_world'
```

Outcome: exit 127 inside bash, `cargo: command not found`; WSL wrapper returned
nonzero. An initial attempt used the upstream root directory; the corrected
attempt uses the nested `cutile-rs` workspace. Neither reached compilation.
No GPU kernel executed and no GPU timing or parity result exists.

Official setup lists Linux and Rust >=1.89; the Ada target requires Tile IR
>=13.2, with CUDA 13.3 recommended. Native toolkit 12.0 is insufficient for that
path. WSL GPU visibility alone does not demonstrate toolchain compatibility.
Fallback: CPU science work in Phase 1. Before Phase 4, install Linux Rust and a
compatible CUDA toolkit/assembler in WSL, validate driver compatibility, then
retry this exact example against a recorded upstream revision. No driver or
system toolkit changes were made during this spike. cuda-oxide was not tried;
switching models does not resolve missing Linux build prerequisites.

### Python functionality and verification

Created an editable `services/science/photon` package, bootstrap CLI, separate
observed/predicted types, and a deterministic synthetic Gaussian clip with a
scripted split. This generator is a fixture, not the Phase 2 reconstruction
algorithm. Synthetic provenance is retained in exported NPZ metadata.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/run_experiment.py --help
.\.venv\Scripts\python.exe scripts/run_experiment.py --synthetic-output runs/phase0/synthetic.npz --seed 42
```

Results: installation succeeded; **3 passed in 4.02s**; help exited successfully;
NPZ exported with shape `[8,32,32]`, source `synthetic`, seed 42. Tests verify
repeatability, different seeds, finite bounded pixels, scripted morphology,
distinct frame tags, CLI roundtrip metadata/pixels and overwrite refusal.
The first test/CLI attempt happened while pip was still installing, failed with
missing pytest/photon imports, and was rerun successfully after installation.
`pip freeze --exclude-editable` printed dependency versions but also a VCS
warning because this repo has no HEAD. Exact versions were recorded in
`requirements-dev.lock`; use `pip list` to inspect this pre-commit environment.

Follow-up at 22:07 -04:00: README's `pip install -r requirements-dev.lock` and
`pip install --no-deps -e .` both succeeded in the existing environment (not a
fresh-machine test). `pip list --format=json` confirmed the pinned versions;
`pip check` reported `No broken requirements found`.

`git ls-files` returned empty: nothing is committed. `git check-ignore` confirmed
`.venv/pyvenv.cfg`, generated NPZ, upstream checkout, a raw data path, and `.env`
are ignored. No secret files or raw datasets were created. No scientific metrics
were computed. Phase 1 is next; future clips/annotations must remain sealed in
the oracle and must never enter controller state.

### Research references

- [CellSplat4D](https://arxiv.org/abs/2610.04199): abstract/title and Oct. 3, 2026 submission verified; full method not reproduced or assessed here.
- [NVIDIA CUDA Rust announcement](https://developer.nvidia.com/blog/introducing-cuda-rust-two-tracks-for-writing-gpu-kernels): spec reference; announcement date not independently audited in Phase 0.
- [NVIDIA source and setup](https://github.com/NVIDIA/cuda-rust/tree/main/cutile-rs): inspected at revision above.
- [cuTile introduction](https://nvlabs.github.io/cutile-rs/main/guide/introduction.html), [hello world](https://nvlabs.github.io/cutile-rs/main/tutorials/01-hello-world.html), [compatibility matrix](https://nvlabs.github.io/cutile-rs/main/reference/compatibility.html): inspected for spike requirements.
- [Cell Tracking Challenge](https://celltrackingchallenge.net/datasets/): Phase 1 dataset/terms audit pending.
- [Pycro-Manager adaptive acquisition](https://pycro-manager.readthedocs.io/en/latest/adaptive_acq.html): spec reference only; integration deferred.

## 2026-10-23 22:17 -04:00 — CUDA setup investigation before Phase 1

Correction to initial diagnosis: Linux Rust is installed under `/home/gael/.cargo/bin`
but absent from the automation login shell PATH. Direct binaries report rustc/cargo
1.99.1. Existing `~/.cargo/env` repairs PATH when sourced. Retried:

```bash
source ~/.cargo/env
cd /mnt/c/Users/gael8/Coding/gator-hack-26/.tools/cuda-rust/cutile-rs
cargo run -p cutile-examples --example hello_world
```

Upstream rust-toolchain.toml automatically installed pinned Rust 1.98.0. Cargo
downloaded dependencies and compiled until `cuda-bindings v0.5.0` failed:
`Neither CUDA_TOOLKIT_PATH nor CUDA_HOME is set, and no CUDA 13.0+ toolkit was
found in default locations`. No GPU kernel ran. Ada execution still needs Tile
IR >=13.2; choose recommended CUDA 13.3 toolkit for the retry.

WSL user `gael` has sudo group membership, but `sudo -n true` reports a password
is required. `/usr/lib/wsl/lib/libcuda.so*` exists. WSL root filesystem has 934 GiB
available. `build-essential` 12.9ubuntu3 installed; libclang-dev not listed.
User action: install toolkit and libclang-dev using interactive Ubuntu sudo;
do not send passwords in chat. No driver update is established as necessary:
driver 581.57 meets NVIDIA's CUDA 13.x family baseline (>=580), subject to feature
compatibility and actual example execution.

Sources rechecked: [cuTile setup](https://github.com/NVIDIA/cuda-rust/tree/main/cutile-rs),
[NVIDIA WSL guide](https://docs.nvidia.com/cuda/wsl-user-guide/index.html),
[driver compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html),
[WSL package repository](https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/).
The WSL repository lists cuda-toolkit-13-3 and cuda-keyring_1.1-1_all.deb.

## 2026-10-23 22:31 -04:00 — CUDA Rust execution verified

After user installed the toolkit, independently checked in WSL:

- `cuda-toolkit-13-3`: 13.3.1-1; nvcc V13.3.73; tileiras V13.3.36.
- `libclang-dev`: 1:14.0-55~exp2.
- Upstream workspace uses rustc 1.98.0 (88d9e12ae 2026-08-18), cargo 1.98.0
  (797e8a9bc 2026-08-05).
- Same NVIDIA revision `fc747196f2d46dce41bd844e3f5b1c5882751f2b`, cuTile 0.5.0,
  RTX 4070 Laptop GPU, Windows driver 581.57.

Executed via `wsl -d Ubuntu-22.04 -- bash -lc`:

```bash
source ~/.cargo/env
export CUDA_TOOLKIT_PATH=/usr/local/cuda-13.3
cd /mnt/c/Users/gael8/Coding/gator-hack-26/.tools/cuda-rust/cutile-rs
cargo run -p cutile-examples --example hello_world
```

Exit 0. Generated Tile IR, compiled and launched the Rust GPU kernel. Output:

```text
Hello, I am program <0, 0, 0> in a kernel with <1, 1, 1> programs.
```

Cargo reported a 2m25s development build; this is build output, not a GPU
performance benchmark. The example did not emit a prerequisite `SKIP`.
**Toolchain classification is now working.** No Windows driver change was
required. The initial missing-toolkit blocker is resolved. PHOTON-specific
scientific workload, integration, numerical parity and timings remain Phase 4.

Then ran `cargo run -p cutile-examples --example saxpy` with the same environment
and upstream revision. Exit 0; all **32 exact CPU/GPU arithmetic assertions**
passed. This upstream example computes `y = 2*x + y` with `x=y=0..31`; printed
results range from `2 * 0 + 0 = 0` to `2 * 31 + 31 = 93`. It copies GPU output
back to host and checks each value with `assert_eq!` against the CPU expression.
No prerequisite skip occurred. This checks a real arithmetic kernel and memory
transfers; it is not Gaussian parity validation or a PHOTON speedup benchmark.

## 2026-10-23 22:41 -04:00 — Phase 1 replay, real-data access blocked

- Goal: validated TIFF ingestion, sealed causal replay, equal-budget fixed/random baselines, real training-data audit.
- Code version: PHOTON 0.0.1, no Git HEAD/commit; all files untracked as at start.
- Backend: Python 3.13.5 CPU, NumPy 2.5.4, tifffile 2026.10.15, Pillow 13.0.0. CUDA not used in these runs.
- Commands: `python -m pip install tifffile pillow`, package reinstall with `--no-deps -e .`, `python -m pytest -q`, both CLI `--help` commands, `pip check` (all using `.venv/Scripts/python.exe`).
- Test outcome: final **18 passed in 3.30s**; earlier increments 13 and 16 passed. No broken requirements. Tests include boundary/invalid budgets, deterministic policies, allowed policy inputs, no withheld pixel reads, future perturbation, oracle time/budget/completion checks, output consistency, TIFF errors and controlled lineage parsing.
- CLI run: generated TIFFs from `make_synthetic_clip(42)`, converted to uint16 in ignored `runs/phase1-fixture/01`. Executed `scripts/run_experiment.py --sequence runs/phase1-fixture/01 --dataset-id synthetic-gaussian-test-v1 --source synthetic --budget 3 --seed 42 --output runs/phase1-fixture/comparison`.
- Measured fixture output: fixed `[0,3,7]`, random `[0,1,6]`, exactly 3/8 each, exposure-count proxy 0.375. Both generated config/trace/metrics/timeline/contact-sheet files. Viewed fixed contact sheet: all three panels correctly labeled SYNTHETIC. Null reconstruction and event metrics with reasons. This is a plumbing check, not evidence of biological performance.
- Access failure: official `https://data.celltrackingchallenge.net/training-datasets/Fluo-N3DH-CHO.zip` timed out (Windows curl exit 28 after ~21s; WSL curl exit 28 at 20s). HTTP retry timed out at 15s. HTTPS probe of public CTC host timed out at 10s. DNS data host resolves 147.251.52.183; no archive created. No matching dataset archive found in Downloads.
- Official metadata/terms: reviewed CTC dataset/annotation pages; 9.5min timestep, XYZ spacing 0.202/0.202/1.0 um. Actual frame shape/count, tracks and divisions unknown until download. Public non-CTC scientific use requires organizer permission. Details and sources in `docs/dataset-notes.md`; no public release or email sent.
- Decision: Phase 1 remains in progress. Do not proceed to Phase 2 until real archive audited and real equal-budget CLI demo verified. User can attempt official download through browser and provide a local archive path. No substitution of synthetic data for the real-data gate.

## 2026-10-23 23:06 -04:00 — Candidate dataset investigation

User requested comparing LFCT and Figshare, and explaining CHO's advantages.
Downloaded LFCT MCF10A FLD_3 original RFP ZIP and XML, plus FLD_4 XML from
author-linked Box public shares. Read all FLD_3 TIFF headers; decoded sampled
frames and reviewed annotation-position overlays. Ran
`.venv/Scripts/python.exe scripts/audit_candidate_datasets.py` successfully after
correcting headerless/empty CSV handling. Independent NumPy parse confirmed
418 division records. Both full raw-file and full pixel fingerprints failed to
establish tracking/division whole-video correspondence in Figshare; do not join
those folder labels by name. Machine-readable output and source checksums in
`runs/candidate-audit/audit.json`; report with sources, caveats and recommendation
in `docs/dataset-comparison.md`. LFCT FLD_3: 433 frames, 6656 spots, 16 filtered
graphs, 17 binary branches; XML interval1sec is not reliable physical acquisition
timing. FLD_4 XML: 433 frames, 9877 spots, 44 reported splits, images not downloaded.
Recommendation is LFCT primary, Figshare secondary; no production replay adapter,
benchmark, policy result, dataset requirement amendment or Phase 1 completion
claimed. This is a dataset audit, not a PHOTON scientific result.

## 2026-10-23 23:11 -04:00 — Broader 3D+t search

User asked about preserving 3D+t. Read author Zenodo records 6460303 and
22078388, MSKCC README and Ultrack author portal. Downloaded both Zenodo API
records into ignored data files; licenses identify CC BY 4.0. Bounded curl
byte-range requests against MSKCC's ZIP and the organoid contiguous small ZIP
each returned HTTP 206 and exactly 1024 bytes. No bulk download initiated.
Downloaded Ultrack neuromast .zattrs and coarse .zarray metadata. Findings,
resource costs and scientific limitations recorded in dataset-comparison.md.
MSKCC's three independent embryos are the strongest next volumetric candidate;
first270-frame author caveat and actual annotation completeness require attention.
No implementation or scientific methodology changed, no dataset gate completed.

## 2026-10-23 23:25 -04:00 — MSKCC selective 3D+t audit completed

- User authorized auditing the replacement while searching independently for CHO.
- Added `scripts/audit_mskcc_dataset.py`: ZIP64 inventory and strict HTTP206/Content-Range validation, selected-file download and ZIP CRC/cache validation. No 26.1GB bulk download.
- Cache contains 433089383 bytes: 3 main lineage TSVs, 3 MaMuT XMLs, 15 sampled volumes (0,89,179,269,399 in each embryo). Source API record and inventory retained. Full archive MD5 unverified.
- All samples 41x512x512 uint16; no sampled uint16-max saturation, no sampled out-of-bounds labels after z/5 coordinate conversion. XML spacing 0.15/0.15/0.75um; author cadence75s. Inspected all three contact sheets.
- TSV annotations: s1 129879 spots, 655 divisions total/568 insidefirst270; s2 114937, 653/560; s3 111175, 652/567. Sumfirst270=1695. All links consecutive, all parent IDs resolve, all branch parents div_state1. Later label ranges s1 0..399, s2 0..375, s3 0..369. These are annotation counts, not PHOTON metrics.
- Strict TSV/XML check initially failed on s2. Investigated: every ID/frame/edge agrees; positions differ for163 s2 and102 s3 spots. First270 position mismatch counts154/98. Final script explicitly records discrepancy and requires temporal graph agreement; spatial accuracy scores deferred. Unknown source of position discrepancies.
- Successful final audit command: `.venv/Scripts/python.exe scripts/audit_mskcc_dataset.py > runs/mskcc-audit/final-audit-stdout.txt`. New deterministic mocked-network range tests plus existing suite: **22 passed in 2.36s**. No policy or scientific algorithm added.
- Verdict: strong 3D+t candidate with genuine independent embryos and abundant annotated events; limitations and reproduction in `docs/mskcc-audit.md`. Original CHO target unchanged. Need explicit data-plan amendment if selected, full first270 image ingestion, tested importer and fair real-data replay before Phase1 closes. No claims of speedup, fewer required observations or biological benefit.

## 2026-10-24 00:00 -04:00 — Phase1 verified with authorized MSKCC replacement

- User confirmed CHO unavailable and authorized choosing replacements. Selected one required family: MSKCC, s1 development/s2+s3 evaluation, fixed0..269 windows. PHOTON_SPEC.md and roadmap gate explicitly amended; LFCT/Figshare optional.
- Implemented `scripts/download_mskcc.py` (resumable per-file CRC checks, independent HTTP range readers), native source-window/metadata loader, offline canonical `photon/annotations.py` importer, extra scientific input/graph tests, code/source provenance in artifacts. Selected files written locally; raw/generated paths ignored.
- Full s1 image download completed 2026-10-23 23:55:44 -04:00. All270 source TIFFs CRC-verified; 5849694836 bytes. Full-window TIFF decoding/shape/dtype/hash validation passed: 41x512x512 uint16,75s cadence,XYZ0.15/0.15/0.75um. Full ZIP MD5 not verified or claimed.
- Production annotation importer reproduces568 s1 window divisions (s2/s3 canonical audit560/567). Frame annotations present throughout each first270 window; known spatial representation differences remain deferred. Only offline audit imports annotations; policies receive metadata and acquired observations.
- Exact commands: `.venv/Scripts/python.exe scripts/download_mskcc.py --sequence s1 --workers 4`; `scripts/inspect_dataset.py data/mskcc-audit/mskcc-confocal --output runs/mskcc-phase1-audit.json`; `scripts/run_experiment.py --sequence data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1 --budget 54 --seed 42 --output runs/mskcc-phase1`; same command repeated with `--output runs/mskcc-phase1-repeat` (all venv Python).
- Actual runs: fixed54/270, random54/270, seed42,270 decision rows each; exposure-count proxy0.2 each. Contact sheets reviewed: real measured MIPs with source indices. Reconstruction/event scores remain null with reasons. No winner or biological effect claimed.
- Independent artifact assertions passed: trace acquired indices/config agree, budgets/last-index fields consistent, complete timelines, identical source and code hashes, and all five files per policy byte-identical to repeat. Machine record `runs/mskcc-phase1-verification.json` includes artifact hashes. Source SHA256 `6d53d2e92fb3a452bdba32e13cadc8ae2b7521ffc7460a9913414ad2fdca6917`; code SHA256 `a9392d99895f45f25635d5a215598cf5138c64c8742d76c49a24c36020362f8c`.
- Final tests: **34 passed in3.28s**. `pip check` clean; `git diff --check` clean. No files committed; repository remains without HEAD. New tests exercise native window/geometry, split, missing source frames, directed graph validity and event-window boundaries; earlier causal/leakage/range-integrity tests retained.
- Decision: Phase1 completion gate passed under authorized dataset amendment. Phase2 not started. Before Phase5, provision full s2/s3 evaluation windows and preserve frozen settings. Next work is Gaussian observation fitting, rendering, causal tracking/prediction and uncertainty; scientific CUDA work remains Phase4.

## 2026-10-24 00:09 -04:00 — Broad SIM+ / Zenodo CE suggestions audited

- User authorized adopting alternatives only if better and redoing Phase1 only as needed. Decision: keep MSKCC; no source split/scientific contract changed.
- Broad BBBC035 source page confirms synthetic exact CTC SIM+ copy and29-minute intervals. Downloaded complete150947167-byte GT ZIP; all entries CRC-valid. Remote image ZIP3180529910 bytes supports exact HTTP ranges. Six selected raw/SEG volume pairs decoded and visually overlaid. Actual sequences150/80 frames; SEG masks at every time; lineage binary divisions37/40; two one-child parents in02 recorded separately. No full raw ZIP integrity or actual biological measurements claimed.
- Zenodo4630932 and4630933 API resolve to same version. CE HDF5 image pair4.77GB; whole record15.9GB includes unrelated PH files/model weights. Downloaded both XMLs andCE01 Mastodon and matched published MD5s. Both XMLs declare250 times; CE01 HDF5 metadata matches35x512x708 volume and250 time groups. Small chunk/patch read through strict ranges, int16 storage/gzip. Binary Mastodon model was not decoded; event count/completeness unknown. Explicit source reuse description BY-NC-ND4.0.
- Audit tooling initially failed on LZW codecs, then on missing file-like readinto for HDF5; resolved with isolated imagecodecs2026.10.10/h5py3.16.0 and implemented/tested readinto. A preview command also needed the isolated codec import path; corrected and completed. No application dependencies or science package code modified.
- `scripts/audit_bbbc_ce.py` completed; findings in `runs/bbbc-ce-audit/{bbbc-audit,ce-audit}.json`, report `docs/bbbc-ce-audit.md`. Final tests34 passed in2.69s; pip check clean. Existing Phase1 artifacts still byte-identical to repeat and science code SHA remainsa9392d99895f45f25635d5a215598cf5138c64c8742d76c49a24c36020362f8c.
- No Phase1 replay redo warranted; remains verified. BBBC useful as optional synthetic validation, not integrated. CE offers no demonstrated benefit over already validated real MSKCC. Phase2 not started.

## 2026-10-24 08:58 -04:00 — Phase 2 causal Gaussian model verified

- Goal: implement a real observation-derived 3D state and withheld-time prediction, not a decorative animation. Model-switch recommendation given before difficult numerical work; no switch assumed without user confirmation.
- Added `photon/gaussian.py` (first-acquisition frozen normalization, threshold/components, weighted moments, positive covariance, least-squares amplitude, CPU renderer), `tracking.py` (physical assignment, source-gap damped velocity, explicit birth/retirement/split candidates, held shape/intensity), typed predicted/evaluation frames and post-closure evaluator. Model never receives paths, sequence, oracle or labels. Simplified model limitations and exact units/formulas in `docs/gaussian-model.md`.
- Installed SciPy 1.18.1, updated project dependency and lock, reinstalled editable package successfully. NumPy 2.5.4, CPython 3.13.5, CPU backend. No scientific GPU operation or timing claimed.
- Unit/integration tests: `.venv/Scripts/python.exe -m pytest -q` **48 passed in 4.46s**. Earlier increment 44 passed before four additional boundary/physical-axis/input tests. Full-mask analytic recovery tolerance 2e-4; thresholded moment tolerance 1.5%; independent renderer formula rtol 2e-6/atol 1e-7. Tested split/birth IDs, snapshots, actual source gaps, deterministic predictions/maps and increasing scalar uncertainty. Read spies and all-unseen-frame perturbations verify no truth reads during prediction; changed truth alters only post-hoc errors. Controlled synthetic translation beats raw hold-last, distinct from real-data result below.
- Executed `.venv/Scripts/python.exe -u scripts/run_prediction_demo.py`, redirected stdout to `runs/mskcc-phase2-stdout.txt`, exit 0. Native s1 first270 source window validated; predeclared acquisitions [0,5,10], withheld target12, full270-step replay closed before target read. Seven/seven/five bright components detected at acquisitions, not asserted to be biological nucleus counts. First-acquisition calibration: background2187, scale2057, normalized noise0.03243412505554585; threshold0.1297365002221834. Prediction position scale0.28292126898563924 um, heuristic only. Six-member +/-axis translation ensemble uses no RNG; config seed0 records this fact.
- Actual full-volume MSE0.0011492511713106393 and MAE0.016446842166130262; raw hold-last MSE0.0010383232654541978. Common evaluation-only union ROI >0.1:465551 voxels, forecast MSE0.012568739149017037 versus hold-last0.010504868602816072. **Real forecast loses both comparisons.** No model parameters changed to improve the inspected target. Visual inspection shows Gaussian blobs lose nuclear texture and diffuse signal; source of error has not been separately ablated. This is one development-frame preview, not an adaptive scheduler benchmark or proof of biological benefit.
- `runs/mskcc-phase2/` exports config/state/270 decisions/metrics, prediction/disagreement NPZ, separate GROUND TRUTH (EVAL ONLY) NPZ and six-panel MIP comparison. Computation and scores use full41x512x512 volumes; only display projects Z. Saved-map display gain5 is labeled. Event score null with reason. Uncertainty is not calibrated and does not capture unseen objects or texture.
- `.venv/Scripts/python.exe scripts/verify_prediction_demo.py` exit0: finite arrays, exact budget/history/trace, truth against source TIFF under frozen normalization, independent whole-volume/ROI errors and science-code hash all match. Evidence `runs/mskcc-phase2-verification.json`. Both new CLI help commands pass, post-reinstall `pip check` clean, generated/raw ignore checks pass, `git diff --check` clean (all project files still untracked, no HEAD).
- Source SHA2566d53d2e92fb3a452bdba32e13cadc8ae2b7521ffc7460a9913414ad2fdca6917; science-code SHA25673e6fb3172e29ed78868c76c8feb3066b5a1c48d7c0497f152aafe7ebca1ee31. Earlier Phase1 code hash remains historical evidence.
- Decision: Phase2 gates pass (no accuracy-improvement gate was specified). Shape/intensity hold avoids unvalidated growth extrapolation; splits remain observed hints, not event probabilities. No blocking gate remains. Phase3 is next: causal, explainable, budget/gap-safe scheduler. Do not imply calibrated risk or predictive advantage. Later evaluation must preserve hold-last, investigate fitting/motion ablations on development data, provision full s2/s3 and score frozen settings honestly.

## 2026-10-24 09:12 -04:00 — Phase 3 exact-budget causal scheduling verified

- Goal: real adaptive decisions from observed Gaussian state, with exact volume budget, min/max gaps, terminal coverage and inspectable reasons. Read project documents before implementation; recommended Sol High for feasibility/scientific correctness without assuming an actual model switch. No delegation used.
- Implemented `photon/adaptive.py` with deterministic score, integer-horizon feasibility of both actions, pending-observation lifecycle validation and separate `image_change` baseline. Replay/CLI now support `photon_adaptive`, `image_change` and `all`, export pre-acquisition score/uncertainty/motion/hints/gap and post-acquisition counts, policy/model versions and final model state. All configs validated before comparison begins. No new dependencies or model/data split changes.
- Priority:0.4 uncertainty+0.25 motion+0.55 observed morphology/split hint+0.8 budget-aware gap pressure; threshold1.0. Physical covariance aspect ratios1.8..3.0 give a heuristic shape alert, not division probability; hints decay with gap. Image-change priority uses0.55 acquired-frame MAE-rate proxy+0.8 gap pressure. Full formulas, units and feasibility derivation in `docs/acquisition-controller.md`.
- Feasibility: B includes mandatory0; min/max gaps constrain successive captures, terminal age<=max_gap. Checks integer first-future-capture interval and exact remaining count. Exhaustive independent schedules for total1..8 agree. Boundary budgets/gaps across score thresholds0.001/1/1e6 pass. Impossible budgets fail explicitly rather than silently relaxing constraints.
- Tests: initial new10 passed in1.69s; then full58 passed in5.98s. Added animation causality/pixel test: targeted11 passed in2.34s; final full `.venv/Scripts/python.exe -m pytest -q` **59 passed in5.83s**. Synthetic observed pre-split elongation increases pre-split capture density; high uncertainty, empty scenes, unexpected changes and lifecycle covered. Actual model biological predictiveness is not established by this constructed fixture.
- Causality: read spies match exactly acquired indices; replacing every unacquired frame yields identical traces/arrays used for both new policies. Changing the next acquired frame leaves decisions through that acquisition unchanged; only subsequent state changes. No labels, source paths, oracle or evaluator enter controller. Runner captures detailed features before acquiring X[t]. API isolation is cooperative, not a hostile-code sandbox.
- Real command: `.venv/Scripts/python.exe -u scripts/run_experiment.py --sequence data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1 --budget 54 --seed 42 --policy all --min-gap 2 --max-gap 12 --output runs/mskcc-phase3`, stdout `runs/mskcc-phase3-stdout.txt`, exit0. All four policies exactly54/270, count proxy0.2. CPU NumPy2.5.4/SciPy1.18.1; s1 development only. Parameters fixed before run; no annotated-event or withheld-error tuning.
- Actual PHOTON schedule:[0,3,5,8,11,13,16,20,22,26,28,32,34,36,38,42,44,46,48,50,52,55,59,62,65,68,70,73,76,79,82,85,88,92,95,99,102,106,110,114,118,122,127,137,149,161,173,185,197,209,221,233,245,257]. Gap histogram2:13,3:16,4:12,5:1,10:1,12:10; terminal age12. Initial1+threshold43+max-gap10 captures. Skips:minimum53,below-threshold42,reserve-coverage109,budget-exhausted12. Image change gaps4..12/terminal12; fixed5/6/terminal0; random1..18/terminal0, retaining original unconstrained meaning.
- Failure/limitation: heuristic spends many captures early, leaving late captures mostly at maximum gap. Maximum aspect ratio is outlier-sensitive; tracking errors can inflate motion. Feasibility guarantees legal coverage, not scientifically optimal timing. Reconstruction/event scores null with reasons; no quality or biological benefit claimed. Do not confuse priority with event probability. Phase2 real forecast loss remains evidence, not superseded by a favorable scheduling claim.
- Repeated PHOTON using same CLI with `--policy photon_adaptive --output runs/mskcc-phase3-repeat`, exit0. Six files byte-identical:config,decisions,metrics,timeline,observed.png,state.json. `.venv/Scripts/python.exe scripts/verify_adaptive_runs.py --repeat runs/mskcc-phase3-repeat --require-current-code` exit0 independently checks counts/trace chronology/pre-post budgets/score arithmetic/gaps/terminal coverage/source and current-code versions/repeat file hashes. Evidence `runs/mskcc-phase3-verification.json`.
- `.venv/Scripts/python.exe scripts/build_schedule_replay.py` exit0,270-step GIF16581567 bytes plus preview/manifest at `runs/mskcc-phase3/replay.*`. Preview visually checked. Only union of acquired images decoded for animation; each panel holds its own past measurement at skipped steps, labels that display, and never shows hidden truth. Test independently checks read indices, GIF frame count and exact own-past preview pixels. Display min/max is per acquired image, not scoring. Full interactive UI remains Phase6.
- Historical verifier adjustment: scripts default to reporting whether current code matches, with strict `--require-current-code` optional. Recomputed Phase2 saved/source errors unchanged under Phase3 code, output `runs/mskcc-phase2-postphase3-verification.json`; historical model hash retained. Scientific package code hash changes do not invalidate immutable historical run evidence.
- Final environment/CLI checks: `pip check` clean; experiment/animation/verifier help success; generated/raw ignore checks pass; `git diff --check` clean (repository still untracked/no HEAD). Current source SHA2566d53d2e92fb3a452bdba32e13cadc8ae2b7521ffc7460a9913414ad2fdca6917; science SHA256424ba895efc8d551be29a79543c0d938329eecedea0cc9d92eb022f27026a323.
- Decision: Phase3 completion gates pass. No blocking gate remains; early spending and uncalibrated features remain explicit quality risks. Stop this increment before Phase4; next build a scientifically useful batched Gaussian CUDA Rust kernel with CPU parity/actual timing. Phase5 development-only ablations/allocation investigation plus frozen s2/s3 evaluation required before comparative claims. No GPU scientific kernel/speedup or phototoxicity benefit claimed here.

## 2026-10-24 10:11 -04:00 — Bounded Phase3 refinement selected and verified

- User chose one focused refinement before Phase4. Wrote `docs/phase3-refinement-plan.md` before this experiment's scores: fixed, original, pacing, robust, combined; s1 first270 only, B54/seed42/min2/max12; +/-1-frame canonical division coverage. Adoption requires higher event coverage than original and no higher common-target raw-hold MSE, ranked by coverage/MSE/name. No parameter grid or post-score tuning. No s2/s3 data/evaluation used.
- Implementation: soft global discretionary allowance1+floor((B-1)*t/(T-1))+2, hard-feasibility override logged; mean clipped elongation and median repeatedly-observed-track velocity. Legacy presets remain. Added trusted `photon/development.py`, post-closure raw evaluation read, causal forecast/held-scene NPZ export, full3D own/common-target metrics, event coverage and selection. New runner/verifier/report scripts; no new dependencies, renderer or scientific data split changes.
- `.venv/Scripts/python.exe -u scripts/run_phase3_refinement.py` exited0; stdout `runs/mskcc-phase3-refinement-stdout.txt`. All five acquisition oracles closed before labels/truth scoring. Original exactly matches historical indices. Five54/270 schedules,216 withheld targets each,110 common withheld times. All withheld targets scored for Gaussian forecast, held fit and raw hold-last with frozen first-frame normalization; evaluation-only foreground truth>0.1. Geometry saved before reveal, rendering performed offline from immutable descriptors.
- Counts/coverage: fixed334/568 (58.80%), original192/568 (33.80%), paced324/568 (57.04%), robust285/568 (50.18%), combined325/568 (57.22%). A separate vectorized distance-to-capture calculation exactly agrees with evaluator counts. First-half counts27/43/29/34/29 respectively. Combined gaps3:1,4:7,5:41,6:4; terminal age9. Original max gap12/terminal12. Time-weighted observed morphology hint mean original0.93778 versus robust0.40490/combined0.40469; these are diagnostic saturation statistics, not biological validation.
- Common raw-hold MSE: fixed0.002593877198638001, original0.0030148813707635102, paced0.002396484938248152, robust0.0027727098039323065, combined0.00239686669592595. Combined20.50% lower than original,7.60% lower than fixed on these matched targets. Common foreground raw MSE original0.02117596602982864→combined0.015423441381577004, fixed0.01705148542039333.
- Important counterexample: own-withheld raw MSE fixed0.002112048451820563, original0.002712791182792161, combined0.0021630874284391992. Fixed wins own-target error and event coverage. Both target definitions retained; no overall superiority claim. Most gain is pacing; robust features add only one covered event over pacing here. These are development-selection results from one correlated embryo, not independent validation.
- Gaussian limitation: combined common forecast MSE0.009422673762121025, held-fit0.009407540063153719, raw-hold0.00239686669592595. Forecasting strongly loses to raw hold, and motion slightly loses to held Gaussian fitting. All variants' complete whole-volume/foreground/own/common errors retained, including losses. No attempt to make a Gaussian win by changing targets/normalization after reveal.
- Verification: `scripts/verify_refinement.py --prepare-probes --sequence data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1` prepared independent source/scene errors at first/middle/last common targets1/174/268 after closure. `scripts/verify_refinement.py --source-probes runs/mskcc-phase3-refinement/source-probes.json` exited0: exact per-frame aggregate arithmetic, acquisition chronology/budgets/gaps/pacing, source/calibration/version accounting, common intersection, independent event counts and adoption rule. All15 target rerenders/45 estimator comparisons exact. This is source spot-checking plus all-score accounting; a second complete full-source rerender was not executed. Optional `run_phase3_refinement.py --recompute` supports full rerender/equality verification, with reported historical/current hashes and optional strict version matching.
- Selection: rule chooses `paced_robust`. Promoted API/CLI default only after scores/checks; `--controller-variant original` retains original, other ablations exposed, image-change baseline unchanged. Added tests for current CLI default/legacy option and synthetic pre-split density under refined pacing. Original data/method artifacts preserved.
- Tests: initial69 passed in7.81s. Additional integration test initially used unsupported float32 TIFFs, correctly rejected by loader (70 passed/1 failed in24.40s). Corrected fixture to uint16; did not relax loader. Final full suite **71 passed in25.35s**. Covers temporal feasibility/overrides, outlier behavior, missing/simultaneous events, independent metric arithmetic, closed-oracle gates, future perturbation, geometry reload and both deployment presets.
- Deployed rerun: `.venv/Scripts/python.exe -u scripts/run_experiment.py --sequence data/mskcc-audit/mskcc-confocal/mskcc_confocal_s1 --budget 54 --seed 42 --policy photon_adaptive --min-gap 2 --max-gap 12 --output runs/mskcc-phase3-refined`, exit0. New default's decisions.jsonl and state.json byte-identical to combined experiment; config scientific parameters/source/indices match. Evidence `runs/mskcc-phase3-refinement/selected-default-verification.json`.
- Provenance: frozen comparison science SHA2568adcdf673fc787fb58629db6b77ac7471a334f16c778fde18e755d33666fd162 and exact source ZIP snapshot; current deployment2a18c9d18c8f9e27055a21303df11afafe720f8321c12ce9558ecd933db1a0f6. Source unchanged6d53d2e92fb3a452bdba32e13cadc8ae2b7521ffc7460a9913414ad2fdca6917; NumPy2.5.4/SciPy1.18.1, CPU only. No speedup or GPU kernel claim.
- Generated measured Markdown report via `scripts/build_refinement_report.py`; includes own-target reversal and Gaussian losses. Built/visually inspected270-step `fixed-vs-combined.gif`/PNG using `scripts/build_schedule_replay.py --runs runs/mskcc-phase3-refinement --fixed-name fixed --adaptive-name paced_robust --output runs/mskcc-phase3-refinement/fixed-vs-combined.gif`, exit0. Acquired images only, each panel holds its own past measurement, no truth reveal.
- Final `pip check`, CLI/refinement help, generated/raw ignore checks and `git diff --check` clean. README/BUILD_PHASES/model-controller notes updated. Repo remains untracked/no HEAD. No blocking refinement gate remains. Stop the bounded search here; Phase4 scientific CUDA Rust parity/timing next. Phase5 must freeze settings and evaluate independent s2/s3/multiple budgets; investigate appearance/motion weakness before claiming predictive quality. No biological protection or general adaptive superiority claimed.

## 2026-10-24 11:28 -04:00 — Phase4 native CUDA Rust renderer verified

- Read project contract/roadmap and reviewed current CPU renderer, prediction ensemble and pinned NVIDIA source. Recommended GPT6.1 Sol High for native numerical/memory/toolchain work; no model switch assumed. Re-ran official SAXPY:32 exact assertions, exit0. GPU RTX4070 Laptop8188MiB/sm89, driver581.57; WSL2 Ubuntu22.04, Linux CUDA13.3/nvcc13.3.73/tileiras13.3.36, Rust1.98.0, pinned NVIDIA fc747196f2d46dce41bd844e3f5b1c5882751f2b/cuTile0.5.0. Upstream tracked source clean.
- Added independent `crates/photon-gpu` package/toolchain/lock and real Rust cuTile Gaussian entry. Python packs past-state center/precision/amplitude descriptors only; no images/oracle/labels reach GPU. Native kernel accumulates anisotropic Gaussians over image grid; FP64 geometry and FP32 exp/value accumulation. Truncation radius4/final[0,1] clipping match CPU semantics. Conservative near-boundary flags trigger exact original CPU full-scene rendering, substituting only flagged voxels; counts/cost disclosed. Avoids point-vs-volume FP64 reduction-order ambiguity at a discontinuity.
- Checked binary batch ABI with version/header/payload/resource/precision/nonfinite checks, max64 scenes/10000 Gaussians per scene/axes4096/128M output voxels/128MiB input. Empty scenes execute zero-signal kernel; empty batch explicitly no kernel. Local request cleanup verifies workspace-owned path. GPU errors clear; auto fallback records CPU/reason, numerical response errors not silently swallowed. Explicit CPU remains default.
- Integrated optional `GaussianSceneModel.predict(...,backend='cuda-rust')`; one batch contains mean plus6 shifted states for3D uncertainty. Prediction tags/backend/native metadata preserve measured/predicted distinction. CPU Welford map/scalar uncertainty remain heuristic; controller fitting/features/budget decisions unchanged. The operation is actual prediction rendering, not a scalar policy decoration or a claim of improved Gaussian quality.
- Prototype pitfalls resolved: offline Cargo first chose uncached futures-macro0.3.34; copied upstream pinned lock then used locked cache. cuTile needs explicit scalar broadcasts/rank-compatible shapes; native error trait import required. Prototype GPU center0.8, rotated3D max error2.98e-8. First full-volume benchmark failed at gridY83968>65535 although small fixtures passed. Remapped logical output to[B,ceil(P/8192),8192]/[1,1,128] tiles, pixel block(y*64+z)*128; all grid limits satisfied. Added above-limit volume regression. Preserved failed/partial benchmark logs and did not merge them into final report.
- Built via `scripts/build_gpu.py --offline`, release profile. Final host compile/link wall76091.5513ms; compile cache not claimed cold. `.tools/photon-gpu/build.json` records exact revision/toolchain/source/manifest/lock/binary hashes. Matplotlib3.11.2 installed for standalone plotting; pinned actual contourpy1.4.0/cycler0.12.1/fonttools4.67.0/kiwisolver1.5.1/pyparsing3.3.3/dateutil3.0.0/six1.17.0/tzdata2026.5 dev dependencies. Editable package metadata refreshed; NumPy2.5.4/SciPy1.18.1 unchanged. PowerShell formatted harmless pip/native stderr as errors; installation metadata/imports and captured native return codes independently verified.
- Test progression: initial7 GPU-focused tests pass in20.33s; corrected-grid8 pass in25.98s; full78 pass in41.42s before grid regression;79 in49.58s after; final **80 passed in50.45s** after adversarial rotated cutoff tests/conservative repair. Tests cover empty/rotated/thin fields, non-tile lengths,10000 Gaussian input,7-state prediction uncertainty, malformed/resource-heavy inputs, explicit fallback and full-volume grid.100 random rotated Gaussians also tested in timed benchmark. Declared rtol2e-4/atol2e-5. High-amplitude near-cutoff fixtures require exact CPU reference inclusion, not a relaxed tolerance.
- `cargo fmt --check` and `cargo test --locked --offline` return0; one native input/resource unit passes. Captured through Python subprocess in `runs/phase4-rust-checks.json`/clean log to distinguish actual return0 from PowerShell native-stderr formatting. No developer-source patches to NVIDIA checkout.
- Final `scripts/benchmark_gpu.py --output runs/phase4-benchmark-verified`, exit0.5 CPU repetitions,5 warmed single-kernel graph CUDA-event intervals,3 separate single-render callers per case; fixed seed42, release build, validation jobs finished before timing, active laptop/no clock lock. CUDA events exclude transfer/compilation/context but include enqueue gaps. Synchronization/buffer lifetimes explicit. Production mode renders once; warm repetitions only in profiling mode. All raw samples/context/JIT/transfer/allocation/host/VRAM snapshots exported, not profiler-instruction or isolated PCIe bandwidth claims.
- Measured CPU/device/caller medians(ms): G1/B1,64²0.260200/0.045056/1857.918600; G100/B1,64²33.241900/0.214016/1984.296300; G10000/B1,64²3087.018400/19.818497/5291.007200; G100/B6,64²194.339700/1.199104/2127.439800; real observed s1t260 G17/B1,41x512x51285.679400/49.300480/5335.463800. Max pixel errors2.98e-8/1.49e-8/4.47e-8/1.49e-8/1.19e-7. CPU uses existing local bounding boxes; GPU dense-grid work count differs. Kernel-only ratios are not application speedups.
- Every full caller slower than CPU; retain CPU default, GPU optional research backend. First fresh namespace3 backend compiles (two fills+render), main JIT preparation1613.011631ms; later same-case callers0 backend compiles/3 disk hits, still pay AST/cache/context. All benchmark boundary repairs0; conservative repair overhead is tested on adversaries, not estimated from those timings. Native memory input/output byte counts and observed free-device bytes recorded; no exact peak memory fabricated. Persistent native context/transport optimization not implemented or promised as a measured fix.
- Final real `scripts/run_phase4_experiment.py --backend cuda-rust --output runs/phase4-real-gpu-verified`, exit0. Whole270-step s1 replay, B54/seed42/paced_robust; all withheld geometry saved causally. After closure, batch render1/134/268; CPU max pixel differences1.7881393432617188e-7/1.1920928955078125e-7/1.1920928955078125e-7. Source errors evaluated only after closure; no annotations opened. Exact54 acquisitions/decisions/state match the earlier CPU experiment.
- Deliberately missing PHOTON_GPU_BINARY, same experiment `--backend auto --output runs/phase4-real-cpu-fallback-verified`, exit0: actual CPU, explicit missing-binary reason/no kernel, zero pixel differences; same54 captures/decisions/state. Backend is recorded honestly in JSON/NPZ. CPU reference/fallback run the same actual data; no future frames leaked to controller or native kernel.
- `scripts/verify_phase4.py` exit0 independently checks5-case median/ratio accounting, single-render mode, hashes, real prediction tags/history/shape/finite bounds, CPU scene rerenders, source-frame MSE recomputation, exact GPU/fallback trajectories and current code. `runs/phase4-verification.json` reports all caller speedups below1. Chart initially clipped labels from automatic tight layout; regenerated directly from unchanged JSON with explicit margins using `plot_gpu_benchmark.py`, visually rechecked. No timing values changed.
- Science SHA2560427bc5620e65b1e37bf87b98ccd81e6b00b396d5f770ad4f8e1d1c8d25a7fff; binary2f0ee563a2bd0b76d2638e4f7f1f58506579ba1a05eea4200a77b197908e833f; Rust source80369c56f763a0f57bbff3a55878b0b446db7b751f76f4e21b60f6a2e1480bd0; source microscopy hash unchanged6d53d2e92fb3a452bdba32e13cadc8ae2b7521ffc7460a9913414ad2fdca6917. References and contract in `docs/cuda-rust-kernel.md`; README/BUILD_PHASES updated with measurements, limitations and reproduction commands.
- Decision: Phase4 correctness/integration/demo gates pass. Latency limitation is explicitly measured, not hidden or labeled a speedup. Do not switch deployment to GPU by default. No reconstruction-quality, optimal-sampling, phototoxicity or held-out gain claimed. Phase5 independent embryos/multiple budgets and fixed/raw-hold comparisons next; Gaussian model's existing appearance/motion weakness remains. No Phase5 work done here.
- Final source archive: `runs/phase4-source-snapshot.zip` contains exact Python/Rust/scripts/manifests/locks/kernel notes, CRC verified; benchmark Python/Rust source hashes match. `pip check`, CLI help, ignore checks and `git diff --check` pass. No raw data/secrets in archive; no commits/publication, repository remains without tracked files/HEAD.
