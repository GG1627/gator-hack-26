"""Native 3D data-window and temporal annotation contracts."""
import numpy as np
import pytest
import tifffile

from photon import data
from photon.annotations import audit_mamut


@pytest.fixture
def native_sequence(tmp_path, monkeypatch):
    # Shrink only test geometry/window; production constants remain 270 x 41x512x512.
    monkeypatch.setattr(data,"MSKCC_WINDOW",3)
    monkeypatch.setattr(data,"MSKCC_SHAPE",(2,8,8))
    directory = tmp_path/"mskcc_confocal_s1"
    (directory/"images").mkdir(parents=True)
    for t in range(3):
        tifffile.imwrite(directory/"images"/f"mskcc_confocal_s1_t{t:03}.tif",np.full((2,8,8),t,dtype=np.uint16),photometric="minisblack")
    # Corrupt out-of-window data must not be read or used to normalize the window.
    (directory/"images/mskcc_confocal_s1_t399.tif").write_bytes(b"deliberately invalid")
    return directory


def test_native_metadata_window_and_no_late_reads(native_sequence):
    sequence = data.load_sequence(native_sequence,dataset_id=data.MSKCC_ID)
    assert sequence.metadata.frame_count == 3
    assert sequence.metadata.shape == (2,8,8)
    assert sequence.metadata.split == "development"
    assert sequence.metadata.frame_interval_minutes == 1.25
    assert sequence.metadata.voxel_size_xyz_um == (0.15,0.15,0.75)
    assert sequence.provenance["source_window_inclusive"] == [0,2]
    assert len(sequence.paths) == 3
    assert sequence.read(2).max() == 2


def test_native_missing_frame_is_not_silently_shortened(native_sequence):
    (native_sequence/"images/mskcc_confocal_s1_t001.tif").unlink()
    with pytest.raises(ValueError,match="Missing"):
        data.load_sequence(native_sequence,dataset_id=data.MSKCC_ID)


def test_native_geometry_and_source_must_match(native_sequence):
    for t in range(3):
        tifffile.imwrite(native_sequence/"images"/f"mskcc_confocal_s1_t{t:03}.tif",np.zeros((8,8),dtype=np.uint16))
    with pytest.raises(ValueError,match="MSKCC expected shape"):
        data.load_sequence(native_sequence,dataset_id=data.MSKCC_ID)
    with pytest.raises(ValueError,match="microscopy source"):
        data.load_sequence(native_sequence,dataset_id=data.MSKCC_ID,source="synthetic")


def write_graph(path, spots, edges):
    import xml.etree.ElementTree as ET
    root = ET.Element("TrackMate")
    model = ET.SubElement(root,"Model")
    all_spots = ET.SubElement(model,"AllSpots")
    for sid,frame in spots:
        group = ET.SubElement(all_spots,"SpotsInFrame",frame=str(frame))
        ET.SubElement(group,"Spot",ID=str(sid),FRAME=str(frame))
    tracks = ET.SubElement(model,"AllTracks")
    track = ET.SubElement(tracks,"Track")
    for a,b in edges:
        ET.SubElement(track,"Edge",SPOT_SOURCE_ID=str(a),SPOT_TARGET_ID=str(b))
    ET.ElementTree(root).write(path)


def test_canonical_division_times_and_window_boundary(tmp_path):
    path=tmp_path/"tracks.xml"
    write_graph(path,[(0,0),(1,1),(2,1),(3,2),(4,2)],[(1,0),(0,2),(1,3),(4,1)])
    audit = audit_mamut(path,3)
    assert audit["division_times"] == [1,2]
    assert audit["binary_divisions"] == 2
    assert audit["all_requested_frames_have_annotations"] is True
    # Mother exists inside shorter window, but daughters outside do not count.
    assert audit_mamut(path,2)["division_times"] == [1]
    assert audit_mamut(path,4)["missing_annotation_frames"] == [3]


@pytest.mark.parametrize("spots,edges,expected",[
    ([(0,0),(0,1)],[],"Duplicate"),
    ([(0,0),(1,2)],[(0,1)],"consecutive"),
    ([(0,0),(1,1)],[(0,99)],"missing spot"),
    ([(0,0),(1,0),(2,1)],[(0,2),(1,2)],"Merge"),
    ([(0,0),(1,1),(2,1),(3,1)],[(0,1),(0,2),(0,3)],"Nonbinary"),
    ([(0,0),(1,1)],[(0,1),(0,1)],"Duplicate graph"),
])
def test_bad_lineages_fail_usefully(tmp_path,spots,edges,expected):
    path=tmp_path/"tracks.xml"
    write_graph(path,spots,edges)
    with pytest.raises(ValueError,match=expected):
        audit_mamut(path,3)


def test_missing_or_corrupt_annotations(tmp_path):
    path=tmp_path/"missing.xml"
    assert audit_mamut(path,3)["available"] is False
    path.write_text("not XML")
    with pytest.raises(ValueError,match="Cannot parse"):
        audit_mamut(path,3)


def test_frozen_split_covers_three_embryos():
    assert data.MSKCC_SPLITS == {"mskcc_confocal_s1":"development","mskcc_confocal_s2":"evaluation","mskcc_confocal_s3":"evaluation"}
    assert data.MSKCC_WINDOW == 270
