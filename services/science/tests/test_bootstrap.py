import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from photon.schemas import ObservedFrame, PredictedFrame
from photon.synthetic import make_synthetic_clip


ROOT = Path(__file__).resolve().parents[3]


def test_synthetic_clip_reproducible_and_valid():
    clip = make_synthetic_clip(42)
    assert clip.shape == (8, 32, 32)
    assert clip.dtype == np.float32
    assert np.isfinite(clip).all()
    assert 0 <= clip.min() <= clip.max() <= 1
    np.testing.assert_array_equal(clip, make_synthetic_clip(42))
    assert not np.array_equal(clip, make_synthetic_clip(43))
    # Initial nucleus drifts, and the final frame has separated daughters.
    assert np.argmax(clip[0, 16]) == 12
    assert clip[-1, 12, 16] > clip[-1, 16, 16]
    assert clip[-1, 20, 16] > clip[-1, 16, 16]


def test_observed_and_predicted_tags_are_distinct():
    pixels = make_synthetic_clip()[0]
    observed = ObservedFrame(0, pixels, source="synthetic")
    predicted = PredictedFrame(1, pixels.copy(), (0,), uncertainty=1.0)
    assert observed.kind == "MEASURED"
    assert observed.source == "synthetic"
    assert predicted.kind == "PREDICTED"
    assert predicted.based_on_indices == (0,)


def test_cli_help_and_fixture_roundtrip(tmp_path):
    script = ROOT / "scripts/run_experiment.py"
    help_result = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True, check=True)
    assert "synthetic" in help_result.stdout
    output = tmp_path / "clip.npz"
    command = [sys.executable, str(script), "--synthetic-output", str(output), "--seed", "7"]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    assert json.loads(result.stdout)["source"] == "synthetic"
    with np.load(output, allow_pickle=False) as artifact:
        np.testing.assert_array_equal(artifact["frames"], make_synthetic_clip(7))
        assert json.loads(str(artifact["metadata"]))["seed"] == 7
    assert subprocess.run(command, capture_output=True).returncode != 0
