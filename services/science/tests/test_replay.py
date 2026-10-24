from dataclasses import fields
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest
import tifffile

from photon.audit import audit_lineage
from photon.data import load_sequence, SequenceMetadata
from photon.oracle import ReplayOracle
from photon.policy import ScheduledPolicy
from photon.replay import run_replay, RunRecord


@pytest.fixture
def sequence(tmp_path):
    folder = tmp_path / "01"
    folder.mkdir()
    for t in range(7):
        tifffile.imwrite(folder / f"t{t:03}.tif", np.full((3, 8, 8), t, dtype=np.uint16), photometric="minisblack")
    return load_sequence(folder, dataset_id="synthetic-test", source="synthetic")


@pytest.mark.parametrize("total", [1, 2, 7, 19])
def test_exact_budget_schedules(total):
    meta = SequenceMetadata("fixture", "01", total, (8, 8), "uint16")
    for budget in range(1, total+1):
        for name in ("fixed_interval", "seeded_random"):
            a, b = ScheduledPolicy(name), ScheduledPolicy(name)
            a.reset(meta, budget, 42)
            b.reset(meta, budget, 42)
            assert a.indices == b.indices
            assert len(a.indices) == budget and 0 in a.indices
            assert all(0 <= t < total for t in a.indices)
    for bad in (0, -1, total+1, 1.5, True):
        with pytest.raises(ValueError):
            ScheduledPolicy("fixed_interval").reset(meta, bad, 42)


def test_oracle_clock_budget_and_completion(sequence):
    oracle = ReplayOracle(sequence, 1)
    with pytest.raises(ValueError):
        oracle.acquire(0)
    with pytest.raises(ValueError):
        oracle.advance(1)
    with pytest.raises(ValueError):
        oracle.evaluate_after_run(RunRecord("fixed_interval", 42, 1, (0,), ()))
    oracle.advance(0)
    for forbidden in (1, -1):
        with pytest.raises(ValueError):
            oracle.acquire(forbidden)
    observed = oracle.acquire(0)
    assert not observed.pixels.flags.writeable
    with pytest.raises(ValueError):
        oracle.acquire(0)
    with pytest.raises(ValueError):
        oracle.finish()
    oracle.advance(1)
    with pytest.raises(ValueError):
        oracle.acquire(1)
    for t in range(2, 7):
        oracle.advance(t)
    assert oracle.finish() == (0,)
    with pytest.raises(ValueError):
        oracle.acquire(6)


def test_policy_allowed_api_has_only_past(sequence, tmp_path):
    class InspectingPolicy(ScheduledPolicy):
        def reset(self, metadata, budget, seed):
            assert {f.name for f in fields(metadata)} == {
                "dataset_id", "sequence_id", "frame_count", "shape", "dtype", "source", "split",
                "frame_interval_minutes", "voxel_size_xyz_um"}
            assert not hasattr(metadata, "read") and not hasattr(metadata, "annotations")
            super().reset(metadata, budget, seed)

        def decide(self, t, past_observations):
            assert all(frame.index < t for frame in past_observations)
            assert not hasattr(self, "oracle")
            return super().decide(t, past_observations)
    run_replay(sequence, InspectingPolicy("fixed_interval"), 3, 42, tmp_path/"isolated")


def test_exports_match_oracle_trace(sequence, tmp_path):
    for name in ("fixed_interval", "seeded_random"):
        output = tmp_path/name
        record = run_replay(sequence, ScheduledPolicy(name), 3, 17, output)
        config = json.loads((output/"config.json").read_text())
        trace = [json.loads(line) for line in (output/"decisions.jsonl").read_text().splitlines()]
        metrics = json.loads((output/"metrics.json").read_text())
        assert [d["t"] for d in trace if d["decision"] == "ACQUIRE"] == list(record.acquired_indices) == config["acquired_indices"]
        assert metrics["acquisitions"] == 3 and metrics["relative_exposure_proxy"] == 3/7
        assert len(config["withheld_indices"]) == 4
        assert len(config["photon_code_sha256"]) == 64
        assert config["replay_mode"] == "retrospective_source_time_replay"
        assert metrics["event_coverage"] is None
        assert (output/"observed.png").exists()
        with pytest.raises(ValueError, match="exists"):
            run_replay(sequence, ScheduledPolicy(name), 3, 17, output)


