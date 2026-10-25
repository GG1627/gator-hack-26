import importlib.util
import json
from pathlib import Path
import zipfile
import pytest

spec=importlib.util.spec_from_file_location("perception_verifier",Path(__file__).parents[1]/"scripts/verify_perception_ablation.py")
verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)


def registered_fixture(folder):
    source=verifier.ROOT/"README.md"
    protocol={"source_sha256":{"README.md":verifier.digest(source)}}
    (folder/"protocol.json").write_text(json.dumps(protocol))
    with zipfile.ZipFile(folder/"source.zip","w") as archive: archive.write(source,"README.md")
    (folder/"registration.json").write_text(json.dumps({"protocol_sha256":verifier.digest(folder/"protocol.json"),
        "source_zip_sha256":verifier.digest(folder/"source.zip")}))
    return protocol


def test_registered_current_and_archived_source_must_agree(tmp_path):
    protocol=registered_fixture(tmp_path)
    assert verifier.verify_registry(tmp_path)==protocol
    # A byte-level change is caught even if the altered archive is still valid ZIP.
    with zipfile.ZipFile(tmp_path/"source.zip","a") as archive: archive.writestr("extra.txt","changed")
    with pytest.raises(ValueError,match="archive hash"):
        verifier.verify_registry(tmp_path)


def test_protocol_byte_change_is_rejected(tmp_path):
    registered_fixture(tmp_path)
    path=tmp_path/"protocol.json";path.write_text(path.read_text()+" ")
    with pytest.raises(ValueError,match="Protocol hash"):
        verifier.verify_registry(tmp_path)


def test_verification_cannot_start_on_an_active_acquisition(tmp_path):
    (tmp_path/"status.json").write_text(json.dumps({"state":"running","stage":"acquisition"}))
    with pytest.raises(ValueError,match="must finish"):
        verifier.verify(tmp_path)


def test_supplement_cannot_be_backdated_after_completion(tmp_path):
    (tmp_path/"status.json").write_text(json.dumps({"state":"complete","stage":"first_pass_complete"}))
    with pytest.raises(ValueError,match="requires the acquisition stage"):
        verifier.register_labels(tmp_path)
