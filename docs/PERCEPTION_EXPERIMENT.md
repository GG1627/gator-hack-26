# Development perception experiment

Latest follow-up: the registered full controller ablation is now running; see
[PERCEPTION_ABLATION_PLAN.md](PERCEPTION_ABLATION_PLAN.md), `docs/HANDOFF.md` and
`runs/perception-controller-ablation/status.json`. The original Phase5 run remains
separate. No new full-controller outcome is claimed before completion/verification.

Registered before running the candidate on source volumes, 2026-10-24.

The saved s1 detector discards a 1,762,951-voxel region at t260 because the upper
size bound is 1,000,000. That region contains 99.4784% of thresholded foreground.
The corresponding t193 region has 967,450 voxels and is fitted as one component.
The region audit reproduces saved region, accepted and rejected counts on all five
frames. This supports splitting connected intensity regions before fitting.

Candidate: marker-controlled watershed of negative smoothed observed intensity.
The foreground threshold, size limits, calibration and Gaussian fitting remain
the baseline values. Markers use 0.3um smoothing and a rectangular physical peak
neighborhood with 1.5um radius. Each retained connected component receives a marker
if neighboring brighter components suppressed its local maximum. Plateau maxima
collapse to one marker. No labels or future frames enter the algorithm.

Panel: s1 acquired frames 0,66,132,193,260. Selected during the preceding count audit,
so this is a development diagnostic, not an untouched validation set. Compare exact
baseline counts and full-volume in-sample MSE/MAE under the same calibration and
renderer, plus inspect projected measured/baseline/candidate images. Component count
agreement is not a selection objective or segmentation score. Single-run timing
alongside Phase5 is not a performance benchmark.

Controlled tests cover anisotropic touching peaks, splitting before upper-size
rejection, empty input, physical-spacing errors, plateau seeds and immutable input.
Optional scikit-image0.26.0/lazy-loader0.4 live in `.tools/perception-deps`; neither
the frozen environment nor its dependency declarations are changed.

Reproduce (PowerShell, from repository root):

```powershell
.venv/Scripts/python.exe -m pip install --target .tools/perception-deps --no-deps scikit-image==0.26.0 lazy-loader==0.4
$env:PYTHONPATH = "$PWD/.tools/perception-deps"
.venv/Scripts/python.exe -m pytest tests/test_experimental_perception.py -q -p no:cacheprovider
.venv/Scripts/python.exe scripts/compare_perception_panel.py
```

The implementation is isolated in `experiments/perception/watershed.py`; no current
policy imports it. Promotion requires spatial/manual segmentation checks, source
alignment resolution, causal forecast tests and development acquisition ablations.
Any later evaluation on inspected s2/s3 must be described as exploratory.

Method reference: [scikit-image watershed documentation](https://scikit-image.org/docs/stable/api/skimage.segmentation.html#skimage.segmentation.watershed).
Watershed is a classical baseline; it is not the project's frontier eligibility claim.

## Measured results

All five baseline diagnostic dictionaries exactly matched saved observations.
Candidate defaults were unchanged. Artifacts: `runs/perception-watershed-panel/summary.json`
and `frame-*.png`. The summary records image/code hashes, library versions and configuration.

| Acquired s1 frame | Baseline components | Candidate components | Baseline fitting MSE | Candidate fitting MSE |
|---|---:|---:|---:|---:|
| 0 | 7 | 7 | 0.00114664 | 0.00114664 |
| 66 | 28 | 37 | 0.00099646 | 0.00099027 |
| 132 | 87 | 130 | 0.00163259 | 0.00142277 |
| 193 | 42 | 306 | 0.00488703 | 0.00300433 |
| 260 | 17 | 263 | 0.02935190 | 0.00867538 |

The candidate retained all foreground voxels from components above the lower size
bound on this panel. This is foreground retention, not cell recall. At t260 it still
has far fewer components than the541 annotated spots. Inspected MIPs show recovery
of the bright specimen lost by the baseline, but remaining broad/merged structures.
Projections cannot validate3D instances. More components can lower in-sample residuals
without improving biological accuracy or forecasting.

Six candidate tests and four count-audit tests passed:10 total in1.51s on the final
run. Candidate single-run fitting times were roughly9.6–17.7s versus0.48–1.53s for the
baseline, concurrent with Phase5. These indicate practical cost, not a clean speed
benchmark. Optional dependencies were installed separately after network/read sandbox
permission was granted; the frozen venv was not upgraded.

Decision: retain the implemented candidate for causal forecast/acquisition ablations
and spatial/manual validation. Do not promote it into the frozen controller or present
the fitting-error reduction as forecast improvement, acquisition savings or reduced
phototoxicity. The result supports fixing perception before adding a foundation model.

## Registered causal forecast probes

Before executing candidate forecasts, choose three reset histories: [0,127,132],
[0,188,193], [0,254,260]. All contain actual saved s1 acquisitions. Predict at1 and3
source frames beyond the last acquisition. Each model uses the same original tracking
code/configuration and first-frame calibration; only its detector differs. Generate
forecasts before loading target images, and include the last raw acquired image as
a baseline. No annotations enter the model. Record all six outcomes, including losses.

This omits intermediate acquisitions and therefore does not reproduce saved full-run
states or establish acquisition gains. It is a bounded test of whether the perception
change can improve temporal prediction at all. `scripts/probe_perception_forecasts.py`
loads a private instance of the tracker module to inject the candidate detector;
the canonical module and frozen source remain unchanged. A targeted isolation test
checks this and verifies that the candidate still rejects predicted images as input.

### Forecast results

| Target | Horizon | Raw-hold MSE | Original Gaussian MSE | Watershed Gaussian MSE |
|---|---:|---:|---:|---:|
| 133 | 1 | 0.00159429 | 0.00199064 | 0.00193494 |
| 135 | 3 | 0.00185245 | 0.00223221 | 0.00220971 |
| 194 | 1 | 0.00224593 | 0.00502016 | 0.00350924 |
| 196 | 3 | 0.00299608 | 0.00522428 | 0.00456847 |
| 261 | 1 | 0.00336953 | 0.02968611 | 0.00907269 |
| 263 | 3 | 0.00439799 | 0.02990721 | 0.01015557 |

The candidate improves Gaussian forecast MSE in all six selected probes. Raw hold
has lower MSE in all six. The candidate improves MAE over the original Gaussian
forecast in three of six probes; these metrics do not always agree. This supports
retaining the perception change for further experiments, while acquired-image
appearance preservation and reliable motion remain unresolved.

Artifact: `runs/perception-forecast-probes/summary.json`. All11 targeted tests passed
after relocating the experiment. Reproduce with fresh output directories:

```powershell
$env:PYTHONPATH = "$PWD/.tools/perception-deps"
.venv/Scripts/python.exe scripts/compare_perception_panel.py --output runs/perception-panel-repeat
.venv/Scripts/python.exe scripts/probe_perception_forecasts.py --output runs/perception-probes-repeat
```

### Frozen-registration correction

The initial candidate file was added inside `services/science/photon/`. Checking only
the37 registered files missed the fact that Phase5 also hashes the complete module
inventory and aggregate science content. Before its next stage, the candidate was
moved to `experiments/perception/watershed.py`, with no numerical algorithm change.
The full `check_registration` function then passed: inventory, individual/aggregate
hashes, protocol and source archive. The live runner was never stopped or restarted.

Original experiment summaries remain unchanged. Their exact original source bytes
were reconstructed and verified against every recorded hash, then archived under
each result directory's `source/`; `source-relocation.json` maps the old locations.
Current scripts use the new location and refuse to overwrite completed summaries.
