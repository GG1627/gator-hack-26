# Peekaboo — After Hours

Selected by the user on 2026-10-25. This replaces L / Soft Focus. Implemented and browser-verified on 2026-10-25. Human comprehension/rehearsal and final reproducibility gates remain open.

## Identity

A quiet evening laboratory with a focused capybara scientist. Solid charcoal, warm yellow type, blue instruments and amber acquisition accents. Editorial animation-cel illustration gives the opening personality; the experiment gets spacious, precise controls.

- [Selected identity board](design-exploration/peekaboo-m-after-hours.png)
- [Opening / demo / results refinement](design-exploration/after-hours/screen-board.png)
- [Transparent mascot asset](../apps/web/public/peekaboo/after-hours-capybara.png)
- [Implementation plan](PEEKABOO_IMPLEMENTATION_PLAN.md)

The mascot is generated illustration, not microscopy evidence. The corrected asset places the eyepiece against the eye rather than the nose. It is one flattened transparent raster, not a rig or sprite sheet. Use it as a static hero with a brief entrance; do not promise independently moving eyes, head or paws. A future pose set is optional and not required for this build.

## Tokens and custom components

| Role | Starting value |
| --- | --- |
| Background | `#242629` |
| Raised surface | `#303338` |
| Image well | `#111315` |
| Main text | `#F5F0E5` |
| Secondary text | `#C2C3BD` |
| Heading / primary action | `#F6D48B` |
| Fixed schedule | `#97B8DA` |
| Peekaboo | `#D99B50` |
| Border | `#555A60` |

Use existing local Manrope Variable: headings 700–800, body 400–500, controls 600–700, tabular metric digits. Remove Newsreader from the active theme. Start hero at clamp(44px, 5.4vw, 80px), content titles 40–56px, body 18–20px, metadata at least 14px on desktop. Verify contrast in the rendered app.

Use 8px spacing rhythm, 48–64px desktop outer gutters, 24px on mobile. Primary buttons are butter with charcoal text, about 48px high and 10px radius. Secondary buttons are outlined. Focus rings must be obvious. Image wells have 12px corners and slim borders, without huge floating card shadows. Avoid pill labels above every headline.

Build one coherent family: SlideNavigation, ActionButton, SourceDisclosure, CaptureStatus, ExperimentSettings, PlaybackControls, ExposureTimeline and ResultSummary. Reuse functional existing components rather than introducing parallel controls. Blue always means fixed, amber always means Peekaboo. Captured/held also have text and filled/outlined marks so color is never the only signal. Reconstruction gets an explicit label, not another ambiguous color.

## Story composition

1. **Opening:** two-column hero. Left: “See more. Illuminate less.”, “A better moment to look.”, Start the story. Right: capybara and microscope, with restrained SideRays behind the illustration. Small Peekaboo / Story / Demo header; slim progress footer. No dashboard statistics here.
2. **Problem:** “Every observation has an exposure cost.” Large authentic dataset image on one side, simple exposure ticks on the other. One sentence and a source disclosure. Use local MSKCC image with provenance; do not substitute generated cells.
3. **Approach:** “Choose when to look.” Three spacious stages, Observe → Estimate → Decide; use simple cell shapes and acquisition ticks, explicitly conceptual. Reveal the decision with a small state transition, not a decorative animation loop.
4. **Representation:** “Turn observations into a compact model.” Actual acquired image beside its saved Gaussian representation. One concise sentence and CellSplat4D inspiration link; do not imply full paper reproduction.
5. **Computation:** “Render the model with CUDA Rust.” A readable CPU fitting/scheduling → native GPU Gaussian rendering → saved browser replay diagram. Reuse theme colors, small icons and sparse labels. Explain actual technology roles, not a terminal wall.
6. **Demo:** “Same specimen. Different timing.” Two large aligned image wells, labels above, captured/held metadata below. Shared clock and transport, followed by aligned exposure lanes. Experiment settings collapsed by default. No mascot or rays competing with captures. Display selected synthetic run near the heading.
7. **Results state:** “More divisions. Fewer captures.” only for the featured successful run; alternate outcomes need neutral or data-dependent headings. Three metrics: divisions captured, captures used, estimated imaging light. Show both method values, qualifier next to light estimate, Replay / Inspect evidence, and expandable cohort evidence. No automatic jump at completion.

On a 1366×768 presentation screen, opening and default demo should fit without clipped controls. On phones, stack panes in the same order with synchronized clock; allow natural vertical scrolling. Keep screenshots and text as separate HTML/assets, never install a whole generated mockup as the page.

## Motion and SideRays

Opening only. Following the user's full-viewport refinement, render the light in a fixed body portal starting at the top-right screen edge, outside the presentation max-width, gutters and slide clipping. Keep foreground content above it and omit the Research archive trigger from the opening header. Final user-requested refinement uses the supplied settings: speed 2.5, intensity 2, spread 2, density 5, glow 1, dust 0, followMouse true, mouseInfluence 0.5, opacity 1 and DPR cap 1.5. The real WebGL effect fills the viewport behind the transparent mascot without masks or content-container restrictions. Use warm gold and pale blue. Prefer the supplied standalone React component over installing an unnecessary UI framework.

Respect reduced motion dynamically and provide a motion toggle for continuous effects. Pause when slide inactive, tab hidden or illustration offscreen. Static fallback must look complete without WebGL2. Verify StrictMode cleanup, context recovery, resizing and render-loop termination. Do not add GradientASCII to this direction.

React Bits upstream [license](https://github.com/DavidHDev/react-bits/blob/main/LICENSE.md) was inspected: MIT plus Commons Clause. Retain its notice and upstream attribution with any vendored component. The adapted SideRays component is integrated and lifecycle-tested; its full notice is served at `/licenses/react-bits-SideRays.txt`. It is unrelated to native CUDA Rust science.

Capture feedback remains the primary demo animation: brief border pulse and scan/snapshot cue only on actual acquisition transitions. A held frame must not flash as a new capture after pause/resume or slide return. Reduced motion uses an immediate clear status change. Avoid bouncing the entire mascot or continuously moving image panes.

## Evidence and implementation boundary

Preserve all contracts and tests in the implementation plan. Generated screen imagery is layout reference only. Actual saved metrics and images override all generated labels, timing marks and cell renderings. No science changes, reruns, commit, push or deployment are part of this design handoff.

The presentation, replay, results and archive chrome now use this theme. Browser QA covered all six slides and results at 1440x900, 1366x768, 390px and 320px, plus replay/evidence state and motion lifecycle. See HANDOFF.md and BUILD_PHASES.md for executed checks and remaining human gates.
