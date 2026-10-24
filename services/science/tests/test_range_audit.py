"""Verify selective-download integrity without depending on a remote server."""
import importlib.util
import io
from pathlib import Path
import zipfile

import pytest


spec = importlib.util.spec_from_file_location(
    "mskcc_audit", Path(__file__).resolve().parents[3]/"scripts/audit_mskcc_dataset.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class Response(io.BytesIO):
    def __init__(self, payload, status, content_range):
        super().__init__(payload)
        self.status = status
        self.headers = {"Content-Range": content_range}


def test_remote_zip_can_extract_verified_ranges(monkeypatch, tmp_path):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer,"w",compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("sample/tracks.txt", "known lineage bytes")
    payload = buffer.getvalue()
    def urlopen(request, timeout):
        start,end = map(int,request.headers["Range"].split("=")[1].split("-"))
        return Response(payload[start:end+1],206,f"bytes {start}-{end}/{len(payload)}")
    monkeypatch.setattr(audit.urllib.request,"urlopen",urlopen)
    reader = audit.RangeReader("https://test.invalid/archive.zip",len(payload))
    with zipfile.ZipFile(reader) as z:
        path = audit.cached_entry(z,"sample/tracks.txt",tmp_path)
        assert path.read_text() == "known lineage bytes"
        path.write_text("corrupt")
        with pytest.raises(ValueError,match="integrity"):
            audit.cached_entry(z,"sample/tracks.txt",tmp_path)
    reader.seek(0,2)
    assert reader.read(1) == b""
    reader.seek(0)
    buffer = bytearray(8)
    assert reader.readinto(buffer) == 8
    assert bytes(buffer) == payload[:8]
    with pytest.raises(ValueError,match="Negative"):
        reader.seek(-1)


@pytest.mark.parametrize("status,content_range,payload",[
    (200,"bytes 0-2/10",b"abc"),
    (206,"bytes 1-3/10",b"abc"),
    (206,"bytes 0-2/10",b"ab"),
])
def test_wrong_or_truncated_ranges_are_rejected(monkeypatch,status,content_range,payload):
    monkeypatch.setattr(audit.urllib.request,"urlopen",lambda *a,**k: Response(payload,status,content_range))
    reader = audit.RangeReader("https://test.invalid/archive.zip",10)
    with pytest.raises(ValueError):
        reader.read(3)
    assert reader.tell() == 0
