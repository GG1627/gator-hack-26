# Peekaboo presentation redesign - implementation plan

Status: After Hours implemented and browser-verified on 2026-10-25. This replaces the previous L / rose-gold plan. Human comprehension, fresh-install and submission gates remain open.

## Accepted direction

Use **M - After Hours** and [AFTER_HOURS_DESIGN.md](AFTER_HOURS_DESIGN.md) as the authoritative visual specification: solid charcoal, butter yellow, blue and amber, bold Manrope typography, a capybara scientist at a microscope, and restrained opening-only SideRays. The generated reference board supplies composition, not scientific data. No further broad style exploration is needed.

Preserve useful partial frontend interaction work. Replace rose/serif/optical styling throughout the presentation, including supporting archive chrome. Do not roll back unrelated changes.

## Experience and slide content

| Step | Main point | Primary visual / interaction |
| --- | --- | --- |
| 1. Opening | See more. Illuminate less. | Peekaboo wordmark, capybara scientist illustration with restrained SideRays, Start the story; direct Demo shortcut |
| 2. Problem | Every observation has an exposure cost. | An authentic dataset image with provenance; short illumination timeline; one brief research citation |
| 3. Approach | Choose when to look. | Stable period vs visible change; Observe → Estimate → Decide; clearly labeled conceptual illustration |
| 4. Representation | Turn observations into a compact model. | Actual acquired image and its Gaussian representation, with concise explanation; CellSplat4D inspiration, not reproduction |
| 5. Computation | Render the Gaussian model with CUDA Rust. | Simple CPU fitting/scheduling → native Rust GPU rendering → saved replay diagram; dated source links in an expandable reference area |
| 6. Demo | Same specimen. Different capture timing. | Existing controlled comparison with large acquired-image panes, shared clock, capture animation, two exposure lanes |
| Demo outcome | What did these schedules preserve? | Evidence-derived divisions, image counts, and estimated imaging-light reduction; Replay and Inspect evidence |

Outcome is a state of the final demo, not an unrelated wall of statistics. Give the presenter an explicit View results action when results are ready; do not unexpectedly advance a slide. Support replay and returning to the completed comparison.

Each slide has one headline, one main visual, and at most a short explanatory sentence. Source details and scientific caveats must remain discoverable through labeled references/evidence, with essential qualifiers next to their claims. References are actual links, not an ornamental paper list. Recheck dated technology claims against primary sources before publishing final slide copy, starting from docs/DEMO_PREP.md.

## Navigation and state

- Small persistent Peekaboo brand, Story / Demo navigation, slide index and previous/next controls. Hash-addressable slides and browser back/forward, without adding a router dependency unless necessary.
- Keyboard arrows navigate only when focus is not in a form control or timeline. Native range inputs retain normal keyboard behavior. No wheel hijacking or timed slide advance.
- Move focus to the slide heading after explicit navigation; keep hidden slides out of the accessibility tree and tab order. Mobile uses natural vertical content within the current slide, without fixed-height clipping.
- Keep demo state in a stable owner. Leaving the demo pauses it but preserves position/settings; returning does not reset. Replay explicitly resets the current run. Changing comparison/scenario resets dependent data as before.
- Opening Research pauses playback, preserves its state, and returns to the invoking control on close. Existing archive remains accessible outside the main presentation sequence.
- Do not mount/render all expensive canvases continuously. Inactive decorative effects stop; fetch or render archive assets only when relevant. Essential presentation works without WebGL.

## Proposed frontend boundaries

Retain React/TypeScript/Vite. Review existing code before finalizing names; keep the refactor modest.

