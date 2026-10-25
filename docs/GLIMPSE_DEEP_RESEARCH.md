# Glimpse: frontier research decision brief

Latest implementation and measured follow-up: [PERCEPTION_EXPERIMENT.md](PERCEPTION_EXPERIMENT.md).
The opening scope below describes the original literature-review pass. Subsequent
user authorization allowed frontend work and the isolated perception experiments.

Research date: 2026-10-24. Model: GPT-6 Astra, confirmed by the environment and user.
Scope: literature, public repositories, and read-only inspection of our implementation.
No candidate models were installed, downloaded, trained, or benchmarked. No scientific
or frontend implementation was changed. Recommendations below are hypotheses and
proposed experiments, not measured improvements or an authorization to implement them.

## Recommendation

The strongest direction is **a microscope replay that maintains an inspectable
specimen model, estimates when that model becomes unreliable, and spends observations
to correct it**. Make the contribution visible through a measured → forecast →
acquire → correction → evidence interaction.

Investigate one new dependency first: **CellposeDINO**, especially its smaller
`cpdino-vitb` model, as an acquired-volume nucleus segmenter. Keep this conditional
on a small perception audit. If nucleus extraction is already adequate, skip that
integration and prioritize empirical forecast-reliability calibration directly.
Do not assume that adding a foundation model improves scheduling.

Then consider compact Gaussian ensemble scoring that actually influences acquisition.
The proposed chain is:

> acquired volume → nucleus instances → fitted Gaussian state → forecast reliability
> → budget-constrained acquisition → observed correction → sealed evaluation

This is a direction, not a commitment to complete every stage. The first scientific
increment should be one isolated change with an ablation. Frontend planning can
proceed while the existing evaluator runs; expensive experiments should wait.

## Findings in our existing implementation

These observations come from `services/science/photon/{gaussian,tracking,adaptive}.py`
and `docs/cuda-latency-audit.md`, inspected during this review.

- Detection thresholds a smoothed volume, labels connected regions, and fits one
  Gaussian per accepted region. Touching nuclei can merge. The severity on a
  representative development panel still needs measurement; this is a plausible
  bottleneck, not a demonstrated explanation of the benchmark losses.
- Shape and intensity are held while centers follow damped estimated motion.
  Candidate splits are association hints, not a validated advance division predictor.
- Scalar uncertainty grows from a heuristic base and elapsed time. The image
  uncertainty ensemble shifts the whole scene along physical axes; it does not
  represent independent cell dynamics or unseen division outcomes.
- Acquisition uses scalar uncertainty, motion, morphology, pacing, and gap rules.
  Rendered forecasts and image disagreement do **not** feed back into its score.
- Native CUDA Rust is real and verified, but currently optional rendering work.
  Transferring and writing full volumes dominates important real-workload costs.

Consequently, replacing the scalar threshold with a larger planner would not by
itself repair missing objects, unreliable associations, or a biased appearance model.
Better perception, better prediction, and better decisions need separate evidence.

## Candidate assessment and primary sources

### 1. CellposeDINO / updated Cellpose4 models — first new dependency to investigate

