# Phase 3: causal acquisition controller

**Current deployment:** the bounded [s1 refinement](phase3-refinement-results.md)
selected `paced_robust`; this is now the API/CLI default. Use
`--controller-variant original` for the legacy behavior documented below.
Image-change baseline defaults are unchanged. The new default caps discretionary
capture count at uniform allowance+2 (feasibility may override), averages clipped
component elongation, and uses median speed from tracks observed at least twice.
Selection/quality limits and all ablations are in the measured report; there is
no held-out result yet. The remaining sections preserve the original design and
historical run evidence.

The controller is a deterministic heuristic for allocating a fixed observation
budget. It is not a trained mitosis predictor, calibrated uncertainty model,
optimal information-gain planner, or proof of phototoxicity reduction. It uses
the Phase 2 Gaussian state fitted only from acquired pixels. No labels, source
paths, future images, or post-hoc scores enter policy decisions.

## Score and observation updates

For a candidate time t, let g be the gap from the last acquisition L, R the
remaining budget before this decision, and E=T-1 the final source index.
The desired gap is (E-L)/R when R>0. Gap pressure is g/max(1, desired_gap).
This is an allocation heuristic; terminal coverage is enforced separately.

The default priority is

`0.4 * uncertainty_score + 0.25 * motion_score + 0.55 * event_interest + 0.8 * gap_pressure`

Acquire at priority >=1 when both actions are feasible. Components are:

- `uncertainty_score`: Phase 2 position scale divided by 0.75 micrometers,
  capped at 1. It grows with time without observation; it is not calibrated.
- `motion_score`: 75th-percentile observed track speed times g, divided by
  1 micrometer and capped at 1. This is a linear displacement proxy from the
  current velocity estimate, not a rendered error estimate or motion classifier.
- `event_interest`: max(morphology_hint, split_hint) times exp(-g/6).
  Morphology uses the largest physical Gaussian aspect ratio among current bright
  components, linearly scaled from zero at 1.8 to one at 3.0. Physical covariance
  multiplies voxel covariance by the outer product of ZYX spacing; aspect ratio
  is sqrt(largest/smallest eigenvalue). Split hint is the number of observed
  candidate splits divided by max(1, active_track_count/2), capped at one.
  The hints update only after acquisitions. They are shape/change alerts, not
  probabilities of future mitosis; debris or merged nuclei can trigger them.
- `gap_pressure`: elapsed gap relative to the remaining-budget desired gap.

State updates use the original source-frame time gaps, not acquisition ordinals.
Size/intensity hold as in Phase 2. No Gaussian rendering or image disagreement
map is needed for this scalar controller; it uses meaningful state/uncertainty
features without introducing decorative GPU computation.

The additional `image_change` baseline uses no Gaussian tracks. It fixes intensity
calibration on the first acquisition and measures normalized pixel MAE between
the last two acquired volumes divided by their source-frame gap. Its score is
`0.55 * min(1, change_rate * g / 0.02) + 0.8 * gap_pressure`.
This can react only after a new image reveals a change. It has the same exact
budget and gap feasibility guard as PHOTON, allowing a later ablation of the
Gaussian features. Neither adaptive policy uses RNG; the seed is recorded for
the common experiment schema. Fixed/random baselines keep their Phase 1 meanings.

## Exact-budget and gap feasibility

An acquisition includes a whole source volume. Frame zero is mandatory and counts
within B. Defaults are min_gap=2 and max_gap=12, both integer source-frame units.
Inter-acquisition gaps must lie in that range. At the final time, the age of the
last measurement must be <=max_gap; there is no mandatory last-frame acquisition
or minimum terminal gap. For MSKCC, 12 frames means 15 minutes. If the configuration
is impossible, reset fails before reading any acquired pixels or creating runs.

For a state with last capture L, exactly R captures left, and earliest next
candidate a, R=0 is feasible iff E-L<=max_gap. For R>0, a feasible first future
capture q exists iff this integer interval is nonempty:

`max(L+min_gap, a, E-R*max_gap) <= q <= min(L+max_gap, E-(R-1)*min_gap)`

