# Finish Phase 5 without Codex or VS Code

Open **Windows PowerShell from the Start menu** (outside VS Code). Paste:

```powershell
cd C:\Users\gael8\Coding\gator-hack-26

$phase5Job = Start-Process `
  -FilePath (Resolve-Path .venv\Scripts\python.exe).Path `
  -ArgumentList '-u', 'scripts/finish_phase5.py' `
  -WorkingDirectory (Get-Location).Path `
  -WindowStyle Hidden `
  -PassThru

"Phase 5 process ID: $($phase5Job.Id)"
```

This runs all five remaining stages in order:

1. Finish image scoring, reusing completed conditions.
2. Verify saved result accounting and hashes.
3. Independently recompute all image scores and compare exactly (another expensive pass).
4. Generate the report and comparison charts.
5. Generate post-hoc success/failure inspection panels.

It stops on the first failure. It does not download data, refreeze the protocol,
rerun acquisition policies, or refit models. The original scientific scripts are
unchanged. This wrapper has a duplicate-run lock; do not separately start the
individual evaluator at the same time.

**You can close Codex, VS Code and PowerShell after launching.** Keep the laptop
plugged in and prevent sleep while it runs. Shutdown/restart/sleep interrupts work.
The computation may take hours; no reliable remaining-time estimate is available.
Closing memory-heavy apps can help: the previous run encountered low available RAM.

## Check progress later

Open a new Windows PowerShell window:

```powershell
cd C:\Users\gael8\Coding\gator-hack-26
Get-Content runs\phase5-runner\status.json
Get-Content runs\phase5-runner\latest.log -Tail 25 -Wait
```

`status.json` reports the current stage (1–5), process ID and state.
The log contains both progress and errors, and appends across launches.
Ctrl+C stops **watching the log**, not the background job. Initial integrity
checks can take time before scoring messages appear.

- `running`: check the log and process. If Windows was restarted or the process
  was forcibly stopped, this status can be stale.
- `failed`: read the end of the log. Later stages were not launched.
- `finished`: all five commands succeeded. Open `runs/phase5/report.md` and
  `runs/phase5/comparison.png`; inspection panels are in `runs/phase5/cases/`.
  Results still need scientific review; success does not imply PHOTON beats fixed
  sampling. The frozen pause checkpoint and existing frontend export are historical
  snapshots and are not automatically refreshed by this runner.

## Stop or resume

To stop computation deliberately, use the PID in `status.json`:

```powershell
$phase5Status = Get-Content runs\phase5-runner\status.json | ConvertFrom-Json
Get-Process -Id $phase5Status.pid
# After confirming this is the running Python job:
taskkill /PID $phase5Status.pid /T /F
```

This force-stops the job and its child evaluator. Completed scoring groups are
reused on restart; an interrupted group starts over. The full recomputation
stage currently restarts from the beginning on each launch. Run the original
start block again after checking that no old evaluator is still running.
Do not restart the runner after `finished` unless you intend another expensive
verification pass.

To preview the five commands without doing any computation:

```powershell
.venv\Scripts\python.exe scripts/finish_phase5.py --dry-run
```

The runner does not mark Phase 5 complete or regenerate the Glimpse frontend.
Return with the log/results for review and a frontend-results refresh afterward.
