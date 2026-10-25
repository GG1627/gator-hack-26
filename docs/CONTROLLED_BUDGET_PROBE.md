# Lower-budget probe — registered 2026-10-25 before execution

Question: can the unchanged morphology-triggered controller keep complete event
coverage with 32 images instead of the current demo's 40?

This is a separate unequal-budget comparison, not a replacement for the original
equal-budget benchmark. Preselect 32 adaptive captures (20% fewer than 40) without
trying alternatives after reading results. Compare fixed32 and fixed40, standard
phase. Retain precursor, abrupt and quiet conditions. Use development seeds 7/42
and prospective seeds 301–306, not the already-inspected 101–105/2026 cohort.
Keep the generator, controller, gaps, 240 frames, and ±1 event tolerance unchanged.
Every schedule must close before scoring. Preserve failures and all seeds.

Run `scripts/probe_controlled_budget.py --output runs/controlled-budget32-v1`.
The run has a 120-second deadline checked by the existing causal runner. No real
microscopy scoring, new health model, controller tuning or demo export is included.
Results apply only to the synthetic model and declared budgets. Longer elapsed
time alone cannot guarantee complete event coverage with fewer acquisitions.
