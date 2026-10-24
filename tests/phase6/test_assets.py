"""Viewer tests live outside the frozen Phase 5 scientific tests."""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("phase6_assets", ROOT / "scripts/build_phase6_assets.py")
assets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assets)


def closed_fixture(folder):
    folder.mkdir()
    assets.write(folder / "config.json", {"frame_count": 4, "budget": 2, "acquired_indices": [0, 3]})
    (folder / "decisions.jsonl").write_text("\n".join(json.dumps({"t": t, "decision": "ACQUIRE" if t in (0, 3) else "SKIP"}) for t in range(4)))
    assets.write(folder / "closed.json", {"closed": True, "files": {name: assets.sha(folder / name) for name in ("config.json", "decisions.jsonl")}})


def test_rejects_open_and_tampered_runs_before_export(tmp_path):
    folder = tmp_path / "run"
    closed_fixture(folder)
    config, trace = assets.validate_run(folder)
    assert config["acquired_indices"] == [0, 3]
    assert len(trace) == 4
    (folder / "decisions.jsonl").write_text('{}')
    with pytest.raises(ValueError, match="hash differs"):
        assets.validate_run(folder)
    assets.write(folder / "closed.json", {"closed": False})
    with pytest.raises(ValueError, match="not closed"):
        assets.validate_run(folder)


def test_trace_mismatch_rejected_even_with_valid_file_hashes(tmp_path):
    folder = tmp_path / "run"
    closed_fixture(folder)
    config = assets.read(folder / "config.json")
    config["acquired_indices"] = [0, 2]
    assets.write(folder / "config.json", config)
    closed = assets.read(folder / "closed.json")
    closed["files"]["config.json"] = assets.sha(folder / "config.json")
    assets.write(folder / "closed.json", closed)
    with pytest.raises(ValueError, match="count/indices"):
        assets.validate_run(folder)


def test_projection_is_max_of_normalized_3d_not_refitted_2d_scene():
    volume = np.array([[[0, .2], [.4, 2]], [[.8, .1], [.3, 0]]])
    np.testing.assert_array_equal(assets.projection(volume), [[204, 51], [102, 255]])


def test_existing_output_refused_without_mutating_it(tmp_path):
    marker = tmp_path / "keep.txt"
    marker.write_text("preserved")
    with pytest.raises(ValueError, match="Output exists"):
        assets.build(tmp_path / "absent", tmp_path / "absent", tmp_path)
    assert marker.read_text() == "preserved"


@pytest.mark.skipif(not (ROOT / "apps/web/public/demo/manifest.json").exists(), reason="Authentic local export not available")
def test_authentic_export_matches_all_saved_runs_and_checkpoint():
    output = ROOT / "apps/web/public/demo"
    manifest = assets.read(output / "manifest.json")
    checkpoint = assets.read(ROOT / "runs/phase5/checkpoint.json")
    approved = {row["condition"] for row in checkpoint["completed_image_conditions"]}
    assert manifest["status"] == "partial" and manifest["phase5_complete"] is False
    assert len(manifest["conditions"]) == 6
    audit = assets.read(ROOT / "runs/phase5/event-audit.json")
    for condition in manifest["conditions"]:
        key = condition["key"]
        run = assets.read(output / condition["replay"])
        evaluation = assets.read(output / condition["evaluation"])
        assert "division_times" not in run and "metrics" not in run
        assert len(run["methods"]) == 6
        for method, entry in run["methods"].items():
            folder = ROOT / "runs/phase5" / key / method
            assert entry["config"] == assets.read(folder / "config.json")
            assert entry["decisions"] == [json.loads(line) for line in (folder / "decisions.jsonl").read_text().splitlines()]
            assert evaluation["methods"][method]["event"] == audit["groups"][key][method]
            if key in approved:
                summary = assets.read(folder.parent / "summary.json")
                assert evaluation["methods"][method]["metrics"] == summary["variants"][method]
            else:
                assert evaluation["methods"][method]["metrics"] is None
                assert evaluation["reason"]
        for t in range(run["frame_count"]):
            assert (output / "images" / run["sequence_id"] / f"{t}.png").exists()
            if t not in run["methods"]["photon"]["config"]["acquired_indices"]:
                assert (output / key / "predictions" / f"{t}.png").exists()
    for name, expected in manifest["source_hashes"].items():
        assert assets.sha(ROOT / name) == assets.sha(output / "sources" / name) == expected
    protocol = assets.read(ROOT / "runs/phase5/protocol.json")
    for name, expected in protocol["implementation_hashes"].items():
        assert assets.sha(ROOT / name) == expected


@pytest.mark.skipif(not (ROOT / "apps/web/public/demo/manifest.json").exists(), reason="Authentic local export not available")
def test_actual_preview_pixels_match_source_volumes_and_saved_3d_geometry():
    from PIL import Image
    from photon.development import load_scenes
    from photon.gaussian import render_gaussians
    import tifffile

    output = ROOT / "apps/web/public/demo"
    sid = "mskcc_confocal_s2"
    config = assets.read(ROOT / f"runs/phase5/{sid}/b54/photon/config.json")
    # Independent projection arithmetic, not a call back into the exporter.
    for t in (1, 269):
        raw = tifffile.imread(ROOT / f"data/mskcc-audit/mskcc-confocal/{sid}/images/{sid}_t{t:03d}.tif")
        normalized = np.clip((raw.astype(np.float32) - config["normalization"]["background"]) / config["normalization"]["scale"], 0, 1)
        expected = np.round(normalized.max(axis=0) * 255).astype(np.uint8)
        np.testing.assert_array_equal(np.asarray(Image.open(output / f"images/{sid}/{t}.png")), expected)
    scenes = load_scenes(ROOT / f"runs/phase5/{sid}/b54/photon/forecasts.npz")
    for t in (1, 268):
        volume = render_gaussians(tuple(config["shape"]), scenes[t])
        expected = np.round(np.clip(volume.max(axis=0), 0, 1) * 255).astype(np.uint8)
        np.testing.assert_array_equal(np.asarray(Image.open(output / f"{sid}/b54/predictions/{t}.png")), expected)
