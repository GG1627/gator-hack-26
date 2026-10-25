# Glimpse implementation target — E / Contact

The user selected E on 2026-10-24. Source: `round-2/e-contact.png`.

## Design system

Near-white chalk `#f7f6f1`, charcoal `#252a29`, secondary text `#636762`, oxide `#b04c3c`, thin warm-gray rules `#cacdc7`. Mineral blue/teal and a restrained warm depth accent belong to the data viewer. Locally bundled Manrope variable sans, light large heading, regular 14–16px controls/body, compact tabular instruments. No generated specimen image is used in the application.

Composition: compact wordmark/tagline header; editorial introduction explaining light cost with a clearly labeled conceptual acquisition diagram and an experiment anchor; equal-budget experiment heading; panoramic viewer with Spatial/Gaussians/Microscope modes; acquired-image inset; shared transport; aligned photographic acquisition strips; recorded decision/evidence reveal; collapsed experiment settings and research provenance. Preserve the existing metrics and evaluation interfaces beneath explicit reveal. Mobile stacks content and retains touch/keyboard controls.

The authorized opening-page follow-up uses code-native SVG, not generated scientific
imagery. It does not plot a measured trajectory or calibrated confidence interval.
Browser checks and inspected screenshots are recorded in BUILD_PHASES.md; captures
are `.tools/glimpse-opening-desktop.png` and `.tools/glimpse-opening-mobile.png`.

## Data and rendering contract

### Animated hero follow-up

The user requested an attention-grabbing opening with explicit problem/approach copy
and motion inspired by React Bits / award-style websites. The implementation uses
the existing Three.js dependency. The first billboard-particle scene was rejected
by the user as flat/basic and replaced with a sculptural scene: 26 actual deformed
3D nuclei, instanced surface granules, a transmissive outer membrane, image-based
studio lighting, directional/rim lights, an illuminated moving slice, restrained
bloom and tone mapping. During Estimate the nuclei separate into an expanded wire
model, then reform. The geometry is original illustration, visibly labeled conceptual,
and never feeds the scientific replay.

The hero headline is “See life. Spend light wisely.” The sentence beneath explicitly
states that repeated imaging can harm cells and Glimpse decides when to capture/wait.
Two editorial sections explain the problem and tested approach without claiming a
demonstrated biological or scheduling benefit. Observe/Estimate/Decide controls support
manual selection; auto progression can be paused. Drag and arrow keys rotate the
specimen, and Home resets user rotation. Reduced-motion preference stops
automatic animation and retains manual stages. Rendering suspends offscreen and when
the page is hidden. A static illustration replaces the canvas if WebGL is unavailable
or the context is lost; GPU resources are disposed on unmount.

References inspected: [React Bits Particles](https://reactbits.dev/backgrounds/particles)
and [Light Rays](https://reactbits.dev/backgrounds/light-rays). These informed motion
direction; no React Bits source or new animation dependency was copied/installed.
The existing E/Contact identity remains the visual reference. The attempted Awwwards
Isomorphic Labs page was unavailable; it was not treated as inspected.

Build and7 Node tests pass. Chromium checks cover pause/resume, manual stages,
automatic progression, offscreen suspension, dynamic reduced-motion preference,
context-loss fallback, drag/keyboard changes to rendered pixels, no browser errors
and no horizontal overflow at1440,1366,1024,
768,390,320px. Existing replay/evidence/budget interactions also pass. Captures:
`.tools/glimpse-hero-motion-desktop.png`, `.tools/glimpse-hero-motion-mobile.png`.
Close-up captures: `.tools/glimpse-hero-sculpture.png` and
`.tools/glimpse-hero-sculpture-model.png`. Initial overexposure was corrected after
visual inspection; the glass depth-write setting was corrected so the wire model
remains visible through the membrane. These are display fixes, not scientific changes.
After user approval, the final choreography was tied to the stage: Observe sweeps
the light sheet through the specimen, Estimate turns acquisition illumination off,
and Decide emits one brief pulse. Paused/reduced-motion views retain a readable
static stage. This illustrative timing is not a recorded controller decision.
Production build and the motion/interaction/six-width browser check passed again.
Formal unfamiliar-viewer comprehension remains an open Phase6 gate.

### Scientific display contract

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
# Controlled lab extension

The controlled replay is now the main demo. Reaching its last frame opens a large
sage completion panel with run-specific coverage, image count, exposure proxy and
final synthetic specimen state. The panel uses the existing typography and grid,
supports reduced motion, and auto-scrolls once per completion. Replay clears results;
changing the scenario retains accurate losing/undefined outcomes. Six-seed evidence
and the real microscopy study are secondary disclosures. Build and end-to-end
completion checks pass at five widths; completion screenshots inspected.

The event-focus branch adds a separate synthetic comparison before the real-data
viewer. It preserves the Contact visual direction and the approved sculptural hero.
Two microscope panels hold their most recent actual synthetic acquisitions on a
shared clock. Capture indicators, frame age and paired timelines explain the
controller's bursts. An optional native CUDA Rust Gaussian-fit view is explicitly
labeled; it never claims future split prediction. Seed, fixed phase and sudden/quiet
controls keep the favorable result inspectable. Evaluation assets load only after
Reveal results; full-run scores are labeled separately from the current replay time.

Verified production build, seven existing Node tests, Chromium interaction and
gated-fetch checks, five viewport widths (320–1440), original real-data replay
regressions, and inspected `.tools/glimpse-controlled-{desktop,mobile}.png`.
No runtime dependencies added. See `docs/CONTROLLED_EVENT_FOCUS.md` for evidence.
