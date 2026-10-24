"""Orchestration checks only; never start the expensive scientific evaluation."""
import importlib.util
import io
from pathlib import Path
from types import SimpleNamespace


spec = importlib.util.spec_from_file_location("finish_phase5", Path(__file__).resolve().parents[2] / "scripts/finish_phase5.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def test_runs_all_five_stages_in_order(monkeypatch, tmp_path):
    calls, states = [], []
    def execute(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(runner.subprocess, "run", execute)
    log = io.StringIO()
    assert runner.run_steps(tmp_path, "python with spaces.exe", log, lambda *args: states.append(args)) == 0
    assert [call[0][2:] for call in calls] == [list(step[1:]) for step in runner.STEPS]
    assert all(call[0][0] == "python with spaces.exe" and call[1]["cwd"] == tmp_path for call in calls)
    assert states[-1][0] == "finished"
    assert "FINISHED" in log.getvalue()


def test_first_failure_prevents_all_later_stages(monkeypatch, tmp_path):
    calls, states = [], []
    def execute(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=7 if len(calls) == 2 else 0)
    monkeypatch.setattr(runner.subprocess, "run", execute)
    log = io.StringIO()
    assert runner.run_steps(tmp_path, "python.exe", log, lambda *args: states.append(args)) == 7
    assert len(calls) == 2
    assert states[-1][:2] == ("failed", 2)
    assert "Later stages were not started" in log.getvalue()


def test_dry_run_creates_nothing_and_starts_nothing(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner.sys, "argv", ["finish_phase5.py", "--dry-run"])
    def forbidden(*args, **kwargs):
        raise AssertionError("Dry run must not launch a process")
    monkeypatch.setattr(runner.subprocess, "run", forbidden)
    assert runner.main() == 0
    assert len(capsys.readouterr().out.splitlines()) == 5
    assert list(tmp_path.iterdir()) == []
