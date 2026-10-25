# Event-focused controlled demonstration

**Latest UI — 2026-10-25:** the default demonstration now features the separate
measured32-image adaptive versus40-image fixed comparison. Seed304 was selected
after evaluation as a successful precursor example; all six prospective seeds,
unfavorable scenarios and a fixed32 comparator remain available. The original
40/40 experiment documented below remains under **Equal budget**. See
[LOWER_CAPTURE_DEMO.md](LOWER_CAPTURE_DEMO.md) for selection, results, export and QA.

This is an explicitly synthetic observability experiment, authorized by the user
after the real-data ablations showed weak scheduling gains. It supplements the
real microscopy evaluation; it does not replace it or establish biological efficacy.

## What changed

The old controller frequently clips motion scores and produces nearly periodic
captures. Improving segmentation changed only four of 54 capture times. The new
experimental controller measures the largest Gaussian aspect ratio in **acquired
pixels**, shortening its observation gap from 12 to four or two frames when shape
changes become apparent. Exact-budget feasibility guards preserve 40 acquisitions
and gaps of two through 12 frames. It does not receive event labels or future images.
This is a different controller and evaluation branch, not a change to frozen Phase 5.

The synthetic forward model has four drifting Gaussian nuclei, 240 64×64 frames,
independent randomized division times, and additive noise. In the favorable
condition, shape elongates over 24 frames before splitting. Abrupt divisions remove
that cue. Quiet clips remove divisions. These are deliberately simplified conditions
for testing what the controller can observe, not a realistic validated cell simulator.

Development seeds were 7 and 42. Settings were then held fixed for evaluation seeds
101–105 and 2026. Demo seed 2026 was declared before those results. Each condition
compares three fixed schedule phases, the existing paced_robust controller, and the
new event-focus controller. Every method uses exactly 40 images. Event coverage is
an acquisition within ±1 frame of a programmed division. Multiple cell events at
nearby times can be covered by one image, consistently for all methods.

## Actual results

All six evaluation seeds, 24 events per event-bearing condition:

| Method | Visible precursor | Abrupt division |
|---|---:|---:|
| Fixed, standard phase | 12/24 | 12/24 |
| Fixed, +⅓ interval | 13/24 | 13/24 |
| Fixed, +⅔ interval | 12/24 | 12/24 |
| Existing adaptive controller | 12/24 | 12/24 |
| New event-focus controller | **24/24** | **6/24** |

Quiet coverage is undefined, not zero or 100%. No method improves total acquisition
count over another in this exact-budget comparison. All use 83.3% fewer images
than all-frame acquisition. This is an exposure-count proxy, not measured cell health.

The favorable result establishes that this controller can exploit the synthetic
precursor. The abrupt result exposes its cost: sparse quiet observations miss sudden
events. The experiment does not prove better real-data forecasting, calibrated
uncertainty, learned mitosis prediction, or performance on unseen biological data.

## Reproduction and verification

Use a fresh output directory for a rerun:

```powershell
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
.venv/Scripts/python.exe scripts/run_controlled_benchmark.py --output runs/controlled-heldout-new
.venv/Scripts/python.exe -m pytest tests/test_controlled_event_focus.py -q
.venv/Scripts/python.exe scripts/export_controlled_demo.py --cuda
```

The exporter defaults to the original `runs/controlled-heldout-v1/summary.json`;
pass `--input` to export a new run. The benchmark checks its 120-second deadline
at every decision. The exporter checks its own 120-second deadline between clips;
each GPU request also has a 25-second timeout. Import/startup time is outside the
reported internal batch timings. No full real-volume experiment is launched.

Executed evidence:

- Development: 30 comparisons, 6.2 seconds inside the runner.
- Evaluation: 90 comparisons, 19.3 seconds inside the runner; complete.
- Six focused tests passed in 4.45 seconds, including future-image perturbation,
  exact budget/gaps, fixed phase fairness, event tolerance, and type/history guards.
- Export: all 90 metric rows recomputed from regenerated source
  images and saved schedules; source SHA-256, image SHA-256 and trace consistency checked.
- Native CUDA Rust rendered 54 batches of Gaussian fits from acquired images.
  One scene per batch was checked against the CPU reference, tolerance 2e-6;
  observed maximum absolute error was 1.1920928955078125e-7.
  The export completed in 55.6 seconds inside its processing loop. These are
  verification timings under concurrent Phase 5 load, not performance benchmarks.

The web lab replays these closed runs. It displays the last acquired synthetic
pixels or a clearly labeled CUDA-rendered Gaussian fit; both are held between
captures. It **does not predict division**. Evaluation reference images and labels
are fetched separately after revealing results. Every evaluation seed, fixed phase,
and scenario is selectable; unfavorable conditions remain visible.

The controlled replay is the primary demonstration. At its final frame, playback
stops and evidence is revealed automatically. A large completion panel reports the
**selected run's** event capture rate and fixed comparison, images taken, acquisition
count reduction relative to all-frame imaging (the same for both schedules), and
final simulated nuclei/divisions. Health is not inferred. Six-seed aggregate results
remain in a separate disclosure. Replay restarts from zero and clears results.
Real microscopy remains accessible through an expandable research archive, and
the main demo is independent of the real-data manifest's loading/error state.
Full-playback browser checks passed for automatic completion, result values,
scrolling, replay/reset, abrupt/quiet results, five widths and archive navigation.

Artifacts: `runs/controlled-heldout-v1/{protocol,summary,export-verification}.json`.
A post-evaluation `source.zip` preserves the source/dependencies/tests; its
`source-archive.json` distinguishes this archival step from the pre-run protocol.
Generated controlled display files are included in Git at
`apps/web/public/demo/controlled` so a fresh checkout can play the primary demo.
Other large microscopy exports remain ignored. A compact evidence copy lives in
`docs/evidence/controlled-heldout-v1`; `summary.json.gz` expands to the original
measured JSON and can be checked against its recorded SHA-256.
Source code is outside the frozen Phase 5 package and test inventory.

Frontend verification completed: production build and seven existing Node tests
pass. Chromium exercised playback, past-only displayed source frames, all-seed
totals, seed/phase resets, the abrupt and quiet controls, the CUDA model view, and
evaluation fetch gating. Desktop/mobile screenshots were inspected; widths 1440,
1024, 768, 390 and 320 had no horizontal overflow or uncaught browser errors.
The original real-data replay also passed its interaction regression check.
Full Phase 5 registration (including the frozen file inventory) still passes.
The existing large Three.js chunk warning remains; no new runtime dependency was added.

As a secondary descriptive measurement, mean hold-last image MSE over **all 240
frames, including acquired frames**, is 2.77566e-5 fixed versus 2.06464e-5 event-focus
in the precursor condition (25.6% lower). It is worse for event-focus in abrupt
clips (6.75864e-5 versus 1.21726e-4) and quiet clips (6.75211e-6 versus 9.16603e-6).
These small whole-image errors include a large background and are not a substitute
for the primary event measurement or real-data image evaluation.
