import io, zipfile, pytest
import ingest

def _zip_bytes(files: dict[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, content in files.items():
            z.writestr(name, content)
    return buf.getvalue()

def test_ingest_zip_extracts(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest.config, "SCAN_ROOT", tmp_path)
    ws = ingest.ingest_zip(_zip_bytes({"agent.py": "print(1)"}), "s1")
    assert (ws / "agent.py").read_text() == "print(1)"

def test_ingest_zip_rejects_zip_slip(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest.config, "SCAN_ROOT", tmp_path)
    with pytest.raises(ingest.IngestError):
        ingest.ingest_zip(_zip_bytes({"../evil.py": "x"}), "s2")

def test_ingest_folder_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest.config, "SCAN_ROOT", tmp_path)
    with pytest.raises(ingest.IngestError):
        ingest.ingest_folder(str(tmp_path / "nope"), "s3")

def test_ingest_folder_copies(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest.config, "SCAN_ROOT", tmp_path)
    src = tmp_path / "proj"; src.mkdir(); (src / "a.py").write_text("x")
    ws = ingest.ingest_folder(str(src), "s4")
    assert (ws / "a.py").read_text() == "x"
