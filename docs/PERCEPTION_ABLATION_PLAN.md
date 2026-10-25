# Registered development acquisition ablation

Date: 2026-10-24. Register before executing the new controller on source volumes.

## Question and scope

Does the implemented watershed detector improve actual acquisition choices when
substituted into the existing paced_robust controller? Prior fitting/forecast probes
improved the Gaussian model but remained worse than raw hold. This experiment tests
the downstream decisions, not just the appearance of a fitted image.

Use only MSKCC-CONFOCAL s1, frames0–269, budget54 complete volumes, seed42. This is
exploratory development on previously inspected data. It is not independent validation.
Do not inspect or tune on s2/s3. The separate frozen Phase5 run is untouched.

## Three variants

1. `fixed`: existing endpoint-inclusive fixed schedule and original Gaussian fitter.
2. `adaptive`: existing `paced_robust` controller and original Gaussian fitter.
3. `watershed`: identical controller/tracker settings, replacing only the fitter with
   the registered intensity-watershed detector. Seed smoothing0.3um, rectangular peak
   radius1.5um, original threshold/size/calibration settings. No parameter search.

The candidate uses private module instances so the canonical tracker/controller and
frozen source files remain unchanged. Detector outputs affect the controller's usual
motion, morphology and split features. Gaussian rendered disagreement still does not
enter the controller score. Use CPU with numerical-library thread counts limited to
one and a lower process priority on Windows to coexist with the Phase5 evaluator.

## Causal execution and preservation

Freeze the protocol, source hashes and source ZIP before acquisition. Use the existing
trusted ReplayOracle and record_development_run path for each variant. A policy gets
only public metadata, time and past acquired observations. Save all causal forecast
geometry and traces. Every run must close at the exact budget before any target/label
scoring. Require the original adaptive trace to reproduce the saved deployed s1 run.
Do not overwrite existing experiments. Record runtime status separately from outcomes.

Full Phase5 registration must pass before and after the experiment. Its background
process is not stopped, restarted or used for this experiment. The science aggregate
hash includes the complete module inventory, so all additions stay outside that set.

## Outcomes to report, including losses

- Exact capture counts, gap distribution and terminal age. Exposure proxy54/270 for
  all variants; no biological phototoxicity measurement or unequal-budget savings claim.
- Retrospective annotated division coverage within ±1 source frame, using the canonical
  MaMuT temporal graph only after closure. This is capture timing, not event detection.
- Full-volume normalized MSE/MAE for raw hold, Gaussian hold and Gaussian forecast.
  Retain own-withheld targets, three-way-common targets and every pairwise-common set.
  Publish target indices/counts and scalar sums. State that matched sets depend on the
  compared schedules and cannot establish overall superiority by themselves.
- All first-pass per-frame rows, source hashes, dependency versions and failure states.
  Validate scalar accounting and reload the saved geometry/ledger. Independent full
  rerender verification can be a later stage, clearly distinguished from this first pass.

The candidate earns further investigation if event coverage improves over the original
adaptive controller without worsening pairwise-common raw-hold MSE against it. Always
report the stronger fixed comparator as well. A result on this one development sequence
does not authorize a generalization claim or automatic promotion into the frozen run.

## Commands

```powershell
$env:PYTHONPATH = "$PWD/.tools/perception-deps"
$env:OMP_NUM_THREADS = '1'
$env:OPENBLAS_NUM_THREADS = '1'
.venv/Scripts/python.exe -m pytest tests/test_perception_ablation.py -q -p no:cacheprovider
.venv/Scripts/python.exe -u scripts/run_perception_ablation.py --output runs/perception-controller-ablation
```

Do not invoke a second instance against a live or existing output directory.
