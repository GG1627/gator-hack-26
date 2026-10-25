# Lower-budget probe results — 2026-10-25

The unchanged event-focus controller can retain most synthetic division coverage
with a lower budget, but complete coverage is not established at 32 images.
The pre-execution plan is [CONTROLLED_BUDGET_PROBE.md](CONTROLLED_BUDGET_PROBE.md).
No alternative budgets were tried or selected after inspecting this probe.

## Prospective results

Six new seeds, 301–306; each has four programmed divisions in the event-bearing
conditions and 240 source frames. Each condition compares 32-image adaptive,
32-image fixed and 40-image fixed schedules, all closed before scoring.

| Condition | Adaptive, 32 captures | Fixed, 32 captures | Fixed, 40 captures |
|---|---:|---:|---:|
| Visible precursors | 23/24 | 8/24 | 11/24 |
| Sudden divisions | 4/24 | 8/24 | 11/24 |
| Quiet specimen | Undefined | Undefined | Undefined |

For precursor runs, adaptive32 covers 95.8% of divisions using 20% fewer images
than fixed40, which covers 45.8%. This is an explicitly unequal-budget comparison,
supplemented by the equal-budget fixed32 result. It is a controlled synthetic
observation, not validation on real cells. All four events are covered in five
of the six precursor runs; seed301 covers three. Do not select only those five
successful seeds and claim universal coverage.

Development seeds 7/42 cover 7/8 events with adaptive32 versus 2/8 for either fixed
budget in the precursor condition; abrupt development results are 2/8 for all
three schedules. Quiet clips have no events and hence no defined coverage.
Sparse adaptive timing has a substantial cost when events have no precursor.

## Execution and independent verification

- Command: `.venv/Scripts/python.exe scripts/probe_controlled_budget.py --output runs/controlled-budget32-v1`
- Single-thread BLAS configuration as in the existing controlled benchmark.
- All 72 comparisons completed in 16.3 seconds internally; 120-second limit.
- Existing controller, generator, gap constraints and event tolerance unchanged.
- A separate saved-artifact checker regenerated all source clips, checked every
  source and pixel hash, independently calculated event distances/coverage,
  last-image MSE and maximum age, and verified all acquisition budgets/traces.
  All 72 rows passed in 12.8 seconds internally. It did not rerun policies.
- Portable evidence: [protocol](evidence/controlled-budget32-v1/protocol.json),
  [compressed original summary](evidence/controlled-budget32-v1/summary.json.gz),
  [source archive](evidence/controlled-budget32-v1/source.zip),
  [verification and totals](evidence/controlled-budget32-v1/verification.json).
  The archive includes the pre-execution plan and source files with matching
  registered hashes. Summary SHA-256:
  `d6f7d22ecf711b28c4c513dc79b429d568a2bf4573932f43b3a2b93377f2cf6c`.

## Decision

**Subsequent user-approved integration:** the measured32/40 comparison is now the
default frontend mode, alongside the original equal-budget comparison. Seed304
was selected after evaluation to illustrate a successful precursor case; all six
seeds and unfavorable cases remain available. See [LOWER_CAPTURE_DEMO.md](LOWER_CAPTURE_DEMO.md).
The original decision below describes the state before that authorization.

Keep the current 40-image, equal-budget demonstration and its measured 24/24
precursor cohort result. This probe is separate evidence for a possible future
lower-budget mode; it is not silently substituted into the demo's images or stats.
The existing policy spends its exact declared budget, so changing playback length
or adding stable time alone does not make it minimize image count.

Cell health is not inferred. At equal light per capture, count ratios provide a
relative exposure/dose estimate. They cannot yield a survival percentage without
an applicable, calibrated biological response model. Wäldchen et al. measured
strong differences with wavelength, labeling, cell line and environment:
[Light-induced cell damage in live-cell super-resolution microscopy](https://www.nature.com/articles/srep15348).
Its cultured-cell super-resolution conditions do not calibrate this synthetic
generator or the MSKCC embryo experiment. No published toxicity coefficients were
transferred into this demonstration.
