# Glimpse implementation target — E / Contact

The user selected E on 2026-10-24. Source: `round-2/e-contact.png`.

## Design system

Near-white chalk `#f7f6f1`, charcoal `#252a29`, secondary text `#636762`, oxide `#b04c3c`, thin warm-gray rules `#cacdc7`. Mineral blue/teal and a restrained warm depth accent belong to the data viewer. Locally bundled Manrope variable sans, light large heading, regular 14–16px controls/body, compact tabular instruments. No generated specimen image is used in the application.

Composition: compact wordmark/tagline header; two-line heading and short explanation; panoramic viewer with Spatial/Gaussians/Microscope modes; acquired-image inset; shared transport; aligned photographic acquisition strips; recorded decision/evidence reveal; collapsed experiment settings and research provenance. Preserve the existing metrics and evaluation interfaces beneath explicit reveal. Mobile stacks content and retains touch/keyboard controls.

## Data and rendering contract

- The scientific package, frozen evaluation protocol and original run artifacts remain untouched. Display exports live under ignored `apps/web/public/demo/spatial/`.
- Export actual saved observed Gaussian fits and causal forecasts, including full covariance. Transform voxel ZYX coordinates and covariance into physical XYZ micrometers. Browser coordinates use a documented rigid axis permutation; shape/aspect ratios are preserved.
- Spatial mode uses a deterministic bounded sample of acquired source voxels. Document threshold, grid sampling, signal quantization and any point cap; this is an observation-derived display, not segmentation or a quantitative reconstruction.
- Gaussian mode may display projected Gaussian splats and 2-sigma ellipsoid geometry. The orthographic splat display is a visual inspection of the saved model; it is not the frozen CPU full-volume renderer used for reported scores. Retain the exact exported CPU-rendered projection for inspection/evaluation and state that distinction.
- Source-derived voxels always use the selected policy's last acquisition at or before the replay time. A Gaussian fit is labeled model fit; a causal forecast is labeled model forecast. No true future shape, annotation or image enters either pre-reveal view.
- Contact strips place acquisitions on a common source clock, only expose thumbnails already acquired, and never imply different total budgets. Keep distinct skipped/future/estimated states, and expose annotated events only in evaluation mode.
- Native WebGL rendering is display work, not a new CUDA benchmark or an application-speedup claim. GPU-unavailable and missing-spatial-export states retain the authentic microscope projection.

## Practical fidelity constraints

The mockup depicts an illustrative dense specimen. Actual source data determines the number, size, position and appearance of displayed components. Measured images, scalar metrics and uncertainty are never changed to match the concept. The source-image toggle must agree with inset visibility. Scale and camera controls must be meaningful; no mockup scale-bar value is copied without physical calculation. Scientific caveats and pending metrics remain accessible. Human comprehension testing remains an open Phase 6 gate.

## Implemented and verified — 2026-10-24

Accepted concept `round-2/e-contact.png` and final Playwright desktop/mobile captures were inspected with `view_image`. Chromium viewports: 1440×1000, 1366×768 and 390×844. Browser plugin was unavailable, so the official Playwright CLI provided screenshots, DOM interaction checks and console inspection.

Fidelity comparison:

| Comparison | Result / intentional adaptation |
|---|---|
| Wordmark, navigation and opening copy | Glimpse, “Know when to look.” and “A glimpse. Then a decision.” preserved. Explanation uses “image” for newcomers; implementation acquires complete volumes. |
| Typography and palette | Locally bundled Manrope, light large heading, chalk/charcoal, oxide actions and mineral model colors match the selected direction. |
| Panoramic viewer and inset | Three modes, acquired-image toggle and authentic image inset implemented; full physical covariance controls projected splats and shaded 2-sigma contours. |
| Specimen density and framing | Actual saved geometry is sparser and more vertically elongated than the illustration. This is intentional; no fabricated cells or decorative source points are mixed into the model. Camera uses exact component bounds. |
| Contact strips and transport | Shared source clock, photographic acquired thumbnails, future empty bins, equal budgets and recorded reasons preserved. Moving-window caption and counts added for clarity. |
| Decision/evidence/settings | Compact rail and collapsed details preserved. Reveal/close evidence gates independent images and metrics. |
| Scale and responsiveness | Physical micrometer coordinates replace the mockup's uncomputed 10 μm bar. Laptop Play remains above the fold; mobile has six contact bins, 44px targets and no horizontal overflow. |

The implementation was faithfully verified against E's layout and identity, with the scientific-data adaptations above. Fixed issues included source-toggle pointer interception, over-conservative ellipsoid camera bounds, evidence navigation and small-screen contact targets. No material layout mismatch remains; the illustrative specimen cannot be reproduced honestly from this saved simplified model.

Validation actually executed:

- `npm test`: 7 passed. Production TypeScript/Vite build passed; lazy Three.js chunk emits Vite's advisory size warning.
- `pytest -q tests/phase6 -p no:cacheprovider --basetemp=.tools/glimpse-spatial-tests-final`: 9 passed in 29.18s. Includes all 1,620 scene frames, 546 spatial-export file hashes, sampled authentic voxel parity and frozen-source checks.
- Actual GPU shader versus independent analytic alpha values: three 129×129 cases, maximum error 1 alpha LSB (tolerance 2), including rotated covariance and thin anisotropy.
- Browser: all six conditions and comparison selectors; source toggle; keyboard rotation; reset/structure/fullscreen; Spatial/Microscope/Gaussian fit/forecast states; play/pause/scrub/contact selection; research navigation; evidence values versus source JSON; reveal/close; responsive sizes; no normal-flow console errors or failed responses. Evaluation JSON was not requested before reveal.
- Missing spatial export and deliberately unavailable WebGL both retain authentic microscope access; no unhandled fallback errors.
- Full 270-step 12fps 3D playback plus evidence reveal: 23.653s; final resource counts 5 geometries / 5 shader programs. This is a browser smoke measurement, not a scientific GPU benchmark.

Export and implementation did not resume Phase 5 or change frozen scientific paths. Formal unfamiliar-viewer comprehension and additional browsers remain unverified.
