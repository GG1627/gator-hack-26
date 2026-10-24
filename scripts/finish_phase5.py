"""Run the remaining frozen Phase 5 stages; never acquire, fit, or refreeze."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
STEPS = (
    ("Resume image scoring", "scripts/run_phase5.py", "evaluate"),
    ("Verify result ledgers", "scripts/run_phase5.py", "verify"),
    ("Recompute and compare all source scores", "scripts/run_phase5.py", "evaluate", "--recompute"),
    ("Build report and comparison charts", "scripts/report_phase5.py"),
    ("Build post-hoc failure panels", "scripts/inspect_phase5_failures.py"),
)


def run_steps(root, python, log, update):
    for number, (label, *arguments) in enumerate(STEPS, 1):
        update("running", number, label)
        log.write(f"\n[{datetime.now().astimezone().isoformat()}] STEP {number}/{len(STEPS)}: {label}\n")
        log.flush()
        result = subprocess.run([str(python), "-u", *arguments], cwd=root,
                                stdout=log, stderr=subprocess.STDOUT, check=False)
        if result.returncode:
            update("failed", number, label, result.returncode)
            log.write(f"\nSTOPPED: step {number} exited {result.returncode}. Later stages were not started.\n")
            log.flush()
            return result.returncode
    update("finished", len(STEPS), "All runner stages finished; inspect results before declaring Phase 5 complete")
    log.write("\nFINISHED: all five stages exited successfully. Scientific results still require review.\n")
    log.flush()
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print commands without creating files or starting evaluation")
    args = parser.parse_args()
    if args.dry_run:
        for label, *arguments in STEPS:
            print(f"{label}: {subprocess.list2cmdline([sys.executable, '-u', *arguments])}")
        return 0

    # Windows byte-range locks are released by the OS when this process exits.
    # Keep the lock file: deleting it would allow two processes to lock different files.
    if sys.platform != "win32":
        parser.error("This background runner is for Windows; use the individual commands on other systems.")
    import msvcrt
    import os

    folder = ROOT / "runs/phase5-runner"
    folder.mkdir(parents=True, exist_ok=True)
    lock = (folder / "runner.lock").open("a+b")
    try:
        if lock.seek(0, 2) == 0:
            lock.write(b"0")
            lock.flush()
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            print("A Phase 5 runner is already active. No second evaluation was started.", file=sys.stderr)
            return 1

        def update(state, step, label, exit_code=None):
            value = dict(state=state, pid=os.getpid(), step=step, total_steps=len(STEPS),
                         label=label, updated_at=datetime.now().astimezone().isoformat(),
                         log=str(folder / "latest.log"), exit_code=exit_code)
            temp = folder / "status.tmp"
            temp.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
            temp.replace(folder / "status.json")

        with (folder / "latest.log").open("a", encoding="utf-8", buffering=1) as log:
            log.write(f"\n=== Phase 5 runner started {datetime.now().astimezone().isoformat()} PID {os.getpid()} ===\n")
            print(f"Progress: {folder / 'latest.log'}", flush=True)
            try:
                return run_steps(ROOT, sys.executable, log, update)
            except Exception as error:
                update("failed", None, str(error), 1)
                log.write(f"\nRUNNER ERROR: {error!r}\n")
                return 1
    finally:
        lock.close()


if __name__ == "__main__":
    raise SystemExit(main())