- App.tsx: presentation shell and navigation; move the existing real-data Replay UI into a separate archive component with its current behavior preserved.
- Presentation.tsx / story content module: six slide definitions, navigation, source links, and accessible lifecycle.
- Peekaboo theme stylesheet: tokens, typography, surfaces, focus states, layout and reduced motion. Scope/archive legacy styling to avoid accidental global overrides.
- Small shared UI family: Button, SlideNavigation, SourceDisclosure, CaptureStatus, PlaybackControls, ExposureTimeline, ResultSummary. Reuse existing Icon where appropriate, with consistent weights and sizes.
- ControlledLab.tsx: preserve saved-data selection and metrics. Extract a small replay hook if needed for lifecycle management. Separate comparison and result rendering; replace scrollIntoView completion behavior with an explicit outcome state.
- Preserve Microscope atlas indexing, held-frame semantics, error/loading states, asset paths and causal evidence gates. Keep captured vs held vs reconstructed visibly distinct.
- Rename product-facing Glimpse labels, page metadata, accessible names and current demo documentation to Peekaboo. Keep PHOTON scientific identifiers, source hashes, immutable evidence and historical records unchanged; document the naming relationship rather than bulk replacing internals.

## Science and content contracts

- Default remains synthetic visible-precursor seed 304, adaptive 32 vs fixed 40, on one 240-frame source clock. Label the synthetic scenario and selected illustrative run.
- Featured outcome remains data-derived: 4/4 vs 1/4 divisions and 20% fewer captures. Estimated 20% less imaging light assumes equal illumination per capture. Do not claim measured health, stress or viability improvement.
- Equal-budget comparisons remain available and show 0% light reduction when counts match. Preserve original 40/40 mode, fixed32 comparison, all seeds/scenarios, and accessible adverse/cohort evidence.
- The browser replays precomputed experiments; it does not run the native GPU kernel or controller. CPU handles fitting and acquisition decisions; native cuTile Rust renders Gaussian intensity. Decorative WebGL/SideRays is unrelated to that scientific kernel.
- No unacquired future-frame images or event evidence appear before reveal. If displaying known saved future schedule marks, clearly separate them from information available to the simulated controller; prefer elapsed exposure marks during playback.
- Real MSKCC imagery and provenance are separate from the synthetic comparison. Real Phase 5 does not establish superior division coverage. Preserve that limitation in the evidence layer.
- The real archive is still a partial exported snapshot. Do not relabel it as the full completed benchmark. Updating its exporter is separate work, not a prerequisite for this redesign.
- No modifications to frozen scientific algorithms, protocols, registrations or benchmark results. No new long scientific runs needed for frontend work.

## Artwork and opening effect

Use the local transparent mascot and coordinated screen board linked in [AFTER_HOURS_DESIGN.md](AFTER_HOURS_DESIGN.md). Implement all text and controls in HTML. Use actual local dataset material for the problem slide and saved model outputs for representation; retain provenance and display normalization. Generated imagery is never scientific evidence.

The screen board contains invented scale bars, channel counts, minute intervals, playback duration and image content: do not copy these. It also shows radial line accents and subtle shading; the actual design uses solid surfaces and restrained top-right SideRays. Use the written specification for these intentional corrections, six-slide navigation and actual evidence values.

The mascot is a static transparent asset. Animate entrance and separate rays only; additional poses or a rig are optional future work. No GradientASCII. The supplied SideRays component may be adapted with upstream license notice retained. See the design specification for initial settings and lifecycle requirements. Do not add shadcn or a new framework solely for this component.

## Implementation sequence and gates

1. **Baseline and visual specification.** Inspect existing screenshots/UI, required skills, assets and tests. Run baseline web checks. Capture current behavior. Use the completed After Hours specification, references and asset provenance. Inspect current UI and confirm the baseline before edits.
2. **Opening + functional demo slice.** Add local typography/artwork and tokens; build the opening and accessible presentation shell; integrate the actual comparison with custom controls. Verify both ends of the experience together before extending intermediate slides.
3. **Story + science visuals.** Implement problem, approach, representation and CUDA Rust slides. Add primary-source references and actual dataset/model images. Keep paragraphs out of the primary composition.
4. **Results + supporting evidence.** Implement outcome state, replay, optional experiment settings, cohort evidence and archive access. Finish product rename. Audition SideRays only after the core experience works.
5. **Verification and refinement.** Check desktop, laptop projector dimensions and mobile, all core interactions and failure paths. Compare native-size rendered screenshots to accepted references, fix differences, and update BUILD_PHASES.md and HANDOFF.md with executed evidence.

