# Glimpse: research and project elevation handoff

**Deep research follow-up (2026-10-24):** See
[GLIMPSE_DEEP_RESEARCH.md](GLIMPSE_DEEP_RESEARCH.md) for the Astra review, the
June 2026 CellposeDINO candidate, first-public-date corrections, implementation
findings, and proposed perception/reliability/decision gates. These are research
recommendations unless separately recorded as implemented. The user confirmed switching to Astra.

**Latest continuation:** the user subsequently authorized autonomous implementation.
The opening-page update and an isolated experimental watershed detector are now
implemented and tested. See [PERCEPTION_EXPERIMENT.md](PERCEPTION_EXPERIMENT.md) for
actual development results, limits and forecast probes. The earlier discussion-only
instruction below is historical; the frozen Phase5 benchmark remains protected.

Recorded 2026-10-24. The user approved these directions for investigation and
requested durable notes before switching Codex accounts. **This is a research
backlog, not authorization to rewrite the frozen benchmark or implement every
idea. Instruction at the original handoff: discussion/documentation only; no code changes yet.**

## Where we are

- PHOTON is the scientific prototype; **Glimpse** is its demo identity.
- Real microscopy replay, causal acquire/skip scheduling, a simplified dynamic
  Gaussian model, a verified native CUDA Rust renderer, and the E / Contact
  interactive frontend are implemented. This is offline replay, not connected
  microscope hardware. The frontend consumes saved authentic artifacts.
- Predictions, acquired measurements and evaluation-only images are distinguished.
  Heuristic uncertainty and event interest are not calibrated probabilities or a
  validated biological division predictor.
- Current event audits favor fixed sampling over PHOTON in all six held-out
  conditions. Gaussian prediction and overall scheduling superiority are not
  established. Acquisition counts are exposure proxies, not measured cell health.
- GPU correctness is verified. Real-volume full-call overhead leaves CPU faster;
  the controller/replay remains CPU by default. Browser WebGL is a separate display.
- Phase 6 automated checks passed; formal unfamiliar-viewer comprehension remains
  open. Phase 7 reproducibility/submission/backup-demo work also remains.
- Source/UI/runner checkpoint: commit
  `f77c213342a5c51a264970508433cef715ee3b2d` on `origin/main`.

## Protect the background evaluation

The user personally launched `scripts/finish_phase5.py`. At this handoff check,
PID **55068** existed as Python, status reported step **1/5**, and the log had
advanced to `Offline evaluation t=100/269`. This is an observation, not a promise
that it will still be running when the next session opens.

Read `runs/phase5-runner/status.json` and the tail of
`runs/phase5-runner/latest.log` first. Commands are in [PHASE5_RUN.md](../PHASE5_RUN.md).
Do not start a second evaluator, kill the existing process, modify frozen science,
or launch resource-heavy experiments while it runs. The old
`runs/phase5/checkpoint.json` describes the historical pause and is not a live
progress tracker. All five runner stages succeeding still requires result review.

## Recommended order

1. Finish and review the frozen benchmark, including failures and actual timings.
2. Diagnose why adaptive scheduling loses: timing, budget pacing, event signal,
   model error and evaluation-window effects are hypotheses to inspect, not known causes.
3. Select **one** bounded scientific improvement and define a falsifiable test.
4. Develop it in a separate experiment with explicit data separation; preserve
   original results and source hashes.
5. Add a judge-facing interaction that makes the measured contribution obvious.

The priority is a verifiable improvement in deciding when to acquire. More
frameworks or newer technology alone do not establish a stronger contribution.
No approach can guarantee a hackathon win.

## 1. Error-calibrated acquisition — first scientific experiment to consider

**Proposal:** replace or supplement heuristic uncertainty with an empirically
validated estimate of forecast reliability. On development data, test whether
observation age, motion, model changes and earlier residuals predict subsequent
error. Investigate acquiring when predicted error exceeds a defined tolerance.

