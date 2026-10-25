# Appearance-preserving forecast: selected probe results

The registered six-target development probe is complete. It produced11 eligible
comparisons: six for original adaptive, five for watershed. Watershed actually acquired
target261, so that one forecast was excluded exactly as registered. Five targets are
shared between the schedules; no replacement targets were selected.

**Negative result:** corrected forecasts have higher full-volume MSE and MAE than
holding the last real image in all11 eligible comparisons. They generally reduce the
large error from direct Gaussian rendering, but do not beat the stronger raw-hold
baseline. This does not support adopting the correction as an accuracy upgrade.

| Target | Schedule | Horizon | Raw-hold MSE | Corrected MSE |
|---|---|---:|---:|---:|
| 133 | Original adaptive | 1 | 0.00159429 | 0.00163951 |
| 133 | Watershed | 1 | 0.00159429 | 0.00163573 |
| 135 | Original adaptive | 3 | 0.00185245 | 0.00204959 |
| 135 | Watershed | 3 | 0.00185245 | 0.00199623 |
| 194 | Original adaptive | 1 | 0.00224593 | 0.00225056 |
| 194 | Watershed | 1 | 0.00224593 | 0.00245776 |
| 196 | Original adaptive | 3 | 0.00299608 | 0.00300699 |
| 196 | Watershed | 3 | 0.00299608 | 0.00427507 |
| 261 | Original adaptive only | 1 | 0.00336953 | 0.00336975 |
| 263 | Original adaptive | 3 | 0.00439799 | 0.00439811 |
| 263 | Watershed | 2 | 0.00393548 | 0.00518678 |

The full JSON retains MAE, direct Gaussian results, actual histories, exclusions and
source hashes. Different schedules can have different last observations/horizons at
the same target. Comparisons among estimators within a schedule use the same history.
This is previously inspected s1 development data, not a generalization claim.

## Evidence and checks

- Artifacts: `runs/appearance-forecast-probe/{protocol,registration,summary,verification}.json`,
  source.zip, report.md, and per-target images showing raw hold/direct Gaussian/
  corrected/ground-truth projections with a common normalization.
- All44 raw-hold and direct-Gaussian scalar checks match the earlier full-run evaluation
  ledger. Source/archive/image hashes, acquisition histories and exclusions passed checks.
- Three controlled implementation tests passed earlier. Corrected volumes have not
  been independently rerendered a second time; the verification scope is stated explicitly.
- The interval from protocol registration to summary was about72.5 seconds, excluding
  initial imports/input checks. This concurrent one-off execution is not a speed benchmark.
- The saved t196 watershed display was inspected. No controller or Phase5 source changed.

Recheck without rerendering volumes:

```powershell
.venv/Scripts/python.exe scripts/verify_appearance_probe.py
```

## Next research priority

Better perception improved Gaussian fitting, yet the controller retained50 of54
acquisition times and gained only one covered division. Preserving texture alone also
failed to beat raw hold. Review motion/association reliability, the meaning of the
uncertainty score, and budget allocation before adding more rendering complexity or
launching another full benchmark. A recent segmentation model remains a candidate
for perception, but would not automatically solve these downstream limitations.