def test_only_acquisitions_read_pixels_and_future_changes_do_not_change_decisions(sequence, tmp_path):
    original_read = sequence.read
    reads = []
    def read(t):
        reads.append(t)
        return original_read(t)
    sequence.read = read
    first = run_replay(sequence, ScheduledPolicy("seeded_random"), 3, 9, tmp_path/"first")
    assert reads == list(first.acquired_indices)
    for path in sequence.paths[1:]:
        tifffile.imwrite(path, np.full((3, 8, 8), 500, dtype=np.uint16), photometric="minisblack")
    second = run_replay(sequence, ScheduledPolicy("seeded_random"), 3, 9, tmp_path/"second")
    assert first.decisions == second.decisions


def test_tiff_failures(tmp_path):
    with pytest.raises(ValueError, match="No CTC"):
        load_sequence(tmp_path)
    (tmp_path/"t000.tif").write_text("not a TIFF")
    with pytest.raises(ValueError, match="Cannot read TIFF"):
        load_sequence(tmp_path)
    tifffile.imwrite(tmp_path/"t000.tif", np.zeros((8, 8), dtype=np.uint8))
    tifffile.imwrite(tmp_path/"t002.tif", np.zeros((8, 8), dtype=np.uint8))
    with pytest.raises(ValueError, match="Missing"):
        load_sequence(tmp_path)
    (tmp_path/"t002.tif").rename(tmp_path/"t001.tif")
    tifffile.imwrite(tmp_path/"t001.tif", np.zeros((9, 9), dtype=np.uint8))
    with pytest.raises(ValueError, match="Inconsistent"):
        load_sequence(tmp_path)
    (tmp_path/"t001.tif").unlink()
    tifffile.imwrite(tmp_path/"t000.tif", np.zeros((2, 3, 4, 5), dtype=np.uint8), photometric="minisblack")
    with pytest.raises(ValueError, match="Unsupported"):
        load_sequence(tmp_path)


def test_lineage_audit(tmp_path):
    file = tmp_path/"man_track.txt"
    assert audit_lineage(file, 7)["available"] is False
    file.write_text("1 0 2 0\n2 3 6 1\n3 3 6 1\n")
    audit = audit_lineage(file, 7)
    assert audit["binary_divisions"] == 1 and audit["division_times"] == [3]
    file.write_text("1 0 2 0\n2 3 6 99\n")
    with pytest.raises(ValueError, match="parent"):
        audit_lineage(file, 7)


def test_cli_comparison_on_download_free_fixture(sequence, tmp_path):
    root = Path(__file__).resolve().parents[3]
    output = tmp_path/"comparison"
    command = [sys.executable, str(root/"scripts/run_experiment.py"), "--sequence", str(sequence.paths[0].parent),
               "--dataset-id", "synthetic-test", "--source", "synthetic", "--budget", "3", "--output", str(output)]
    subprocess.run(command, check=True, capture_output=True, text=True)
    for name in ("fixed_interval", "seeded_random"):
        config = json.loads((output/name/"config.json").read_text())
        assert config["source"] == "synthetic" and len(config["acquired_indices"]) == 3


def test_rgb_rejected(tmp_path):
    tifffile.imwrite(tmp_path/"t000.tif", np.zeros((8, 8, 3), dtype=np.uint8), photometric="rgb")
    with pytest.raises(ValueError, match="Multichannel"):
        load_sequence(tmp_path)


def test_oracle_rejects_mismatched_record(sequence):
    oracle = ReplayOracle(sequence, 1)
    for t in range(7):
        oracle.advance(t)
        if t == 0:
            oracle.acquire(t)
    oracle.finish()
    with pytest.raises(ValueError, match="matching"):
        oracle.evaluate_after_run(RunRecord("fixed_interval", 42, 1, (6,), ()))


@pytest.mark.parametrize("budget", [1, 7])
def test_boundary_budgets_end_to_end(sequence, tmp_path, budget):
    for name in ("fixed_interval", "seeded_random"):
        record = run_replay(sequence, ScheduledPolicy(name), budget, 42, tmp_path/f"{name}-{budget}")
        assert len(record.acquired_indices) == budget
        assert record.acquired_indices[0] == 0
