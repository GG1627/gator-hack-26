"""Validate diagnostic time alignment and prevent misleading missing-data counts."""
import importlib.util
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest

spec = importlib.util.spec_from_file_location("count_audit", Path(__file__).parents[1]/"scripts/audit_perception_counts.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def inputs():
    config = {"sequence_id":"mskcc_confocal_s1", "split":"development", "acquired_indices":[0,2]}
    state = {"observations":[{"t":t, "detection":{"accepted":n,"connected_regions":n+1,"rejected_size":1},"active_tracks":n}
                              for t,n in [(0,2),(2,1)]]}
    root = ET.fromstring('<TrackMate><Model><AllSpots><SpotsInFrame><Spot ID="1" FRAME="0"/><Spot ID="2" FRAME="1"/><Spot ID="3" FRAME="2"/><Spot ID="4" FRAME="2"/></SpotsInFrame></AllSpots></Model></TrackMate>')
    return config,state,root


def test_uses_observed_source_frame_not_next_decision_frame():
    result = module.audit(*inputs())
    assert [row["annotated_spots"] for row in result["rows"]] == [1,2]
    assert result["median_component_to_spot_ratio"] == 1.25
    assert result["fewer_components_than_spots"] == result["more_components_than_spots"] == 1


def test_rejects_held_out_sequence():
    config,state,root = inputs()
    config["sequence_id"] = "mskcc_confocal_s2"
    with pytest.raises(ValueError, match="development"):
        module.audit(config,state,root)


def test_rejects_missing_annotation_frame():
    config,state,root = inputs()
    for spot in root.findall("Model/AllSpots/SpotsInFrame/Spot"):
        if spot.attrib["FRAME"] == "2": spot.attrib["FRAME"] = "3"
    with pytest.raises(ValueError, match="Missing annotation frame"):
        module.audit(config,state,root)


def test_rejects_observation_schedule_mismatch():
    config,state,root = inputs()
    state["observations"][1]["t"] = 1
    with pytest.raises(ValueError, match="schedule"):
        module.audit(config,state,root)