**Research:** Ye et al., *Learned, uncertainty-driven adaptive acquisition for
photon-efficient scanning microscopy*, Optics Express, 2025.
[Paper record and abstract](https://pubmed.ncbi.nlm.nih.gov/40798069/)
([DOI](https://doi.org/10.1364/OE.542640)). The work estimates reconstruction
uncertainty and uses it for selective spatial rescanning. Our temporal scheduling
problem needs a new adaptation; this is not a drop-in method or an inherited guarantee.

**Small experiment:** test whether the proposed score predicts actual error on
development-only temporal masks, then compare scheduling against fixed timing
and the frozen heuristic at equal capture budgets. Include raw hold and Gaussian
forecast errors, event coverage and maximum gaps; preserve losses as well as wins.

**Boundaries:** offline development targets may supervise training; live decisions
may use only acquired observations available then. Errors visible only at selected
acquisitions can be selection-biased. Temporally correlated samples and the small
number of embryos limit calibration claims. Do not call a score a probability or
claim distribution-free guarantees without the needed assumptions and validation.

**Demo payoff:** show the forecast losing reliability, the reason for an acquisition,
and its measured correction after reveal. This behavior is proposed, not implemented.

## 2. Causal division-risk prediction — closest to the original ambition

**Proposal:** investigate a small model predicting an approaching division from
past acquired morphology, intensity and dynamics. Establish tracking/label quality
and learnability before choosing a network or adding a foundation model.

**Research:** Stepp et al., *Smart hybrid microscopy for cell-friendly detection of
rare events*, Nature Communications, 2026.
[Paper record and abstract](https://pubmed.ncbi.nlm.nih.gov/41501068/)
([DOI](https://doi.org/10.1038/s41467-025-68168-4)). Their hybrid-EDA uses label-free
surveillance and dynamics-informed neural networks to trigger fluorescence imaging.
Our current recordings do not supply that label-free surveillance stream, so we
cannot claim to reproduce their setup or obtain free observations between captures.

**Small experiment:** define a prediction horizon and causal features, check whether
they predict annotated divisions on development data, then test whether the signal
improves scheduling. Event prediction accuracy and acquisition event coverage are
different outcomes; measure both appropriately. Never expose future annotations to
the deployed controller.

**Risk:** limited independent training examples, unreliable identity association,
and ambiguous pre-division morphology. A trained model is worthwhile only if it
adds validated information beyond observation age and simple baselines.

## 3. GPU ensemble forecasting — meaningful next CUDA Rust workload

**Proposal:** evaluate a bounded collection of plausible Gaussian futures with
different motion estimates or explicitly modeled split hypotheses. Use disagreement
as a candidate acquisition signal. This is our proposed engineering direction,
not a claim that the cited papers implement it.

**Small experiment:** CPU reference first; fixed batch sizes and numerical parity;
then benchmark CUDA cold/warm/device/transfer/full-call latency. Compare the
ensemble controller to an otherwise identical single-model controller. The useful
question is whether computation enables better decisions within the timing budget.

**Risk:** correlated hypotheses can agree while all being wrong; disagreement is
not automatically calibrated uncertainty. Rendering a large full-volume ensemble
may worsen current memory/latency pressure. Profile and consider a scientifically
justified compact score before expanding kernel scope. Preserve the existing
CUDA audit and do not advertise application speedups based on device timing alone.

## 4. Selective CellSplat4D adaptations — reconstruction research, higher scope risk

**Research:** Tao and Lu, *CellSplat4D: PSF-Aware 4D Gaussian Splatting for Sparse
Robotic Live-Cell Imaging*, preprint submitted 3 October 2026.
[Abstract](https://arxiv.org/abs/2610.04199) ·
[Full text](https://arxiv.org/html/2610.04199v1).

Potential ideas include optical point-spread-function modeling, temporal component
lifetimes and foreground/nucleus-focused reconstruction evaluation. The paper
discusses ambiguity between emitter extent and optical blur; do not freely fit
both and interpret the result as a uniquely identified biological shape. Its
specific optics assumptions also need scrutiny before applying to our confocal data.

**Critical causal distinction:** section IV-C uses two bracketing volumes for
temporal completion. The later volume cannot inform an earlier online acquisition
decision. Retrospective completion may be studied separately and labeled as such;
an online adaptation must only consume information available at decision time.

Full reproduction is a substantial research/training project. Prefer one bounded
adaptation and an ablation over replacing the working prototype. Our current
implementation is a simplified dynamic Gaussian model, not full CellSplat4D.
Additional spatial lineage metrics remain constrained by the known TSV/XML
coordinate mismatch; resolve that before claiming nucleus-level position accuracy.

## 5. Interactive budget experiment — recommended demonstration addition

Let a judge choose an image budget and inspect the resulting event/quality trade-off,
with synchronized measured images, predictions, decision reasons and evidence reveal.
The existing 27/54/89 budgets provide authentic starting points. Expose only budgets
with actual results, or explicitly execute and label new experiments; do not interpolate
favorable scores or suggest a saved replay is a live controller.

A useful visual would pair acquisition-count savings against all-frame imaging with
equal-budget quality/event results against fixed sampling. Keep successes and failures
visible. The interface should make the chosen scientific contribution understandable
without requiring judges to know what Gaussian covariance or CUDA means.

## Experiment integrity and implementation gates

### Head-to-head demo discussion — 2026-10-24

The user requested a clearer fixed-versus-Glimpse story, prominent image counts,
and discussion of cell health. **Discussion/documentation only; no UI changes.**

**Product objective:** spend the imaging budget when observations are most useful.
The aspiration is to retain useful biological information with fewer acquisitions,
or retain more useful information at the same acquisition count. Fewer images alone
can be achieved by any sparse fixed schedule; the adaptive timing needs its own proof.

Proposed three-column evidence presentation, using the existing B54 condition:

| Strategy | Acquired source volumes | Reduction against every-frame capture | Purpose |
|---|---:|---:|---|
| Every-frame reference | 270/270 | 0% | Dense source recording/reference, not a separately conducted biological arm |
| Fixed timing | 54/270 | 80% | Sparse baseline at equal budget |
| Glimpse adaptive | 54/270 | 80% | Test whether different acquisition timing retains more useful information |

Those counts are actual schedule counts; 80% is arithmetic, not a measured health
benefit. One acquisition is a complete 41-plane source volume in this dataset;
predicted frames and repeated playback of a held image are not additional captures.
Do not say Glimpse takes 80% fewer images *than fixed* in this comparison.

Below counts, reveal real annotated-event coverage and reconstruction errors with
provenance, missing/pending states and matched-target qualifications. Current event
audits favor fixed in all six conditions. Do not choose a false winner, manufacture
missed events or blur the fixed images to make the adaptive view look better.
An eventual equal-quality comparison across budgets is another possible experiment;
it requires measured curves and a predefined quality criterion, not an assumed gain.

**Cell health is not measured.** Do not invent damaged/dead cells, a survival count,
health percentage, or differential scan deterioration. Both displayed schedules
subsample the same pre-recorded specimen; replay cannot create separate biological
outcomes. Under the equal-per-volume-dose assumption, fixed and adaptive at B54 have
the same total exposure-count proxy. Timing effects on viability are unknown here.
Actual optical dose also depends on illumination settings and acquisition protocol.

If the motivation needs an explainer, use a separate clearly labeled educational
illustration of potential light-exposure risks with literature attribution. Any
hypothetical simulation must display its assumptions and simulated status throughout;
do not mingle fictional damage with experimental evidence. Preferred demo metric:
“Acquisition-count exposure proxy”; health panel, if present: “Not measured.”

**Positioning:** event-driven microscopy is an established research area, with
[event-driven acquisition demonstrated in 2022](https://www.nature.com/articles/s41592-022-01589-x)
and [hybrid-EDA published in 2026](https://www.nature.com/articles/s41467-025-68168-4).
Do not claim the problem has never been addressed or that we invented adaptive
microscopy. Our contribution must be the implemented causal Gaussian-based
scheduler, verified CUDA Rust computation, transparent benchmark and any separately
validated improvement. Their combination does not establish first-of-its-kind status.

Suggested aspiration copy: **“Spend observations where they matter.”**
Supporting factual copy: “Glimpse uses a predictive Gaussian model to choose when
to acquire the next microscopy volume. Compare its recorded choices with fixed
timing at the same image budget, then reveal what each schedule captured.”

Before frontend implementation, select the comparison condition, verify source
counts/metrics and decide whether to show both the dense reference and sparse fixed
baseline. Preserve original source pixels and visible scientific limitations.

- s1 is development data. s2/s3 outcomes have already been inspected; they cannot
  become fresh untouched tests for a revised controller. Declare reuse explicitly
  and obtain an independently held-out sequence for a new generalization claim.
  Do not quietly retune on the current evaluation outcomes.
- Register a new experiment and save separately. Do not modify frozen protocol,
  registered source, existing trajectories, original scores or their provenance.
- Evaluate at equal budgets with causal inputs, reproducible seeds/configuration,
  appropriate baseline/ablation comparisons and explicit uncertainty in conclusions.
- Stop an experiment that fails a predefined useful-effect or feasibility check;
  document the failure rather than hiding it or growing scope indefinitely.
- Do not add LLM agents, foundation models, reinforcement learning or services just
  for novelty. Do not claim phototoxicity reduction without biological evidence.
- If hardware integration is later considered, distinguish a simulator/adapter from
  an actual microscope experiment. No such integration has been implemented here.

## Model choice for the next session

Default GPT-6.1 Sol Medium suffices for documentation and established UI work.
Before substantial uncertainty/model/CUDA design, recommend GPT-6.1 Sol High as
required by AGENTS.md. For a deeper comparison of unfamiliar research approaches
or experimental architecture, recommend Astra Medium if it would materially help.
The user switches models manually; no switch has been confirmed in this record.
Do not recommend Astra High by default or assume a stronger model was selected.

## Paste into the next Codex session

> Read AGENTS.md, PHOTON_SPEC.md, BUILD_PHASES.md, docs/HANDOFF.md and
> docs/GLIMPSE_ELEVATION_RESEARCH.md. We have a working Glimpse E / Contact demo
> and verified scientific prototype. I launched the standalone Phase 5 runner;
> inspect its live status/log before doing anything and do not duplicate or stop it.
> We agreed to investigate error-calibrated acquisition, causal division-risk
> prediction, useful GPU ensemble workloads, selective CellSplat4D ideas, and a
> budget-driven judge interaction. Discuss and prioritize first; no implementation
> changes are authorized by these notes alone. Preserve frozen science, acknowledge
> existing fixed-baseline wins, and separate any new experiments from the old test.
