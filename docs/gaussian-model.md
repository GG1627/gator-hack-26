# Phase 2: causal Gaussian observation model

This CPU model is a simplified intensity representation, not a reproduction of
CellSplat4D, a PSF model, or a validated biological tracker. It accepts acquired
`ObservedFrame` objects only. It has no sequence, file path, oracle, or annotation
input. Source loading remains in the trusted runner; target scoring occurs only
after the oracle closes the complete replay.

## Observed pixels to Gaussians

Arrays use YX or ZYX axes. MSKCC metadata XYZ spacing is reversed to ZYX
(0.75, 0.15, 0.15 micrometers). Centers/covariances use voxel units; assignment
distances and scalar position uncertainty use micrometers. Time uses source-frame
indices (75 seconds per frame on MSKCC), including gaps between acquisitions.

The first acquisition fixes background to its median and scale to its 99.99th
percentile minus background. A negligible scale becomes 1. Signal is positive
background-subtracted intensity divided by scale. Noise is 1.4826 times the
median absolute deviation divided by scale. Future acquisitions never recalibrate
this transform. Fits use unclipped positive signal; rendering, previews and scores
use the same [0,1] clipping. This is a signal-error space, not raw photon counts.

Detection smooths with a Gaussian of 0.15 micrometer sigma and uses
face-connected components above max(0.08, four times first-acquisition noise).
Default accepted size is 24 through 1,000,000 voxels; more than 2,048 accepted
components fails explicitly. Detection reports rejected counts. These are bright
component candidates, not established cell or nucleus counts.

For each mask, weights are original positive observed signal. Weighted moments
give center and covariance. Covariance eigenvalues are floored at 0.25 squared
voxels for positive definiteness. Amplitude is least squares against the Gaussian
basis on that mask. Thresholding truncates tails and can underestimate size;
touching objects can merge and diffuse objects can be missed.

Rendering adds A exp(-0.5 (x-c)^T covariance^-1 (x-c)) in local bounding boxes,
truncates at Mahalanobis radius 4, then clips the final sum to [0,1]. Background
is zero in normalized signal space. There is no alpha compositing, learned
appearance, PSF correction or physical camera-noise likelihood. Output is float32.

## Association, prediction and uncertainty

Physical-distance Hungarian assignment uses a 5 micrometer gate and explicit
dummy unmatched columns. Velocity updates use actual acquisition-index gaps and
0.7 smoothing weight. Prediction integrates exponentially damped velocity
(rate 0.03 per source frame); zero damping gives constant velocity. Shape and
intensity hold at their last observed estimates. They are updated on acquisition,
not extrapolated using an unvalidated growth model.

An observed two-component proximity/mass heuristic can retire a mother and create
two new child IDs with parent hints. It is labeled `candidate_split`, never
verified mitosis. Unmatched detections receive fresh IDs; unmatched tracks retire.
Prior snapshots remain immutable. No future divisions or unseen births are
predicted between acquisitions. Sparse tracking errors are expected.

Position uncertainty is sqrt(base_sigma^2 + (gap * 0.08)^2) micrometers. The base
is 0.15 plus an observed association-event fraction contribution, with an extra
0.5 for an empty scene. Thus it cannot shrink between acquisitions. This is a
heuristic displacement scale, not a calibrated posterior or error bound.

Optional image disagreement is pixel standard deviation across deterministic
positive/negative physical-axis translations of the whole scene. The six members
in 3D express correlated motion uncertainty, not independent object motion or
shape uncertainty. Pixel disagreement need not grow monotonically and can be zero
for an empty scene despite positive scalar uncertainty. It cannot account for
unmodeled background, unseen objects or nuclear texture. Display gain is 5 only
for that preview panel and is labeled.

## Causal evaluation and actual development result

The predeclared preview acquires source frames 0, 5, 10, predicts withheld frame
12, then closes the 270-step replay before reading truth. The evaluator checks
that prediction history equals actual acquisitions before the target and that
normalization equals the first acquisition's calibration. Labels are never read.
The image panel is a maximum-intensity projection; metrics use all 41x512x512
voxels. No forecast settings were changed to improve the revealed target.

Whole-volume normalized MSE is **0.0011492511713106393**, versus
**0.0010383232654541978** for holding the last measured image. Forecast MAE is
0.016446842166130262. The evaluation-only common ROI is the union of prediction,
truth and held image above 0.1, containing 465,551 voxels. Its MSE is
**0.012568739149017037**, versus **0.010504868602816072** for hold-last.
The forecast loses on both comparisons. The inspected preview shows lost nuclear
texture and diffuse signal; this likely contributes, but fitting and motion errors
have not been separately ablated. There is no adaptive-policy or event-coverage
result here and no demonstrated biological benefit.

Artifacts: `runs/mskcc-phase2/` contains configuration, state, trace, metrics,
predicted volume/disagreement, separate evaluation truth, and `comparison.png`.
`scripts/verify_prediction_demo.py` independently recomputes metrics from those
arrays and source TIFFs. This is development evidence, not a held-out benchmark.
Full s2/s3 evaluation and policy comparisons remain Phase 5.

## Verification and architectural boundary

Synthetic full-mask fitting recovers center/covariance/amplitude with 2e-4
tolerances; thresholded covariance uses 1.5% tolerance for tail truncation. An
independent rotated-Gaussian formula checks rendering (rtol 2e-6, atol 1e-7).
Tests cover dark/thin/boundary objects, invalid numerical inputs, physical-axis
gates, split/birth identities, held state, source-gap velocities and uncertainty.
Perturbing every unacquired frame leaves predictions/disagreement bit-identical
while changing post-hoc errors. A read spy verifies that predicting reads only
acquisitions and that early evaluation fails before reading truth. A controlled
translation forecast beats hold-last; that synthetic success is separate from the
real failure above. Python API isolation is not a hostile-code security sandbox.

Implementation: `photon/gaussian.py`, `tracking.py`, `schemas.py`, `oracle.py`;
runner: `scripts/run_prediction_demo.py`. SciPy 1.18.1 is the only new application
dependency. Official algorithm interfaces:
[connected components](https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.label.html),
[Gaussian smoothing](https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.gaussian_filter.html),
[linear assignment](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html).

Next: a budget-safe causal controller may use observed motion, split candidates,
gap and heuristic uncertainty, but must not present these as calibrated event
probabilities. Before claiming forecasting value, compare fitting-only and motion
ablations and evaluate frozen settings on independent embryos. GPU work remains
Phase 4; no GPU acceleration is claimed for this CPU model.
