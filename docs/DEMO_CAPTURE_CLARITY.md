# Demo capture clarity and browser QA — 2026-10-25

## Latest user revision

Recent-capture thumbnails were removed at the user's request; their code and styles
were deleted. The capture sweep, held/new-image feedback, counters and timelines
remain. **Constant-speed playback is now default.** Optional capture pauses are
labeled as a viewing aid. Both methods share the same240-frame experiment and
40-image budget; the UI states this before the comparison. Fixed has approximately
regular gaps (integer frame rounding); adaptive intentionally varies its gaps.
Viewing speed and sweep duration are presentation choices, not measured microscope
exposure settings. This revision supersedes the original implementation record below.

Build and seven Node tests pass. `node .tools/glimpse-clock-check.cjs` passed
page identity, absence of recent captures, shared source/timeline clocks, retained
sweep, evaluation gating, original selected-run results, default full playback
in21.091s, replay/reset, optional pauses, reduced motion, five responsive widths
320–1440, adverse/quiet results and absence of browser errors. Browser plugin remains
unavailable; installed Playwright Chromium was used at localhost5174. Desktop/mobile
screenshots were visually inspected. Other browser engines and physical devices
remain untested; existing Three.js build warning remains. No scientific job or new
measurement was needed.

![Simplified desktop comparison](../.tools/glimpse-clock-desktop.png)
![Simplified mobile panel](../.tools/glimpse-clock-mobile.png)

## Summary

The approved Glimpse styling and recorded 40-image experiment are preserved.
Acquisitions now have a restrained scan sweep, a persistent capture number, and
explicit new-image versus held-image status. Four recent acquired images remain
visible and support click or keyboard inspection. Guided playback briefly holds
on captures and moves faster through gaps; Quick retains constant-speed replay.
The timeline highlights the most recent acquisition. Play brings the comparison
into view with clearance for the navigation header.

End results now include exposure bars for all-frame, fixed and Glimpse imaging,
calculated from the selected run. The dose assumption is explicit; cell health
remains unmeasured. No images, original metrics, controller decisions, fixed
timings, or evidence-fetch gates were changed. No dependency was added.

## Environment

- Local URL: `http://127.0.0.1:5174/`.
- Browser plugin not available; used the previously installed Playwright Chromium.
- Desktop/mobile widths: 1440, 1024, 768, 390 and 320 pixels.
- Normal and reduced-motion settings tested.
- Skills used: frontend-design-pro, React best practices, frontend testing/debugging
  and Playwright. Targeted UX guidance supported restrained feedback and reduced motion.

## Changes verified

`apps/web/src/ControlledLab.tsx` and `controlled-lab.css`: display acquired pixels
only, make each capture perceptible, retain the last observation while waiting,
and expose the same measured selected-run outcomes after replay completion.
Contact thumbnails always show acquired synthetic pixels, including when the
large viewer is switched to the explicitly labeled Gaussian model.

| Check | Result / evidence |
|---|---|
| Page identity | Pass: expected Glimpse title and controlled lab |
| Blank page / framework overlay | Pass: working controls and rendered comparison |
| Console health | Pass: no console/page errors or HTTP failures |
| Screenshots | Pass: desktop capture panel and results, mobile adaptive panel and results visually inspected |
| Interaction proof | Pass: capture inspection, keyboard activation, playback, resets, selectors, result comparisons |
| Causal display | Pass: images and thumbnail frames are acquired and no later than replay time |
| Evidence gate | Pass: no controlled evaluation fetch before reveal/completion |
| Responsive layout | Pass: no horizontal overflow at all five widths |
| Reduced motion | Pass: sweep animation disabled; text status remains available |
| Scientific source registration | Pass: frozen Phase 5 source/inventory still matches |

## Interaction loop

Load → inspect frames0/12/13/60/120/180/238 → compare each panel's image and counter
with its saved acquisition indices → click a recent capture → play Guided from0
→ verify capture dwell → finish automatically at239 → show original 4/4 versus3/4
result, 40 images each, 83.3% fewer exposures versus all-frame, eight simulated nuclei
→ replay/reset → Quick → switch to model → keyboard-inspect thumbnail → five widths
→ reduced motion → sudden/quiet scenarios → phase and seed reset.

The final full guided replay + automatic result presentation completed in
**28.919 seconds** in local Chromium. This is viewing time, not scientific compute
performance. An earlier pacing trial took34.7 seconds; waiting periods were shortened
while preserving capture dwell, then the whole interaction script passed again.
The initial screenshot exposed a sticky-navigation overlap; comparison scroll
clearance was added and the final desktop image was inspected with headers visible.

## Commands and remaining limits

- `npm.cmd run build`: passes; existing large Three.js chunk warning remains.
- `npm.cmd test`: all seven Node tests pass.
- `.venv/Scripts/python.exe -m pytest tests/test_controlled_event_focus.py -q`:
  six tests pass in4.37s.
- `node .tools/glimpse-capture-check.cjs`: complete Chromium interaction loop passes.
- `run_phase5.check_registration(Path('runs/phase5'))`: passes.
- Separate bounded32-image probe and its measured limits:
  [CONTROLLED_BUDGET_RESULTS.md](CONTROLLED_BUDGET_RESULTS.md).

Chromium only; physical mobile devices and other browser engines were not tested.
Human ten-second comprehension remains unrecorded. Browser scripts and screenshots
are ignored local artifacts; screenshot links below work in the current workspace.
The optional real-data archive still uses the earlier partial export.

## Screenshots

![Acquisition comparison and recent acquired images](../.tools/glimpse-captures-desktop.png)
![Mobile adaptive panel](../.tools/glimpse-captures-mobile.png)
![Results and relative exposure bars](../.tools/glimpse-dose-results-desktop.png)
![Mobile results](../.tools/glimpse-dose-results-mobile.png)
