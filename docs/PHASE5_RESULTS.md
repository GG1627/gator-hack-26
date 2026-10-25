# Phase 5 reviewed results — 2026-10-25

The registered real-microscopy benchmark is complete and verified. The standalone
runner finished all five stages at 00:47:23 EDT on October 25. A fresh
`.venv/Scripts/python.exe scripts/run_phase5.py verify` also exited successfully
during this review: all 36 run ledgers, target sets, event counts, aggregates and
exports verified. No acquisition or full-volume evaluation was restarted.

## What was evaluated

Two held-out MSKCC-CONFOCAL embryos (s2/s3), source frames 0–269, budgets
27/54/89, and six schedules per condition: fixed, frozen PHOTON `paced_robust`,
image-change, and random seeds 7/42/2026. All 36 runs use exact equal acquisition
counts within each condition. Events use the registered ±1-frame tolerance.

`runs/phase5/verification.json` passes scalar/ledger accounting;
`recomputation.json` records exact full-source recomputation for all six groups
and 36 runs; each group also records exact per-frame recomputation.
`report-verification.json` confirms all fields of the 36 generated report cards
match `benchmark.json`. These report cards are separate from the browser export.

## Results and interpretation

| Embryo | Captures / 270 | Fixed covered divisions | PHOTON covered divisions | PHOTON raw-hold MSE reduction on shared withheld targets |
|---|---:|---:|---:|---:|
| s2 | 27 | 176/560 | 140/560 | 1.44% |
| s2 | 54 | 352/560 | 325/560 | 5.32% |
| s2 | 89 | 557/560 | 544/560 | 6.82% |
| s3 | 27 | 150/567 | 131/567 | -0.41% (worse) |
| s3 | 54 | 348/567 | 332/567 | 6.71% |
| s3 | 89 | 558/567 | 546/567 | 9.22% |

MSE reductions are `100 * (1 - PHOTON MSE / fixed MSE)`, using each pair's common
withheld frames and the raw last-acquired image estimator. They measure the
schedules with that estimator, not the accuracy of Gaussian reconstruction.
The target set depends on both schedules. Fixed has lower own-withheld raw-hold
MSE in all six conditions, so there is no general image-quality superiority claim.
Fixed also covers more annotated divisions in every condition. Coverage measures
whether observations occur near labeled divisions; it is not event-detector recall.

Gaussian forecast own-withheld MSE is worse than raw hold in all 36 runs.
The Gaussian representation/kernel is functional, but this experiment does not
establish a reconstruction advantage. Only two independent embryos were evaluated;
random seeds are repeated schedules, not additional biological replicates.
Acquisition count is an exposure proxy. Cell health and phototoxicity were not measured.

## Failure review

The generated comparison chart and s2/B54 win/loss panels were visually reviewed.
At t179, PHOTON holds t178 versus fixed t177 and has lower full-volume raw-hold
MSE (difference -0.00124603). At t259, PHOTON holds t254 versus fixed t258 and
loses (difference +0.00207218). Gaussian panels show substantial missing or broad
structure. These selected examples illustrate observed errors, not causal proof
of their mechanism or independent validation. The earlier event audit also shows
fixed's t101 observation covering divisions at t100 that PHOTON's t97/t102 miss.

All 12 post-hoc panels and their selection/source metadata remain under
`runs/phase5/cases/`. Panels are maximum-intensity projections; scores use full
3D volumes. `runs/phase5/report.md`, `comparison.png`, `comparison.svg`,
`benchmark.json`, and the verification records remain local ignored artifacts.
The frozen report's statement that Phase 6 has not started is historical boilerplate;
the current UI status is in BUILD_PHASES.md. Frozen scripts were not edited.

## What to use and what remains

Keep the approved controlled synthetic replay as the main demonstration. Phase 5
adds independently recomputed real-data evidence, a useful conditional image-error
result, and explicit limitations. It evaluates the older frozen controller, not
the newer morphology-triggered controller used in the controlled demonstration.
Synthetic wins do not establish gains on these real embryos.

The real-data browser archive still uses the earlier partial snapshot:
`apps/web/public/demo/manifest.json` has `status: partial` and
`phase5_complete: false`. Its exporter is tied to the paused checkpoint and must
be updated and tested before publishing complete results there. This review did
not regenerate assets or relabel the old export as complete.

Phase 6 still needs the unfamiliar-viewer ten-second comprehension check.
Phase 7 needs final reproducibility/setup review, evidence/credits, backup demo
and submission preparation. No further long benchmark is needed for these tasks.
