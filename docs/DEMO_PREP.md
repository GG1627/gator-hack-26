# Peekaboo / PHOTON — Demo and judge preparation

Prepared October 25, 2026. This guide describes the implemented prototype and
verified results. **Peekaboo** is the demo/product name; **PHOTON** is the underlying
project name used in the code and scientific records. Glimpse was the earlier product name.

## 1. The project in one sentence

> Peekaboo combines Gaussian cell modeling, native CUDA Rust rendering and adaptive acquisition to explore how microscopy can preserve important events with fewer light exposures.

**Tagline:** See more. Illuminate less.

**The problem:** Researchers need enough microscopy images to observe important
cellular events, but repeated illumination can bleach fluorescent signals and
cause phototoxic stress. A fixed schedule keeps capturing at regular intervals
without responding to whether the specimen is changing.

**Our approach:** Use acquired observations to decide when to look again. Wait
longer during stable periods and concentrate observations around visible change,
while respecting a declared image budget and observation-gap constraints.

**Intended users:** Researchers doing live-cell time-lapse microscopy. This
prototype is an offline acquisition study and interactive replay, with future
microscope integration as a possible next step.

## 2. Are we done?

The core prototype and approved demonstration are implemented. The original
real-microscopy Phase 5 benchmark is complete and independently recomputed.
The frontend, controlled experiments, native GPU kernel and supporting verification
are functional. The current priority is presentation and reproducibility readiness.

Still outstanding before calling the entire submission finished:

- Run the unfamiliar-viewer ten-second comprehension check.
- Walk through setup from a fresh checkout/environment.
- Prepare the pitch and submission text, credits and dated technology evidence.
- Record a backup demo and verify it opens without a network connection.
- Refresh the optional real-microscopy browser archive if presenting complete
  Phase 5 image results there; its current export is an earlier partial snapshot.

The primary synthetic demo does not depend on that optional archive refresh.
No additional hour-long benchmark is necessary to prepare this presentation.

## 3. How we fit “Fresh off the Frontier”

The challenge asks for a technology, dataset or discovery first publicly available
within the preceding twelve months, used centrally to solve a problem or explore
an idea. For an October 2026 presentation, our strongest implemented technology
anchor is **NVIDIA cuTile Rust**. Recent microscopy research provides an additional
research connection.

| Technology/resource | Dated evidence | What it contributes to our actual project |
|---|---|---|
| NVIDIA CUDA Rust, specifically **cuTile Rust** | Upstream changelog records release 0.0.1 on **April 7, 2026**; broader NVIDIA announcement **September 8, 2026** | Our custom Rust GPU kernel evaluates batches of Gaussian intensity fields; the resulting model imagery is part of the demo, with CPU-reference checks. |
| **CellSplat4D** microscopy research | First listed arXiv submission **October 3, 2026** | Research inspiration for a simplified evolving Gaussian representation of cellular observations; our acquired-image Gaussian shape measurements also support adaptive scheduling. |
| Causal adaptive acquisition controller | Our project implementation | Chooses acquisition times from acquired images and budget/gap constraints, with no future-image or event-label inputs. This is our engineering contribution. |

Primary sources:

- [cuTile Rust release history](https://github.com/NVlabs/cutile-rs/blob/main/CHANGELOG.md)
- [NVIDIA CUDA Rust announcement, September 8, 2026](https://developer.nvidia.com/blog/introducing-cuda-rust-two-tracks-for-writing-gpu-kernels/)
- [CellSplat4D paper and submission history](https://arxiv.org/abs/2610.04199)

**Date wording matters:** April 7 is a documented cuTile Rust release date;
September 8 is the broader announcement. Do not describe the announcement as the
first public availability of all constituent software. For the final eligibility
packet, preserve the earliest-public-availability evidence rather than relying
only on a recent blog post. Ultimate eligibility is the organizers' decision.

**Implementation wording matters:** We use cuTile Rust. Do not claim we implemented
both CUDA Rust tracks or used cuda-oxide's SIMT kernel-authoring path. Gaussian
splatting in general predates the challenge window; the recency connection is the
specific recent tooling/research, not Gaussian mathematics itself.

CellSplat4D is an inspiration, not a full reproduced method. We did not reproduce
its PSF estimation, complete 4D optimization or 3D U-Net supervision pipeline. Lead
the implementation claim with our actual cuTile kernel rather than implying we
integrated the complete paper.

## 4. What the main technologies actually do

### Gaussian modeling

We fit compact Gaussian descriptions to nuclei in acquired pixels. A Gaussian has
a position, brightness and shape/covariance. In the controlled controller, elongation
is measured through aspect ratio: stronger shape cues shorten the target gap from
12 frames to 4 or 2. These thresholds are engineering heuristics, not calibrated
probabilities of biological division.

The real-microscopy branch also includes causal tracking and Gaussian forecasts.
The controlled demo's model view shows the latest acquired-image Gaussian fit,
held between captures. It does not predict or synthesize an unseen division.

### Native CUDA Rust

We wrote a real tile-based Gaussian accumulation kernel in Rust. It evaluates
intensity fields over pixels/voxels on an NVIDIA GPU and has a CPU reference.
It is scientific computation, not just the browser's decorative 3D animation.

- Kernel: [crates/photon-gpu/src/main.rs](../crates/photon-gpu/src/main.rs)
- Dependencies: [crates/photon-gpu/Cargo.toml](../crates/photon-gpu/Cargo.toml)
- Python bridge/fallback: [services/science/photon/gpu.py](../services/science/photon/gpu.py)
- Timing investigation: [cuda-latency-audit.md](cuda-latency-audit.md)

The lower-budget export executed 36 native GPU batches. Sampled CPU comparisons
had maximum absolute error **1.1920928955078125e-7**, below the **2e-6** tolerance.
Export verification records are included with the display assets.

**Important boundary:** acquisition decisions and acquired-image fitting currently
run on CPU. The GPU renders Gaussian models; it does not make the controller's
capture decisions. The browser replays exported imagery and does not require
CUDA at presentation time. Do not claim a demonstrated whole-application speedup.

### Adaptive scheduling and causal evaluation

The controller receives acquired observations only. It cannot read the current
hidden image before choosing to capture it. Event labels are opened for offline
scoring after schedules are closed. It obeys budget and gap constraints and logs
its decisions.

- Controlled policy: [experiments/controlled/event_focus.py](../experiments/controlled/event_focus.py)
- Generator/replay/evaluation: [experiments/controlled/benchmark.py](../experiments/controlled/benchmark.py)
- Lower-budget experiment: [scripts/probe_controlled_budget.py](../scripts/probe_controlled_budget.py)
- Verified display export: [scripts/export_controlled_budget_demo.py](../scripts/export_controlled_budget_demo.py)

### Supporting stack and dataset

Python, NumPy and SciPy support scientific computation. Rust/cuTile provide native
GPU rendering. React, TypeScript, Vite and Three.js provide the interactive frontend.
Three.js renders the conceptual hero and interactive scientific views; it is
separate from our Rust scientific kernel.

MSKCC-CONFOCAL C. elegans microscopy provides authentic 3D+t evaluation data.
It is an older dataset, not our twelve-month eligibility claim. The main controlled
demo uses explicitly labeled synthetic microscopy and retains known ground truth.

## 5. The numbers to memorize

### Featured lower-capture example

**Mode:** Fewer images. **Scenario:** Visible precursors. **Seed:**304.

| Statistic | Peekaboo | Fixed |
|---|---:|---:|
| Experiment length | 240 frames | 240 frames |
| Images taken | **32** | 40 |
| Divisions covered | **4/4** | 1/4 |
| Division coverage | **100%** | 25% |
| Relative imaging light, assuming equal light per image | **80%** | 100% |

Peekaboo uses 8 fewer images: **20% fewer exposures than fixed**. Its selected-run
coverage advantage is 75 percentage points. Event coverage means an acquisition
within **±1 source frame** of a programmed division; it is not event-detector recall.

Seed 304 was selected after evaluation to illustrate a successful case. It was
not predeclared as the default before those outcomes were known. All six seeds
are available and the UI discloses the selection in the cohort details.

### All six new evaluation seeds,301–306

| Scenario | Adaptive 32 | Fixed 40 | Fixed 32 |
|---|---:|---:|---:|
| Visible precursors | **23/24** | 11/24 | 8/24 |
| Sudden divisions | **4/24** | 11/24 | 8/24 |
| Quiet specimen | Undefined: no events | Undefined: no events | Undefined: no events |

Precursor coverage is 95.8% versus 45.8% for fixed 40. One precursor division is
missed in seed 301. Without a precursor, sparse adaptive timing performs worse.
Do not extend the featured4/4 result into a claim of complete coverage everywhere.

The32-image budget was chosen before this probe; the controller spends that budget.
We have not demonstrated automatic discovery of the minimum number of images.

### Original equal-budget experiment

The **Equal budget** mode preserves the original six-seed experiment:

- Both methods use40 images over 240 frames.
- Precursor cohort: adaptive 24/24 versus standard fixed 12/24.
- Shifted fixed phases:13/24 and12/24.
- Sudden-event cohort: adaptive 6/24 versus standard fixed 12/24.
- Original featured seed 2026: adaptive 4/4 versus fixed 3/4.

These are different seed cohorts and budgets. Do not mix their numerators,
denominators or selected-run outcomes.

## 6. Light exposure, phototoxic stress and cell health

The frontend's **Less imaging light** statistic is calculated as:

```text
relative imaging-light reduction = 1 - adaptive captures / fixed captures
                                = 1 - 32 / 40
                                = 20%
```

This assumes the same illumination per image: intensity, exposure duration,
illuminated geometry and other relevant settings remain equivalent. We measure
capture counts; absolute dose in J/cm² is not measured in this prototype.

The denominator must be clear:

| Comparison | Capture-count reduction |
|---|---:|
| Peekaboo32 versus fixed 40 | **20%** |
| Peekaboo32 versus all 240 frames | 86.7% |
| Fixed 40 versus all 240 frames | 83.3% |
| Either40-image schedule versus the other | 0% |

Use **phototoxic stress**, not “photonic stress.” Published work supports the
biological motivation: light exposure can disrupt cellular processes, with effects
depending on dose, wavelength, specimen and illumination pattern.

For example, PhotoFiTT reports that6J/cm² at 475 nm caused over 50% mitotic delay in
CHO cells. That is a study-specific division-timing effect, not a universal health
percentage and not a calibration of our simulated nuclei or MSKCC embryos.
[PhotoFiTT, Nature Communications,2025](https://www.nature.com/articles/s41467-025-66209-6).
Related primary research examines wavelength, labeling and cell-dependent damage:
[Wäldchen et al.,2015](https://www.nature.com/articles/srep15348).

Recommended wording:

> In this controlled example, Peekaboo uses20% fewer exposures. Assuming equal illumination per capture, that means20% less imaging light—the light burden that can cause phototoxic stress.

> Peekaboo is designed to reduce unnecessary illumination while preserving important observations. Actual cell-health improvement requires biological validation.

Do not claim20% less cellular damage, improved survival or healthier final cells.
The two replay schedules observe the same underlying specimen trajectory; the
simulator does not model illumination-induced injury or repair.

## 7. Live-demo walkthrough

1. Open `http://127.0.0.1:5174/`. Start with the hero: “See life. Spend light wisely.”
2. Explain the problem in one sentence, then enter the experiment.
3. Leave **Fewer images → Visible precursors → Seed 304 → Fixed 40** selected.
4. Press Play. Point out that both panels share the same clock and experiment
   duration. Each sweep is a capture; the image holds when there is no exposure.
5. Explain the difference in timing: fixed has regular gaps; Peekaboo varies its
   spacing in response to shape cues. Its target gap can shrink during change.
6. Let the results open automatically. Say “Four divisions captured with 32
   images, compared with one using40 fixed images.20% fewer exposures.”
7. Point to **Less imaging light** and state the equal-illumination assumption.
8. Open **Across all six evaluation seeds** if asked about selection or reliability.
9. Use Fixed 32 or Equal budget if asked about fairness. Both comparisons are real.
10. Show Sudden divisions if asked about limitations. Open the real-microscopy
    archive if asked about real-data work, noting its partial display snapshot.

The default lower-budget playback plus automatic results took about 22 seconds in
tested local Chromium. Viewing speed is accelerated replay, not real biological
time. The sweep animation's duration is not microscope exposure duration.
Optional capture pauses are a viewing aid affecting the shared replay clock.

## 8. Suggested spoken pitches

### Thirty-second introduction

> Microscopes need light to see living cells, but that same light can disturb the processes researchers want to study. Peekaboo decides when another picture is worth taking. We model acquired cell images with Gaussian shapes, adapt capture timing to visible changes, and use native CUDA Rust to render the models. In this controlled example, we capture all four divisions with 32 images, while fixed imaging captures one with 40. That's20% fewer exposures, with the full experiment and limitations available to inspect.

### Three-to-four-minute outline

| Approximate time | What to cover |
|---|---|
| 0:00–0:30 | Biological motivation: observing cells can disturb them; fixed timing cannot respond to changing activity. |
| 0:30–1:15 | Run the featured demo. Explain the shared clock, capture sweeps, held images and adaptive bursts. |
| 1:15–1:45 | Show4/4 versus1/4,32 versus40, and20% less imaging light under equal illumination. Identify the synthetic condition. |
| 1:45–2:30 | Explain the recent technology: actual Rust GPU Gaussian kernel using cuTile, dated2026 releases, and CellSplat4D inspiration. |
| 2:30–3:00 | Difficulties: toolchain, GPU numerical parity, transport overhead and strict future-image isolation. |
| 3:00–3:30 | Six-seed results, sudden-event limitation and completed real-microscopy evaluation. |
| 3:30–4:00 | Next step: biological/hardware validation and better calibrated event prediction; finish with “See more. Illuminate less.” |

Treat these as talking points to rehearse, not a script to read word for word.

## 9. Likely judge questions

**What is an acquisition budget?**

The number of images allowed, including the initial observation. Our controllers
currently spend their exact declared budget. The featured comparison gives
Peekaboo32 images and fixed 40; equal-budget controls are also available.

**Shouldn't both methods have the same interval?**

They should observe the same time span and source clock. Their acquisition
intervals intentionally differ: fixed is regular, while adaptive changes its
spacing. Equal intervals would eliminate the scheduling behavior being tested.

**Is32 versus40 an unfair comparison?**

It asks whether useful event coverage can be retained with a smaller declared
budget. We also provide fixed 32 and the original40/40 comparison to separate
image-budget effects from scheduling effects. This does not establish an optimal
budget or the best possible fixed schedule across all phase choices.

**Did you choose a favorable example?**

Yes. Seed 304 illustrates successful precursor-aware timing and was chosen after
evaluation for presentation. All six evaluation seeds are accessible, with
aggregate23/24 versus11/24 and the missed event retained. We also show conditions
where the method performs worse.

**How do you know when a cell will divide?**

The controlled model provides a visible elongation precursor. Our controller
measures shapes in acquired pixels and responds to a heuristic threshold. It is
not a trained biological predictor, and cannot reliably anticipate abrupt events.

**Does it cheat by reading future images or division times?**

The scientific controller only receives past acquired observations. Labels are
used after closure for scoring. The frontend is a replay of those closed runs;
it does not execute the policy. Evaluation imagery is fetched separately after
reveal/completion. Causality tests perturb future images and verify earlier decisions.

**Is the demo running the microscope/controller live?**

No. It replays authentic outputs from a causal synthetic acquisition experiment.
The source images, schedules and metrics were generated and checked before export.
There is no hardware connection in the hackathon prototype.

**Is the GPU just rendering the decorative hero?**

No. The custom Rust kernel computes scientific Gaussian intensity fields used
for model renders. Three.js handles browser graphics separately. Capture decisions
and fitting run on CPU, and the browser replays precomputed outputs.

**Does using the GPU make the whole system faster?**

Not universally. We measured numerical parity and component timings; transport,
initialization and output costs can dominate. The real-volume path remains CPU
by default. Some dense small-output workloads benefit, but we do not claim a
general application speedup.

**Did you implement CellSplat4D?**

We built a simplified Gaussian observation/forecasting system inspired by recent
microscopy research. We did not reproduce its complete 4D/PSF/neural pipeline.
Our concrete new-tooling implementation is the cuTile Rust kernel.

**Does it work on real microscopy?**

We have a completed, independently recomputed36-run benchmark on two held-out
C. elegans embryos using an older frozen controller. It did not beat fixed on
division coverage. The newer controlled controller demonstrates a useful mechanism
in synthetic conditions; it has not established the same gains on real cells.

**Are the cells healthier with Peekaboo?**

We measured fewer scheduled exposures, not viability. At equal illumination per
capture, the example uses20% less imaging light. We would need a biological
experiment to establish changes in phototoxic stress, growth or survival.

**What's next?**

Evaluate the newer controller on independent real microscopy, improve perception
and uncertainty calibration, and eventually test a microscope integration with
measured illumination and biological outcomes. These are future capabilities.

## 10. Difficulties we can substantiate

- **Toolchain setup:** native Rust GPU work required WSL/Linux tooling and a
  compatible CUDA environment on the RTX 4070 Laptop GPU.
- **Numerical correctness:** CPU/GPU floating-point behavior near truncation
  boundaries required conservative boundary handling and reference repair.
- **Performance surprises:** faster device work did not remove transport/JIT/
  initialization overhead. A persistent worker and improved packing helped,
  while CPU remained appropriate for real-volume predictions.
- **Causality and fairness:** acquisition, label access and scoring were separated;
  budgets/gaps, target sets, trace consistency and seed provenance were verified.
- **Real-data modeling weakness:** Gaussian appearance/forecasting did not beat
  raw hold. Isolated perception/appearance experiments exposed limitations and
  motivated a controlled observability experiment instead of a fabricated win.

## 11. Real-microscopy results in reserve

Phase 5 evaluated s2/s3, 270 volumes each, budgets 27/54/89 and six schedules per
condition: 36 closed runs, followed by offline scoring and exact source recomputation.

- Fixed covers more annotated divisions in all six conditions.
- PHOTON has lower raw-hold image MSE on pairwise-common withheld targets in 5/6
  conditions. Those target sets depend on both schedules.
- Fixed has lower raw-hold MSE on each schedule's own withheld frames in all 6/6.
- Gaussian forecast MSE loses to raw hold in all 36 runs.
- Only two independent embryos; random seeds are schedules, not new embryos.

These findings establish a working causal evaluation system and identify real
limitations; they do not establish general adaptive superiority. See
[PHASE5_RESULTS.md](PHASE5_RESULTS.md) for exact numbers and provenance.

## 12. Practical preparation and evidence links

### Start the portable demo

Reuse the existing server if it is running. Otherwise, from the repository root:

```powershell
Set-Location apps/web
npm.cmd ci
npm.cmd run dev -- --port 5174 --strictPort
```

Open `http://127.0.0.1:5174/`. The committed synthetic assets allow replay without
Python, the raw microscopy dataset, CUDA or external APIs. Initial dependency
installation may require network access. Real-microscopy archive assets remain local.

### Verification already executed

- Production TypeScript/Vite build passed; existing large Three.js chunk warning remains.
- Seven Node tests passed.
- Fourteen focused Python tests passed for controlled acquisition and lower-budget export integrity.
- Chromium tested all 18 lower-budget seed/scenario outcomes, both comparison modes,
  fixed 32 control, result resets, causal image display, evaluation gating, GPU-model
  assets, reduced motion and five widths 320–1440.
- Latest light-stat check verified 20% for 32/40 and0% for 32/32 and40/40, with no
  browser errors and no overflow at desktop/mobile widths.
- Frozen Phase 5 source registration passed after frontend integration.

These checks were executed during development; they are not a claim that a fresh
machine or every browser engine has been tested.

### Evidence map

| Need | Where to look |
|---|---|
| Latest handoff | [HANDOFF.md](HANDOFF.md) |
| Phase status and executed checks | [BUILD_PHASES.md](../BUILD_PHASES.md) |
| Main demo/export/QA detail | [LOWER_CAPTURE_DEMO.md](LOWER_CAPTURE_DEMO.md) |
| Lower-budget full results | [CONTROLLED_BUDGET_RESULTS.md](CONTROLLED_BUDGET_RESULTS.md) |
| Pre-execution lower-budget plan | [CONTROLLED_BUDGET_PROBE.md](CONTROLLED_BUDGET_PROBE.md) |
| Portable original probe evidence | [docs/evidence/controlled-budget32-v1](evidence/controlled-budget32-v1) |
| Exported metrics | [budget32/evidence.json](../apps/web/public/demo/controlled/budget32/evidence.json) |
| GPU/export/file-hash verification | [budget32/export-verification.json](../apps/web/public/demo/controlled/budget32/export-verification.json) |
| Original equal-budget experiment | [CONTROLLED_EVENT_FOCUS.md](CONTROLLED_EVENT_FOCUS.md) |
| Real-microscopy benchmark | [PHASE5_RESULTS.md](PHASE5_RESULTS.md) |
| GPU timing limitations | [cuda-latency-audit.md](cuda-latency-audit.md) |
| Earlier research/context | [GLIMPSE_DEEP_RESEARCH.md](GLIMPSE_DEEP_RESEARCH.md) |

### Final rehearsal checklist

- [ ] Save dated copies/screenshots of the upstream eligibility sources.
- [ ] Have an unfamiliar viewer describe the project after ten seconds.
- [ ] Verify setup from a fresh checkout and test the exact presentation browser.
- [ ] Confirm the default state is Fewer images / Visible precursors /304 / fixed 40.
- [ ] Rehearse the 20% light calculation and the synthetic-versus-real distinction.
- [ ] Know where to open all-seed evidence, equal-budget controls and failure cases.
- [ ] Record a 60–90-second backup video with readable result cards.
- [ ] Keep the laptop awake/charged and test playback with networking disabled.
- [ ] Finish submission text, source links, dataset attribution and credits.
- [ ] Avoid last-minute scientific changes or long reruns merely for presentation.
