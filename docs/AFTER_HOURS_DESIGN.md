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
2. **Problem:** "How do you watch living cells without disrupting them?" Authentic MSKCC image with a short C. elegans caption; explicit frequent-capture exposure cost and sparse-capture missed-event risk. Conceptual two-lane timing illustration highlights a brief division. End with "When is another picture worth taking?" Keep technical image provenance and biological qualifications in Research & references.
3. **Solution reveal:** full-bleed solid butter yellow, oversized charcoal "Meet Peekaboo.", "A better moment to look.", one software description and How it works action. New transparent standing capybara pose presents the microscope. Keep existing navigation styling and omit archive chrome here. No rays, charts or outcome statistics on the reveal.
4. **Approach:** "How does Peekaboo decide?" followed by Observe / Estimate / Decide. One connected workflow: actual acquired synthetic frame, conceptual Gaussian sketch, and stable/changing shape decision branches. The remaining image budget constrains both branches. A return arrow explains repeating after the next capture. Model sketch and branch illustration are explicitly conceptual; full heuristic explanation stays in the disclosure.
5. **Gaussian explanation:** "What is a Gaussian?" Interactive analytic intensity surface with position, elongation and relative brightness controls plus Reset model. Label the surface conceptual and in relative units; height depicts intensity. Below, show actual acquired synthetic pixels and the actual native CUDA Rust fit from the same frame 0, with "From pixels to timing" explaining how shape change informs acquisition timing. Keep saved evidence immutable under slider changes. References explain intensity-weighted fitting, scope and CellSplat4D inspiration without claiming full reproduction.
6. **CUDA Rust rendering:** "One model. Many pixels." Conceptual fitted-parameter sketch flows into a custom native-GPU tile module and an actual saved frame-0 intensity image. Inspectable tile buttons map 128 logical output positions to a two-row overlay in the 64x64 image. Explicit CPU capture-decision / GPU rendering roles; caption says illustrative tiling and saved output. Expanded kernel/checks/sources includes native code, saved export verification, dated upstream links and full-path performance caveats. No live-browser CUDA or universal speedup claim.
7. **Demo:** "Same specimen. Different timing." Two large aligned image wells, capture/hold metadata, shared clock/transport and exposure lanes. Settings collapsed by default. No mascot/rays in the experiment panes. Selected synthetic run stays visible.
8. **Results state:** "More divisions. Fewer captures." for the featured successful run; neutral/data-dependent headings for alternatives. Show divisions, both capture counts, estimated imaging light and its qualifier, Replay / Inspect evidence and cohort disclosure. No automatic jump.

Presentation has seven hash-addressable slides; results remains a state of Demo. References and final asset prompts: [solution/approach provenance](design-exploration/solution-approach/PROVENANCE.md). The standing mascot is [solution-capybara.png](../apps/web/public/peekaboo/solution-capybara.png), generated with built-in ImageGen and confirmed to have real transparency.

On a 1366×768 presentation screen, opening and default demo should fit without clipped controls. On phones, stack panes in the same order with synchronized clock; allow natural vertical scrolling. Keep screenshots and text as separate HTML/assets, never install a whole generated mockup as the page.

## Motion and SideRays

Opening only. Following the user's full-viewport refinement, render the light in a fixed body portal starting at the top-right screen edge, outside the presentation max-width, gutters and slide clipping. Keep foreground content above it and omit the Research archive trigger from the opening header. Final user-requested refinement uses the supplied settings: speed 2.5, intensity 2, spread 2, density 5, glow 1, dust 0, followMouse true, mouseInfluence 0.5, opacity 1 and DPR cap 1.5. The real WebGL effect fills the viewport behind the transparent mascot without masks or content-container restrictions. Use warm gold and pale blue. Prefer the supplied standalone React component over installing an unnecessary UI framework.

Respect reduced motion dynamically and provide a motion toggle for continuous effects. Pause when slide inactive, tab hidden or illustration offscreen. Static fallback must look complete without WebGL2. Verify StrictMode cleanup, context recovery, resizing and render-loop termination. Do not add GradientASCII to this direction.

React Bits upstream [license](https://github.com/DavidHDev/react-bits/blob/main/LICENSE.md) was inspected: MIT plus Commons Clause. Retain its notice and upstream attribution with any vendored component. The adapted SideRays component is integrated and lifecycle-tested; its full notice is served at `/licenses/react-bits-SideRays.txt`. It is unrelated to native CUDA Rust science.

Capture feedback remains the primary demo animation: brief border pulse and scan/snapshot cue only on actual acquisition transitions. A held frame must not flash as a new capture after pause/resume or slide return. Reduced motion uses an immediate clear status change. Avoid bouncing the entire mascot or continuously moving image panes.

## Evidence and implementation boundary

Preserve all contracts and tests in the implementation plan. Generated screen imagery is layout reference only. Actual saved metrics and images override all generated labels, timing marks and cell renderings. No science changes, reruns, commit, push or deployment are part of this design handoff.

The presentation, replay, results and archive chrome now use this theme. Browser QA covered all seven slides and results at 1440x900, 1366x768, 390px and 320px, plus replay/evidence state and motion lifecycle. See HANDOFF.md and BUILD_PHASES.md for executed checks and remaining human gates.
