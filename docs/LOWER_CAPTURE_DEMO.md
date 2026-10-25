# Lower-capture demonstration — 2026-10-25

**Latest card revision:** the former final-specimen/health card now reports
**Less imaging light**,20% versus fixed for32/40 captures, with the equal-illumination
assumption and phototoxic-stress context. It reports0% versus fixed for32/32 and
40/40. No health percentage is inferred. Build, seven Node tests and
`.tools/glimpse-light-stat-check.cjs` pass; desktop/mobile screenshots captured,
mobile inspected, no overflow at1440/390/320. The existing Three.js warning remains.
Latest local screenshots: `.tools/glimpse-light-stat-{desktop,mobile}.png`.

Glimpse now opens the measured **Fewer images** comparison. In the featured
synthetic precursor example, seed304, adaptive captures **4/4 divisions with32
images**, versus **1/4 with40 fixed images**. Both observe the same240-frame
sequence. The original40/40 comparison remains under **Equal budget**.

## Selection and scientific meaning

The user authorized featuring a favorable measured scenario. Seed304 was selected
**after evaluation** as an illustrative successful example: the lowest seed in
the cohort with complete adaptive coverage and the largest division-count advantage
over fixed40. This is presentation selection, not a new independent test.
The UI marks the seed as featured and explains selection in the cohort disclosure.
All six predeclared prospective seeds301–306, all three conditions and every
unfavorable result remain available. No simulator, event time, policy or score
was changed to improve the result. See [the registered probe](CONTROLLED_BUDGET_PROBE.md)
and [complete results](CONTROLLED_BUDGET_RESULTS.md).

| Comparison | Adaptive | Fixed |
|---|---:|---:|
| Featured seed304 precursor coverage | 4/4 | 1/4 |
| Images per run | 32 | 40 |
| Six-seed precursor coverage | 23/24 | 11/24 |
| Six-seed sudden-event coverage | 4/24 | 11/24 |
| Six-seed precursor coverage with fixed32 selected | 23/24 | 8/24 |

The lower image count is a declared budget, not an algorithmically discovered
minimum. It demonstrates performance at that budget. Seed301 misses one precursor
division; this cohort does not establish universal complete coverage at32 images.
The synthetic morphology cue is deliberately informative and does not establish
real-cell performance. Frozen real-microscopy findings remain unchanged.

With equal illumination per image,32 versus40 corresponds to20% fewer exposures
and20% less imaging light. It does not establish a20% reduction in cellular damage
or a biological health outcome. The UI states this assumption and leaves health
unmeasured. The image-count/stat cards and comparison bars derive from selected
saved schedules. Switching fixed to32 changes the denominator correctly: the
exposure-reduction card then reports86.7% versus all-frame imaging, shared by both.

## Export and reproduction

`scripts/export_controlled_budget_demo.py` reads the portable compressed original
summary and verification under `docs/evidence/controlled-budget32-v1/`. It checks
the summary hash, registered source hashes, complete cohorts, exact per-method
counts, contiguous traces, gap constraints, source-pixel hashes and every metric
against regenerated source clips. It runs no controller. Evidence/reference data
are separate from the replay manifest and images.

```powershell
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
.venv/Scripts/python.exe scripts/export_controlled_budget_demo.py --cuda
```

The exporter refuses an existing output; use `--output <fresh-directory>` for
verification reruns. The committed display assets are under
`apps/web/public/demo/controlled/budget32/`, so replay needs no Python/GPU runtime.
Omit `--cuda` to export acquired pixels without a model-view option. Both options
preserve scientific results. The export has a120-second batch deadline and25-second
GPU-request timeout, as with the existing bounded workflows.

Executed export:72 verified rows;36 actual CUDA Rust fit-render batches with
sampled CPU comparisons; maximum observed absolute error1.1920928955078125e-7
(tolerance2e-6);26.7 seconds internally.57 files,5,805,660 bytes including the
export-verification record. All original demo assets are preserved. Exported
file hashes and native-render metadata are in
`apps/web/public/demo/controlled/budget32/export-verification.json`.

## Frontend QA

Environment: `http://127.0.0.1:5174/`, installed Playwright Chromium because the
Browser plugin is unavailable. Capture animation and constant shared-clock
playback are retained; no recent-capture strip or new dependency was introduced.

| Check | Result |
|---|---|
| Page identity / blank page / framework overlay | Pass: expected Glimpse page, complete working comparison |
| Console and HTTP health | Pass: no app errors or failed HTTP responses |
| Evaluation gating | Pass: no controlled reference/evidence fetch before reveal/completion |
| Past-only images and counters | Pass: selected schedule's acquired indices at seven replay timestamps |
| Full default playback | Pass:22.069s, automatic reveal;4/4 vs1/4,32 vs40,20% savings |
| Every lower-budget seed/scenario | Pass: all18 selected-run metrics match saved evidence |
| Cohort and featured-selection disclosure | Pass:23/24 vs11/24 and post-evaluation selection visible |
| Fixed32 comparator | Pass:32/32 bars,86.7% versus all-frame,23/24 vs8/24 cohort |
| Original equal-budget mode | Pass: seed2026,4/4 vs3/4,40/40,83.3% versus all-frame |
| Cross-mode resets and replay | Pass: reset clock, results, seed, phase and selected evidence |
| CUDA model view | Pass: correct comparison's model assets requested |
| Reduced motion | Pass: sweep animation disabled; visible status retained |
| Responsive and screenshot review | Pass: no overflow at1440/1024/768/390/320; desktop/mobile inspected |
| Frozen Phase5 registration | Pass: implementation/inventory unchanged |

Commands: `npm.cmd run build`, `npm.cmd test` (seven passing Node tests),
`.venv/Scripts/python.exe -m pytest tests/test_controlled_budget_export.py tests/test_controlled_event_focus.py -q`
(14 passed in3.15s), and `node .tools/glimpse-budget-mode-check.cjs`.
New Python tests reject tampered metric values, declared budgets, traces, source
hashes, duplicate comparisons, invalid indices and changed portable evidence.
The existing Three.js chunk warning remains. Other browser engines, physical mobile
devices and the human ten-second comprehension gate remain untested.

## Local screenshots

![Featured lower-capture results](../.tools/glimpse-budget-results-desktop.png)
![Mobile lower-capture results](../.tools/glimpse-budget-results-mobile.png)
![Recorded capture comparison](../.tools/glimpse-budget-captures-desktop.png)
![Mobile capture panel](../.tools/glimpse-budget-captures-mobile.png)
