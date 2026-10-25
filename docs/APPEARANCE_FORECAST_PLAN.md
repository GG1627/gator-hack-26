# Registered appearance-preserving forecast probe

2026-10-24, before executing this estimator on source images.

Motivation: the original and watershed Gaussian forecasts both lost to raw hold
on six earlier development probes. Direct rendering discards measured texture and
unrepresented structures. Test a parameter-free alternative:

`prediction(t) = clip(last normalized acquired image + Gaussian(t) - Gaussian(last acquisition), 0, 1)`

This holds the unmodeled residual while applying only the model's predicted change.
It does not transport that residual, predict unseen divisions, or guarantee improved
accuracy. Clipping can alter mass; incorrect motion can cause ghosting. Position
uncertainty remains heuristic and is not calibrated for the corrected image.

Use the currently running detector-ablation's saved causal histories/geometries after
it closes. Do not refit or change any controller. Compare raw hold, direct Gaussian
forecast and appearance correction on explicit source targets133,135,194,196,261,263
for original adaptive and watershed schedules. If a target was acquired by either
schedule, report that exclusion explicitly; do not replace it based on errors.
Use only targets withheld by both for the direct cross-policy table. Save per-policy
eligible outcomes as well. This is previously inspected s1 development data.

Freeze source/plan hashes before evaluation, generate estimates before reading each
target image, and keep the same first-acquisition normalization. Score full-volume
MSE and MAE; report every result, including cases worse than raw hold. No adjustable
mixing weight or parameter sweep is permitted in this probe. A small selected panel
cannot establish overall superiority or acquisition benefit.

Controlled tests cover exact raw preservation under zero predicted change, a known
Gaussian translation with static residual texture, clipping, immutable outputs and
rejection of inconsistent acquisition/calibration provenance. The implementation is
isolated under `experiments/forecasting/`, outside the frozen PHOTON source inventory.
