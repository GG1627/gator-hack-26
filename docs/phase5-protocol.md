# PHOTON Phase 5 protocol v1

This protocol is specified before computing held-out outcomes. The executable
definition is `photon.benchmark.protocol_definition()`. `run_phase5.py freeze`
registers its exact JSON, source and runner hashes, Git state, validated input
fingerprints and a CRC-checked source snapshot. The registration is immutable;
every subsequent stage checks it. No adaptive parameters are selected from s2/s3.

Use s1 only for development. Evaluate s2 and s3 independently over the already
declared source frames 0..269, all 41x512x512 voxels, 75 seconds/volume. First
complete, decode and source-ZIP-CRC-check every declared volume. Out-of-window
samples such as frame399 do not enter the experiment. ZIP entry CRC verification
does not establish the full archive's publisher MD5.

Exactly 27, 54 or 89 whole volumes are captured, including frame0 (10%, 20%,
32.96%). All budgets are feasible for PHOTON/image-change min2/max12/terminal
age<=12. Freeze `paced_robust` and current image-change defaults. Fixed retains
endpoint-inclusive floor spacing; random retains uniform sampling without
replacement of B-1 indices from 1..269 plus frame0. Random seeds are 7,42,2026.
Deterministic policies run once per condition with seed42 recorded, not treated
as replicated random experiments. Comparisons equalize image counts; random
does not share adaptive gap constraints. Preserve that baseline and state the
constraint difference. No constrained-random superiority claim is supported.

The existing trusted runner saves immutable causal forecast geometry at every
skipped time and held-fit geometry at every acquired time. Policies receive only
public metadata and acquired observations. All 36 trajectories close before
opening labels or withheld pixels for scoring. Offline evaluation never calls
or updates a policy. Backend is CPU; the verified optional CUDA worker is outside
this experiment. Acquisition-stage elapsed times include fitting and I/O and
are descriptive, not controlled performance benchmarks.

Score three estimators at each withheld time: damped-motion Gaussian forecast,
last acquired Gaussian fit without motion, and last acquired raw volume. The
raw-hold baseline must remain visible even if Gaussian reconstructions lose.
Normalize with the shared first acquired volume only: subtract median, divide
by percentile99.99 minus median (existing constant-image fallback), clip
float32 signal to [0,1]. No per-future-frame normalization or label mask enters
the controller. Compute full-volume MAE/MSE using float64 error sums. Also score
foreground defined only offline by normalized truth>0.1, pooled by foreground
voxel count. This mask is not annotated segmentation. Empty masks yield null
foreground metrics. Do not use SSIM without a validated 3D window definition.

Retain own-withheld scores for every policy. The primary reconstruction
comparison is each fixed/PHOTON pair's exact intersection of withheld times;
also export each method's matched comparison to fixed and the all-method
intersection. Intersections depend on schedules and exclude acquired times;
they cannot establish uniform error reduction on all possible targets. Own
withheld comparisons have different target sets. Report both; never hide a
ranking reversal. All 270 source times are traversed for offline scoring.

The other primary objective is retrospective annotated event coverage: capture
within +/-1 source frame of a canonical MaMuT first-daughter frame. Simultaneous
divisions count separately; missing annotations give null plus reason, incomplete
graphs fail. This is observation coverage, not a validated event detector's
recall. Spatial tracking scores remain deferred. No precision/recall is claimed
for morphology hints. For failure analysis, export fixed-only, PHOTON-only and
both-missed event identities, largest matched raw-hold errors, and uncorroborated
heuristic-interest>=0.5 source times. The latter is descriptive, not validated
classifier false-positive measurement.

Retain every embryo/budget/method/seed result. Random mean/min/max are descriptive;
seeds are not independent biological samples. There are only two held-out embryos,
so no significance or broad biological generalization claim is predeclared.
Report improvements and losses separately for both primary objectives. There is
no selection rule, adoption step, test-data tuning, optional stopping on results,
or exclusion of unfavorable conditions. The dev refinement already satisfied
the development investigation requirement; do not reopen it based on s2/s3.

After full verification, `inspect_phase5_failures.py` may generate a distinctly
labeled post-hoc MIP panel for the largest signed raw-hold loss and win in each
condition. Omit a direction when it has no such case. Selection is descriptive
failure analysis, never a fresh test or a controller input; scores remain 3D.

Export one trusted `benchmark.json`, per-run config/decisions/state/causal scene
archives/timeline/metrics/per-frame error sums, group summaries, immutable closure
hashes and standalone chart/report. Scalar verification checks exact counts,
target sets, event arithmetic and exports. Full `evaluate --recompute` rereads
source volumes and rerenders saved geometry, requiring exact per-frame and final
metrics without executing policies. Tests additionally cover acquisition-only
reads, future perturbation, closure ordering, absent annotations, invalid budgets,
ledger tampering, controlled errors, seed determinism and reproduction.

Phase 6 has not begun. The generated card data/report must match trusted JSON;
there is no frontend to verify yet. Exposure reduction versus imaging every
volume is a capture-count proxy, not measured dose reduction or phototoxicity.

Reproduction from the existing environment:

```powershell
.venv/Scripts/python.exe scripts/run_phase5.py validate-data
.venv/Scripts/python.exe scripts/run_phase5.py freeze
.venv/Scripts/python.exe -u scripts/run_phase5.py acquire
.venv/Scripts/python.exe -u scripts/run_phase5.py evaluate
.venv/Scripts/python.exe scripts/run_phase5.py verify
.venv/Scripts/python.exe -u scripts/run_phase5.py evaluate --recompute
.venv/Scripts/python.exe scripts/report_phase5.py
.venv/Scripts/python.exe scripts/inspect_phase5_failures.py
```