Proceed through these authorized steps without asking for approval after every small decision. Surface changes to methodology, primary demonstration criteria, or major dependencies before making them. User can steer during implementation. Do not commit/push or deploy solely because earlier unrelated work was authorized for push.

## Acceptance checks

- npm.cmd test and npm.cmd run build in apps/web; report actual results and existing warnings accurately.
- Browser verification of opening → story → demo → play/pause/seek → completion → results → replay; back navigation and direct Demo access; focus/keyboard behavior; hidden slides and archive lifecycle.
- Compare featured and alternate scenarios, both budget modes, comparator changes, light percentages and zero-event handling against saved evidence. Existing ignored Playwright scripts can inform checks but old selectors/scroll assumptions may need updates.
- Check evidence network gating, held-source indices, distinct acquired/model states, no stale results after switching modes, and no running playback after leaving demo.
- Desktop 1440×900, common presentation laptop 1366×768, mobile 390px and narrow 320px; no horizontal overflow or cropped controls. Reduced motion, missing assets, unavailable WebGL, console errors and font loading.
- Inspect accepted concepts and rendered screenshots together. Record at least typography, color, layout, imagery, component and responsive fidelity; distinguish accepted refinements from accidental drift.
- Do not rerun all scientific benchmarks for a UI-only change. Run relevant additional tests only if data helpers/export behavior changed.
- Human ten-second comprehension and Phase 7 fresh-install/backup recording/submission checks remain outstanding until actually performed. Do not mark those gates complete from automated frontend checks.

## Model handoff

Implementation and functional regression checks are complete. GPT-6.1 Sol Medium is sufficient for isolated copy/layout refinements. Retain stronger engineering review if making substantial replay or evidence-state changes; Astra is not needed for routine execution. The user changes models manually.

## Executed implementation checks - 2026-10-25

- All six slides, demo/results, custom controls, authentic context/model imagery and archive chrome restyled. Opening uses the transparent mascot and adapted standalone React Bits SideRays. Upstream notice is retained in source and served at `/licenses/react-bits-SideRays.txt`. Newsreader removed; Manrope is local.
- `npm.cmd test`: all 7 existing tests passed. `npm.cmd run build`: TypeScript and Vite passed. Existing lazy Viewer3D chunk warning remains; it is outside the initial story bundle.
- Playwright Chromium used because Browser plugin is unavailable. Identity, meaningful content, absence of framework overlay, console health, screenshots and interactions passed.
- Six slides plus results checked at 1440x900, 1366x768, 390x844 and 320x740. No horizontal overflow. Default desktop story/demo/results fit the viewport; mobile scrolls naturally. Concept/render review covered typography, colors, mascot, spacing, controls and responsive behavior. Scientific images/metadata deliberately use saved evidence rather than generated board placeholders; rays are restrained rather than radial decoration.
- Full playback to frame 239: 40 Fixed / 32 Peekaboo captures, 239 observed DOM updates without a source frame later than the replay clock, no automatic results jump. Play/pause/seek, replay, hash/back navigation, heading focus, demo persistence and archive pause/return verified.
- All 36 saved run result displays matched their ledgers across both modes, all seeds and all three scenarios. Fixed32 and both alternate fixed offsets checked; equal counts display 0% less light. No changes to scientific algorithms or evidence.
- Explicit evidence-network gating, inspect-evidence expansion, quiet/adverse copy and selected-run qualifiers checked. Ambient pause, dynamic reduced motion, tab hide, inactive/covered effect suspension, native WebGL context loss/recovery, no-WebGL fallback, actual capture pulses and absence of a false resume pulse passed. Manifest failure and retry recovery passed.
- Screenshots and temporary QA scripts are outside the repo under the local temp `peekaboo-after-hours` directory. Human ten-second understanding, fresh install, backup recording and submission remain unverified.
