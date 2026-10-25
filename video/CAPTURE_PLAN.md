# Peekaboo — capture sheet

Companion to IMPLEMENTATION_PLAN.md. These are planned takes, not existing files.
All source-media timecodes must be measured after recording. Experiment frame
numbers below were checked against the saved seed 304 ledgers during planning.

## Recording setup

1. Start the existing apps/web development server with its documented npm command;
   use the actual printed port. Prior sessions used 5174. Do not assume a server
   is still running. Navigate to `/#demo`, `/#model` and `/#compute` as appropriate.
2. Use a dedicated browser context, viewport 1920×1080, device scale 1, zoom 100%,
   no extensions/popups/personal information. Record the viewport, not desktop chrome.
   Save masters at 30fps or preserve original timestamps and explicitly conform to
   30fps during preparation. Confirm actual metadata; do not just rename a format.
3. Wait for all images/fonts and the initial state before starting. Check browser
   console and failed requests. Disable unrelated system notification/audio capture.
4. Keep actual mouse movements economical. Move away from the specimen after a click.
   Never synthesize a cursor over footage to pretend an interaction happened.
5. Save masters under ignored `video/public/recordings/`. Record two takes only if
   needed for a defect; no obligation to rerecord a clean take. Preserve source files.

## Takes

| ID / suggested file | State and exact action | Minimum usable material | Film use |
|---|---|---|---|
| D01 / demo-304-master.mp4 | `/#demo`; Fewer images; Visible precursors; seed 304; Fixed 40; observed image view; quick/constant-speed playback. Frame 0. Record setup hold, actual Play comparison click, all source frames 0–239, auto results, result hold. | 3s before click, uninterrupted full replay, 8s after results. Record at least 30s, extend if needed. | 13–48s main evidence |
| D02 / demo-304-markers.mp4 | Same state. Enable Show divisions explicitly, reset/seek to frame 0 as needed and verify toggle remains enabled. Run through end. Markers must reveal only at/before current source frame. | Full replay + 5s end hold. | Optional marked version; label markers as evaluation annotations, not predictions |
| D03 / demo-304-shape.mp4 | Same state; seek to source 120; pause; show 132, 136, 138, 140, 141. Capture actual slider interaction or run from 120 without cuts. Keep both method panels and source frame indicator. | 2s holds at inspected frames; clean continuous 120–141 take if using motion. | Causality/model inset, not a replacement for main continuous replay |
| D04 / result-evidence.mp4 | End D01; open Across all six evaluation seeds. Show selected-example disclosure and fixed-32 option in a separate take if needed. Do not switch settings under a result from another configuration. | 5s full result; 6s readable disclosure; optional 5s fixed32. | Scope and provenance / backup |
| G01 / gaussian-model.mp4 | `/#model`; start default controls; move shape only, pause; reset; move position only, pause; reset. Show actual acquired/model pair unchanged by conceptual controls. | 5s default, each gesture + 3s hold, 5s paired source images. | 62–76s |
| C01 / cuda-render.mp4 | `/#compute`; default source; select one tile, hold; select another, hold. Show CPU/GPU labels and saved output. Open provenance in a separate take. | 5s default; 4s per tile; 8s disclosure. | 76–120s |
| L01 / abrupt-304.mp4 | `/#demo`; Fewer images; Sudden divisions; seed 304; Fixed 40. Reset; run and reveal results. Check exact outcome before edit. | Full replay + 8s results. | 120–126s failure example |
| R01 / real-data-evidence.mp4 | Research archive only if its shown results match the completed Phase 5 artifacts. It is documented as an older partial export. Prefer a source-backed editorial evidence card if not refreshed. | 8s stable relevant evidence. Optional authentic source microscopy requires dataset attribution. | 126–134s; never use beneath featured winning statistics |

Recorded app footage must retain the existing synthetic/data-scope labels even
though the narration says only “controlled experiment.” Editorial diagrams get
“Conceptual visualization.” Actual model imagery must say acquired-image fit,
not forecast of an unseen division. Use “Recorded app” for screen footage.

## Exact experiment anchors

Source: `apps/web/public/demo/controlled/budget32/manifest.json` and `evidence.json`.

- `304-precursor`: 240 source frames, adaptive 32 acquisitions, fixed_0 40.
- Division times sorted: **140, 173, 186, 194**. Coverage criterion ±1 source frame.
- Adaptive acquisitions in the first useful close-up: **120, 132, 136, 138, 140**.
  Decisions at 136/138/140 are shape-triggered bursts. Their recorded target gaps
  are 4/2/2; at 132 the decision still records target gap 12. Do not rewrite the
  recorded decision order to make an earlier frame appear prescient.
- All adaptive acquisitions: 0,12,24,36,48,60,72,84,96,108,120,132,136,138,140,
  152,164,168,170,172,174,178,182,184,186,190,192,194,206,218,230,239.
- In `304-abrupt`, adaptive covers **0/4**, fixed_0 **1/4**. This is a selected
  adverse example; the six-seed abrupt cohort is 4/24 vs 11/24. Do not mix them.

The current quick playback schedules roughly 18 source steps/second, but browser
rendering can lengthen wall time. 239 steps nominally take about 13.3s; a prior
measured browser run took longer. **Measure the actual take.** The 22-second film
demo slot includes setup/explanation and result arrival, not a claimed playback
duration. Fit the continuous take with genuine opening/end holds. If it exceeds
the slot, retime neighboring editorial allocations within the overall target;
do not silently omit divisions or time-compress only one method.

## Edit decision list template

For each source record: `id`, `path`, `sha256`, `appRevision`, `capturedAt`,
`width`, `height`, `fps`, `durationFrames`, `scenario`, `seed`, `methods`,
`sourceInFrame`, `sourceOutFrame`, `filmFromFrame`, `playbackRate`, `notes`.

Leave unknowns null until captured. Source in/out positions reference video
frames; experimental frame t belongs in separate notes/anchors. Cuts and slow
motion are editorial changes and must not imply biological timing. Default
playbackRate is 1. Paused detail views should be visibly a close-up/freeze.

Keep a full uncut comparison as backup. Label accelerated experiment replay on
screen; capture sweep duration is a UI cue, not microscope exposure duration.
If cropped for readability, retain equal specimen scale, method names, acquisition
counts, shared clock and data labels. A crop that loses these is not an acceptable
main comparison. Reframing cannot turn predicted/held imagery into acquired imagery.

## Acceptance before editing

- Both panels cover the same full field of view, without uneven zoom or clipping.
- No loading placeholders, cursor covering events, debug panels or browser errors.
- Counts/schedules match the manifest; end results match evidence exactly.
- Show-divisions markers are identifiable as offline evaluation annotations.
- Save hashes and timecodes; verify masters play offline.
- No music, narration or SFX captured into app masters. Mix them separately.
