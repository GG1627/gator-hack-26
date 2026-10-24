# Phase 3 refinement: measured development results

Exploratory selection on MSKCC s1 source frames 0..269 only. No s2/s3
evaluation was used. All methods acquired 54 complete volumes, including
frame zero. These results do not establish generalization or biological benefit.

Selected by the [fixed development protocol](phase3-refinement-plan.md): **paced_robust**.

The adoption rule requires more covered events than original and no higher
common-target raw hold-last MSE, then ranks coverage, raw-hold MSE and name.

## Schedule and retrospective event coverage

Coverage counts canonical binary divisions with a capture within +/-1 source
frame of the first daughter time. Simultaneous divisions count separately.
This is temporal observation coverage, not detection recall or alert precision.

| Variant | First-half captures | Max gap | Terminal age | Covered events | Coverage |
|---|---:|---:|---:|---:|---:|
| fixed | 27 | 6 | 0 | 334/568 | 58.80% |
| original | 43 | 12 | 12 | 192/568 | 33.80% |
| paced | 29 | 6 | 9 | 324/568 | 57.04% |
| robust | 34 | 12 | 12 | 285/568 | 50.18% |
| paced_robust | 29 | 6 | 9 | 325/568 | 57.22% |

## Reconstruction on identical withheld times

All five schedules share **110 withheld target times**. These
tables use exactly that intersection. Full3D voxel-weighted errors use the
first acquisition's frozen normalization and [0,1] clipping. Foreground is
evaluation-only normalized truth signal>0.1, shared by all estimators for
each target. Own-withheld results are also saved in JSON, but those sets differ.

Gaussian hold freezes the last fitted scene and isolates motion extrapolation.
Raw hold carries forward the last measured volume. Neither reads future truth.

### Whole-volume MSE

| Variant | Gaussian forecast | Gaussian hold | Raw hold-last |
|---|---:|---:|---:|
| fixed | 0.009467520863 | 0.009443385712 | 0.002593877199 |
| original | 0.009452064915 | 0.009426212105 | 0.003014881371 |
| paced | 0.009422620789 | 0.009407329803 | 0.002396484938 |
| robust | 0.009421949742 | 0.009406660195 | 0.002772709804 |
| paced_robust | 0.009422673762 | 0.009407540063 | 0.002396866696 |

### Foreground MSE

| Variant | Gaussian forecast | Gaussian hold | Raw hold-last |
|---|---:|---:|---:|
| fixed | 0.08471851728 | 0.08456221985 | 0.01705148542 |
| original | 0.08469411704 | 0.08453600628 | 0.02117596603 |
| paced | 0.0844124173 | 0.08431649862 | 0.01542165896 |
| robust | 0.08443211665 | 0.08433033858 | 0.01904956442 |
| paced_robust | 0.0844107383 | 0.08431577874 | 0.01542344138 |

### Each method's own withheld targets

All methods withhold216 frames, but the timestamps differ. These scores
complement the matched-target comparison and can rank methods differently.

| Variant | Gaussian forecast MSE | Gaussian hold MSE | Raw hold-last MSE |
|---|---:|---:|---:|
| fixed | 0.007130691037 | 0.007108824831 | 0.002112048452 |
| original | 0.008089653211 | 0.008057661392 | 0.002712791183 |
| paced | 0.007352533331 | 0.007328703508 | 0.002163335414 |
| robust | 0.007892338758 | 0.007870303368 | 0.002480179557 |
| paced_robust | 0.007352836292 | 0.007328044982 | 0.002163087428 |

## Interpretation and limits

Only the declared variants were evaluated; no post-score parameter search was
performed. The original run and all losing variants are preserved. A selected
variant can still lose to fixed sampling or raw hold-last; read all tables.

In this run fixed sampling covers more events and has lower own-withheld raw
MSE than the selected variant. The selected variant has lower common-target raw
MSE. There is no overall superiority claim over fixed sampling. Most coverage
gain over original comes from pacing; robust aggregation adds one covered event
over pacing-only here. Gaussian forecasts lose strongly to raw hold-last, and
their motion extrapolation also loses slightly to holding the fitted scene.

Event counts are clustered within one embryo and are not independent biological
replicates. Reconstruction includes camera noise and simplified-Gaussian appearance
bias. The shared withheld set is schedule-dependent, and the first-acquisition
normalization is not a photon-count calibration. Future Phase5 must evaluate frozen
settings on independent s2/s3 windows and multiple budgets before broad claims.

Forecast geometry was saved during causal replay. All five oracles closed before
truth or lineage labels were read for scoring. Offline rendering uses only saved
geometry, fixed normalization and public volume shape; truth never updates it.

Artifacts: `runs/mskcc-phase3-refinement/` contains protocol, configs, decision
traces, forecast/held-scene archives, final states, per-frame errors and summary.
`source-snapshot.zip` preserves the exact comparison implementation. Metric
accounting/source-probe evidence is in `verification.json` when checks complete.

Comparison science SHA256: `8adcdf673fc787fb58629db6b77ac7471a334f16c778fde18e755d33666fd162`.
Source SHA256: `6d53d2e92fb3a452bdba32e13cadc8ae2b7521ffc7460a9913414ad2fdca6917`.
