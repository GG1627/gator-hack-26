# Bounded Phase 3 refinement: development protocol

Written before this experiment's event/reconstruction scores are computed.
Historical s1 schedules and the single Phase 2 failure preview have already been
inspected. This is exploratory development, not preregistered independent testing.
No s2/s3 images or evaluation outcomes may enter this experiment.

- Source: complete MSKCC s1 frames 0..269, original frozen normalization and model.
- Budget54 including frame0, seed42 (no RNG in adaptive variants), min2/max12.
- Five runs: fixed, original PHOTON, pacing only, robust features only, both.
- Pacing: permit threshold-driven captures only while post-action count is at most
  `1 + floor((B-1)*t/(T-1)) + 2`, capped at B. Original feasibility can override
  pacing to satisfy exact budget/gaps; overrides are explicitly logged.
- Robust features: mean of individually clipped elongation scores replaces max;
  median speed from tracks seen at least twice replaces the all-track 75th
  percentile. Split hint unchanged. No parameter grid or threshold search.
- Event coverage: canonical binary divisions, first daughter time, within +/-1
  source frame of any capture; preserve simultaneous events as distinct events.
  This retrospective observation coverage is not detection recall or alert quality.
- Render all withheld forecasts from state saved causally before truth reveal.
  Compare Gaussian forecast, held Gaussian fit (motion ablation), and raw hold-last.
  All use the same first-acquisition normalization/clipping. Metrics use full3D.
- Primary reconstruction comparison: exact intersection of withheld times across
  all five schedules. Also report each policy's own withheld times and their
  different target-set limitation. Foreground is evaluation-only truth signal>0.1,
  identical across estimators/policies for a shared target; report whole volume too.
- Event labels/truth are read only after **all five** oracle runs close. Neither
  predictions nor controller configuration can update after scoring starts.
- Adoption rule: among changed variants with strictly more covered events than
  original and no higher common-target raw hold-last MSE, choose highest coverage,
  then lower raw hold-last MSE, then name. Otherwise retain original. Report all
  Gaussian results, including losses; hold-last quality is used here to isolate
  schedule utility from the known simplified Gaussian appearance error.
- Preserve all artifacts and unsuccessful variants. Unit tests cover mathematical
  metrics, null labels, boundary budgets, pacing overrides, outliers, and causal
  invariance. Recompute saved development metrics and rerun the chosen schedule.
- Stop after this bounded comparison. Phase4 remains unopened; Phase5 must later
  test frozen settings on independent embryos and multiple budgets. No broad
  superiority, biological protection, or validated mitosis prediction claim.
