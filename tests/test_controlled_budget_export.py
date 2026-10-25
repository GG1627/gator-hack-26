"""Reject misleading unequal-budget display exports before any assets are written."""
import copy
import gzip
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.export_controlled_budget_demo import EVIDENCE, load_verified_summary, validate_rows
from experiments.controlled.benchmark import make_clip


@pytest.fixture(scope="module")
def sample():
    summary = load_verified_summary(EVIDENCE / "summary.json.gz", EVIDENCE / "verification.json")
    rows = [r for r in summary["rows"] if r["seed"] == 304 and r["condition"] == "precursor"]
    clip, events, _ = make_clip(304, "precursor")
    return rows, clip, events


def test_real_saved_comparison_has_unequal_counts_and_reproducible_metrics(sample):
    rows, clip, events = sample
    validate_rows(rows, clip, events)
    assert {r["name"]: (len(r["run"]["acquired_indices"]), r["metrics"]["covered_events"]) for r in rows} == {
        "adaptive32": (32, 4), "fixed32": (32, 1), "fixed40": (40, 1)}


@pytest.mark.parametrize("tamper", ["budget", "metric", "trace", "source", "duplicate", "out_of_range"])
def test_rejects_tampered_scientific_display_rows(sample, tamper):
    original, clip, events = sample
    rows = copy.deepcopy(original)
    row = next(r for r in rows if r["name"] == "adaptive32")
    if tamper == "budget":
        row["run"]["budget"] = 40
    elif tamper == "metric":
        row["metrics"]["covered_events"] = 3
    elif tamper == "trace":
        row["run"]["decisions"][0]["decision"] = "SKIP"
    elif tamper == "source":
        row["sequence_sha256"] = "0" * 64
    elif tamper == "duplicate":
        rows[1] = copy.deepcopy(rows[0])
    elif tamper == "out_of_range":
        row["run"]["acquired_indices"][-1] = 240
    with pytest.raises(ValueError):
        validate_rows(rows, clip, events)


def test_rejects_changed_portable_evidence_hash(tmp_path):
    summary = json.loads(gzip.decompress((EVIDENCE / "summary.json.gz").read_bytes()))
    summary["rows"][0]["metrics"]["covered_events"] = 999
    changed = tmp_path / "changed.json.gz"
    changed.write_bytes(gzip.compress(json.dumps(summary).encode()))
    with pytest.raises(ValueError, match="hash/verification"):
        load_verified_summary(changed, EVIDENCE / "verification.json")