The authors document June 2026 releases of `cpdino` and smaller `cpdino-vitb`, based
on DINOv3, alongside `cpsam_v2`. The original `cpsam` dates to April 2025. Attribute
recency to the specific 2026 adapted model, not to Cellpose or DINO generally.
[Official model documentation](https://cellpose.readthedocs.io/en/latest/models.html)
and [release](https://github.com/MouseLand/cellpose/releases/tag/v4.2.1.1).

Public files include a 344 MB `cpdino-vitb` checkpoint and 1.21 GB `cpdino` checkpoint.
These are download sizes, not runtime memory estimates.
[Author-hosted weights](https://huggingface.co/mouseland/cellpose-sam/tree/main).

The volumetric path combines flows inferred from orthogonal 2D slices with 3D
dynamics; it is not a native temporal forecasting network. Anisotropy is supported.
Our recorded Z/XY spacing ratio is 5. Validate axis handling, boundaries, and
identity consistency rather than assuming the volumetric option resolves them.
[3D documentation](https://cellpose.readthedocs.io/en/latest/do3d.html).

The repository documents the additional DINOv3 dependency and training-data
restrictions; code licensing, model terms, and training-data terms need to be
recorded separately. The weight card has limited provenance. Audit whether training
included our evaluation datasets before making an unseen-data claim.
[Repository](https://github.com/MouseLand/cellpose),
[model card](https://huggingface.co/mouseland/cellpose-sam).

**Our judgment:** a stronger practical fit than training a new cell-fate network.
Run it only on acquired observations. Preserve Gaussian fitting/rendering as the
downstream model. Compare to both current detection and a simple watershed baseline.
Neither inference speed nor accuracy on MSKCC has been established here.

### 2. Automatic prompt generation (APG) with μSAM — alternate perception candidate

The March 18, 2026 arXiv paper adds automatic prompts to existing microscopy-tuned
SAM models without retraining the base model. Its reported comparison is 2D, even
for datasets originating as volumes. Code and APG documentation are public.
[Paper](https://arxiv.org/html/2603.17845v1),
[implementation](https://github.com/computational-cell-analytics/micro-sam).

**Our judgment:** useful alternate if CellposeDINO fails the bounded trial. Slice
accuracy does not prove coherent 3D nuclei. Avoid expanding the comparison to every
SAM variant. The precise earliest OpenReview posting was not confirmed because its
forum required browser verification; March 18 is a verified arXiv date, not a claim
that no earlier public version exists.

### 3. Temporal-attention cell-fate prediction — high ambition, high adaptation risk

The first verified arXiv version is **March 17, 2026**, preceding its October journal
publication. It studies cancer-cell outcomes under treatment.
[Preprint record](https://arxiv.org/abs/2603.16562).
The repository provides a ResNet/Transformer pipeline and trained checkpoint,
using tracked cell crops and reporter channels. Its default task distinguishes
eventual death from division; endpoint-truncation experiments inspect advance signal.
[Author code](https://github.com/bozeklab/Cell-Fate-Prediction).

**Our judgment:** eventual fate is not the same target as “division within the next
three source steps.” An embryo cell likely to divide eventually may offer no useful
timing signal. Missing reporter channels, 3D geometry, sparse/irregular observations,
and track association all require adaptation. All-cell prospective windows must
include non-event periods; known endpoint-aligned clips do not alone establish
deployment performance. Start with a small causal feature baseline before proposing
Transformer training. Keep any future training split grouped by independent movie
or lineage as appropriate, not random overlapping crops.

### 4. 3D light-sheet foundation model — credible future research, defer now

A May 25, 2026 preprint describes volumetric pretraining and downstream adaptation.
The public repository supplies UNet/SwinUNETR checkpoints and fine-tuning workflows
for binary segmentation, classification, and deblurring.
[Preprint](https://arxiv.org/abs/2605.26026),
[repository](https://github.com/AdinaScheinfeld/lsm_fm_public_repo).

**Our judgment:** confocal embryo instance separation differs from light-sheet
binary segmentation. We have lineage points rather than dense masks, so few-shot
fine-tuning introduces annotation work. It is not a pretrained division forecaster.
Checkpoint availability is verified from documentation, but local memory feasibility,
transfer quality, and complete reuse terms were not established. Do not retrain the
backbone during this hackathon.

### 5. CellSplat4D — deepen a bounded adaptation; preserve the causal distinction

Submitted October 3, 2026. Its method includes frame-unit temporal gates, a fixed
PSF, residual-guided capacity allocation, and nucleus-focused evaluation. Its gap
completion network consumes **two bracketing volumes**. That later observation is
unavailable to an earlier online decision. No author implementation link was located
in the examined paper/search; absence was not established exhaustively.
[Paper](https://arxiv.org/html/2610.04199v1).

**Our judgment:** most useful near-term ideas are evaluating foreground/model decay
and assigning representation capacity where an acquired image has large residuals.
Residual-driven extra Gaussians would be a scoped adaptation, not full reproduction.
Do not estimate a PSF from arbitrary specimen autocorrelation and assume biological
shape has been separated from blur. Confocal optics need their own justification.
Any backward-looking interpolation belongs in a separately labeled reconstruction
view, never in the acquisition controller's past inputs.

### 6. CUDA Rust — retain, and connect useful computation to decisions

The upstream changelog records an initial tagged cuTile Rust release on April 7,
2026 and beta on May 16. September 8 is the broader NVIDIA announcement, not the
first release of every constituent technology. The earliest pre-tag public exposure
was not exhaustively established. Pin the exact version used and retain its history.
[Upstream release history](https://github.com/NVlabs/cutile-rs/blob/main/CHANGELOG.md),
[announcement](https://developer.nvidia.com/blog/introducing-cuda-rust-two-tracks-for-writing-gpu-kernels/).

**Our proposed engineering contribution:** calculate compact forecast-disagreement
scores on GPU and return a small reduction instead of many full rendered volumes.
Choose evaluation sites from acquired/predicted geometry plus a background coverage
grid, never hidden future pixels. Compare the compact score to a full reference on
development cases, including missed births and empty-model failure cases.

This could reduce transport cost, but no speedup has been measured. First establish
that the CPU version adds useful decision information; then require numerical parity,
identical CPU/GPU decisions, and full-call cold/warm latency. An advanced kernel may
remain worth presenting when slower, as a verified experimental result with a clear
function. Do not add dummy workload to manufacture a crossover.

### 7. CELLECT — relevant to our exact data, but carries major evaluation caveats

Published October 20, 2025, just outside a strict October 24, 2025–October 24, 2026
window. The study uses MSKCC-CONFOCAL and NIH-LS. It is useful supporting technology,
not a clean recency anchor under that window.
[Publisher](https://www.nature.com/articles/s41592-025-02886-x).
The repository provides 3D tracking code/weights, uses consecutive image pairs,
and includes training examples involving our dataset family.
[Repository](https://github.com/zzz333za/CELLECT).

**Our judgment:** checkpoint training overlap must be resolved before any held-out
claim. Feeding it consecutive dense frames would violate our sparse observation
contract; feeding widely separated acquired frames changes its operating regime.
It could be useful for an offline diagnostic with explicit provenance, but is not
the first integration to attempt.

### 8. DUAL denoising and hybrid event-driven acquisition — useful context

DUAL's September 15, 2026 publication describes diffusion-based denoising with
temporal conditioning; representative data/code are linked publicly. Earliest
preprint/release timing was not conclusively established in this review.
[Paper](https://link.springer.com/article/10.1186/s43074-026-00288-6),
[repository](https://github.com/feilab-hust/DUAL).
**Our judgment:** defer. We lack an acquisition-dose/noise experiment establishing
that denoising is the limiting problem. Any temporal input would need a causal audit.

Hybrid-EDA had a public April 5, 2025 preprint, despite the later journal date. Its
label-free surveillance triggers fluorescence. Our recordings lack that extra stream.
[Preprint](https://www.biorxiv.org/content/10.1101/2025.04.04.647219v1).
Ye et al.'s uncertainty-guided spatial rescanning work was public October 24, 2023.
It remains methodological inspiration, not a new resource for this challenge.
[Preprint history](https://arxiv.org/abs/2310.16102).

## Proposed experiment gates

These gates are a draft to finalize and register before implementation/outcome inspection.
They are not changes to the frozen Phase 5 protocol.

### Gate A: determine whether perception is the limiting factor

Use a fixed s1 development panel spanning early, middle, and late recording. Freeze
frames/crops before comparing candidate outputs. Inspect native 3D orthoviews, not
only maximum-intensity projections. Establish whether components merge multiple
annotated nuclei and whether association becomes unstable across realistic gaps.

Then compare current thresholded components, a bounded marker-watershed baseline,
and one CellposeDINO checkpoint. Start with the smaller checkpoint, low inference
batch size, and explicit axes/anisotropy in an isolated environment after Phase 5.
Measure peak RAM/VRAM and complete per-volume time; checkpoint size is insufficient.
The observation cadence is 75 seconds, but a credible interactive path should leave
substantial compute headroom rather than merely fit inside that interval.

Use verified s1 centers for one-to-one detection matching under a predefined physical
tolerance. Points cannot establish mask IoU; dense-mask claims require independently
annotated masks. Keep calibration and assessment panels separate and report the
within-embryo limitation. Stop if the candidate fails to improve the declared
perception endpoint or exceeds the resource budget. A watershed win is a valid result.

### Gate B: establish forecast reliability before changing the scheduler

On development-only temporal masks, ask whether a small causal feature set predicts
future error better than elapsed observation age alone. Candidate features include
past prediction residuals, association ambiguity, motion, and ensemble disagreement.
At runtime, a residual becomes available only after acquisition. Use dense offline
development targets for scoring; selected-acquisition residuals alone are biased.

Keep raw hold, held Gaussian fit, and moving Gaussian forecast separate. Otherwise
appearance error may be mistaken for motion uncertainty. Evaluate contiguous reserved
development blocks with a gap between training/calibration and assessment; this
does not create an independent embryo. Prefer a small model with a useful reliability
curve to an unvalidated probability display. Stop if it adds no predictive information
beyond age and simple change features.

### Gate C: demonstrate that the signal changes decisions usefully

Freeze a single candidate policy and compare at equal budgets with fixed timing,
image-change, the existing heuristic, and an age-only version. If perception also
changes, include a perception-only ablation so its contribution is identifiable.
Define a primary outcome and useful-effect threshold before scoring; report secondary
outcomes and regressions. Include fixed phase sensitivity as a diagnostic without
choosing a favorable phase for the headline comparison.

s2/s3 outcomes have been inspected. Reuse can be labeled exploratory, but a new
generalization claim needs independently held-out data with model-training provenance
checked. NIH-LS is a candidate to investigate, not an approved or validated replacement.
Do not treat later adjacent frames of the same embryo as a new independent specimen.

At B89, the existing ±1-frame coverage metric is already near saturation for fixed
sampling. That leaves little room for event-count improvement. Preserve this result
and metric. A new pre/post-division observation or lineage-continuity endpoint would
require separate justification, annotation QA, and preregistration, not a post-hoc
change to turn the existing loss into a win.

### Gate D: make CUDA work consequential

Only after Gate B/C show a useful score, implement its CPU-equivalent GPU reduction.
Test parity around decision thresholds and preserve causal/budget/gap invariants.
Measure cold/warm full caller latency and memory at actual component counts and
horizons. Compare ensemble versus single-model decisions separately from GPU versus
CPU speed. Hardware acceleration should preserve the method's answer.

## The product story this supports

Proposed hero: **Know when to look.** Follow with a short explanation of the
observation budget, the evolving specimen estimate, and the evidence reveal.
Keep the existing chalk/charcoal/oxide visual language.

The main experience should show an acquired specimen, a model becoming less reliable,
the recorded reason to acquire, and the measured correction. Until calibration exists,
the display must say heuristic uncertainty rather than probability of being right.
A timeline/budget control should expose actual saved conditions. The hero can use
illustration, but specimen geometry and scientific evidence must retain provenance.

For the challenge explanation, answer four questions with artifacts: what specific
resource is recent, what computation it performs, what breaks or changes when it is
removed, and what difficult integration problem we solved. Numerical parity, causal
isolation, transport overhead, and model error are real engineering stories. Mixed
results can remain central; a failing accuracy benchmark does not automatically make
a technology irrelevant, nor does novelty establish an accuracy gain.

Current facts must remain explicit: offline replay; no measured health benefit;
fixed wins the existing event audit; proposed improvements have not run. Strong
presentation comes from making the actual mechanism and evidence understandable.

## Execution recommendation and session evidence

1. Review this brief and plan the frontend narrative on Astra.
2. Let the current Phase 5 runner finish all stages, then review actual outputs.
3. Authorize/register one bounded scientific increment, starting with Gate A.
4. Implement the selected frontend plan with Sol Medium. Use Sol High for substantial
   scientific/numerical implementation when required by AGENTS.md.

During this research session, PID55068 remained present. The log completed the
s2/B89 first-pass score and advanced into the next group to t75/269 while still in
runner step1/5. This is a timestamped-session observation, not a live status claim.
Full independent recomputation and Phase 5 completion were not established.

Only documentation was written. No inference, installation, dataset download,
benchmark, new controller, or image generation was performed. Several publisher
pages required fallbacks to author repositories/preprints; blocked pages were not
treated as read. Research is bounded rather than an exhaustive survey of all releases.

## Authorized follow-up: frontend and development count audit

The user subsequently authorized autonomous implementation while away. The statements
above describe the original research pass. This follow-up adds a frontend introduction
and a lightweight diagnostic; it does not change the frozen science or its results.

`scripts/audit_perception_counts.py` reads saved s1 observation diagnostics and source
MaMuT spot counts at exactly the acquired frames. It rejects evaluation sequences,
missing annotation frames, duplicate spot IDs, and observation/schedule mismatches.
It loads no image volumes or model weights and does not run or alter a policy.
Reproduce with `.venv/Scripts/python.exe scripts/audit_perception_counts.py`.
Output: `runs/perception-count-audit/summary.json`, including input SHA256 hashes.

Among 54 saved development acquisitions, 38 have fewer fitted components than
annotated spots, 14 have more, and 2 agree. Median component/spot ratio is 0.6825.

| Source frame | Accepted Gaussian components | Annotated spots | Size-rejected connected regions |
|---|---:|---:|---:|
| 0 | 7 | 2 | 26 |
| 66 | 28 | 28 | 49 |
| 132 | 87 | 132 | 132 |
| 193 | 42 | 338 | 2,109 |
| 260 | 17 | 541 | 1,954 |

This is **not segmentation recall**. Component counts cannot distinguish merged
nuclei, fragmented/noisy signal, missing signal, or annotation coverage. The current
diagnostic combines both sides of the size filter: below 24 voxels and above
1,000,000 voxels. The fixed normalized threshold is 0.1297365. The saved measured
contact sheet visibly retains many nuclei late in the sequence, but it cannot
identify the underlying 3D rejection mechanism.

**Updated priority:** before installing CellposeDINO, audit small versus large
rejections and intensity/background drift on a preselected s1 panel. Separate
detection normalization from the frozen evaluation normalization: any candidate
image-dependent preprocessing must use only an actually acquired image. Then compare
the current detector, a simple instance-separation baseline, and the candidate model.
Do not tune a detector solely to reproduce annotation counts. Spatial correspondence
and representative manual/source-label checks are still necessary.

Four targeted diagnostic tests passed in 0.04 seconds. Pytest reported a cache-write
permission warning; test execution succeeded. This follow-up establishes a reason
to investigate perception; it establishes no gain from a replacement algorithm.