The lower bound reserves enough captures/terminal coverage to reach the horizon;
the upper bound leaves enough source indices to spend all remaining captures at
the minimum gap. With integer interval gaps and a terminal age from zero through
max_gap, possible final coverage is contiguous, making the intersection necessary
and sufficient. Exhaustive enumeration independently tests this formula on small
complete schedules.

At each decision the policy checks both successors: acquire now (subject to the
current min/max gap) then finish with R-1, or skip and finish with R starting at
t+1. An infeasible action cannot be chosen regardless of score. This prevents
early overspending, impossible final catch-up, and late maximum-gap violations.
Reasons are `mandatory_initial`, `priority_threshold`, `below_priority_threshold`,
`minimum_gap`, `reserve_for_future_coverage`, `max_gap_due`, `exact_budget_deadline`,
or `budget_exhausted`. Both successors being impossible is an explicit error.

Trace score/risk/uncertainty fields are computed **before** observing X[t].
`last_acquired_index_before` and `gap` describe the decision inputs, while
`last_acquired_index` and remaining-budget-after describe its result. The exported
`predicted_risk` is explicitly typed as uncalibrated acquisition priority. It
includes budget/gap pressure and must never be displayed as a biological risk
probability. Reset validates all requested policies before a comparison begins.

## Real development run and known weakness

Run: `runs/mskcc-phase3/`, MSKCC s1 source frames 0..269, B=54, seed42, default
controller/Phase 2 fit settings. All four policies acquired exactly 54 complete
volumes, exposure-count proxy0.2 each. Settings were fixed before this run.

| Policy | Inter-capture gap histogram | Terminal age |
|---|---|---|
| Fixed | 5:49, 6:4 | 0 |
| Seeded random | Range 1..18 (unconstrained Phase 1 baseline) | 0 |
| PHOTON | 2:13, 3:16, 4:12, 5:1, 10:1, 12:10 | 12 |
| Image change | 4:34, 5:9, 6:4, 7:2, 8:2, 10:1, 12:1 | 12 |

PHOTON used many observations early: 43 threshold-triggered captures plus the
initial capture, followed by 10 maximum-gap captures. It made 109 skips to reserve
future coverage. This is a budget-allocation weakness, not evidence that early
frames are scientifically more important. Max-over-component morphology is
sensitive to outliers; motion estimates can reflect tracking mistakes. These
heuristics can keep priority high. No label-driven or error-driven parameter
adjustment was made to produce a favorable trace. Improving allocation requires
development-only investigation and frozen independent-embryo evaluation later.

Fixed/random retain their original schedules; the random baseline is not
constrained to min2/max12. Current comparison establishes equal counts, not equal
gap constraints or an accuracy advantage. Do not infer that a nonuniform schedule
is better. Event coverage and reconstruction losses remain null in Phase 3 runs;
the Phase 2 forecast loss to hold-last remains part of the evidence.

## Replay and verification

`scripts/build_schedule_replay.py` makes an offline 270-step GIF showing fixed
versus PHOTON. It decodes only the union of completed runs' acquired image indices;
each panel at time t displays only its own last measurement at or before t.
Skipped steps explicitly say **held display**. They are not Gaussian predictions
or truth reveals. Per-acquired-image min/max is display-only. Future ticks are
completed-run historical schedules, never policy inputs. A manifest records every
image index read for the animation.

`scripts/verify_adaptive_runs.py` checks counts, decision chronology, remaining
budget, scalar score arithmetic, gap/terminal constraints, source/code versions,
timelines and null quality metrics. Model state and configurations are exported.
Tests independently enumerate feasibility, cover all budgets for short horizons
under multiple gaps and score thresholds, show density responding to an observed
pre-split shape cue on a clearly synthetic fixture, test high uncertainty/empty
scenes/unexpected changes and exercise policy lifecycle errors.

Causal tests spy on source reads and perturb every unacquired frame. PHOTON and
image-change traces remain identical, and only acquisitions read pixels during
replay. A changed next-acquired frame cannot affect its own or earlier decisions;
only subsequent decisions react. Separate animation tests verify its read indices
and panel pixels against each policy's own past measurements. This is supported
API isolation, not a security sandbox for malicious Python code.

Phase 4 scientific CUDA work and Phase 5 quality/event comparisons remain separate
gates. No GPU speedup, calibrated event detection, favorable accuracy result or
biological light-damage reduction is claimed by this scheduling experiment.
