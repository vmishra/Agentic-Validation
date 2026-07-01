import pathlib
import indexer

FIX = pathlib.Path(__file__).parent / "fixtures" / "adk_repo"

def test_read_files_skips_ignored(tmp_path):
    (tmp_path / "node_modules").mkdir(); (tmp_path / "node_modules" / "x.js").write_text("nope")
    (tmp_path / "a.py").write_text("ok")
    files = indexer.read_files(tmp_path)
    assert "a.py" in files and not any("node_modules" in k for k in files)

def test_read_files_handles_hidden_and_binary(tmp_path):
    (tmp_path / ".env.example").write_text("GEMINI_API_KEY=")
    (tmp_path / "a.py").write_text("x")
    (tmp_path / "blob.dat").write_bytes(b"\x00\x01\x02 binary junk")
    files = indexer.read_files(tmp_path)
    assert ".env.example" in files        # hidden text file is scanned
    assert "a.py" in files
    assert "blob.dat" not in files        # binary skipped by NUL sniff

def test_skips_lockfiles_and_minified(tmp_path):
    (tmp_path / "package-lock.json").write_text('{"big":"lock"}')
    (tmp_path / "app.min.js").write_text("var a=1")
    (tmp_path / "main.py").write_text("x")
    files = indexer.read_files(tmp_path)
    assert "main.py" in files
    assert "package-lock.json" not in files and "app.min.js" not in files

def test_compact_evidence_is_bounded_json():
    import json
    ev = indexer.build_evidence(FIX)
    s = indexer.compact_evidence(ev, max_chars=20000)
    d = json.loads(s)
    assert d["framework"]["primary"] == "google-adk"
    assert len(s) <= 20000

def test_build_evidence_detects_framework():
    ev = indexer.build_evidence(FIX)
    assert ev.framework["primary"] == "google-adk"
    assert ev.file_count >= 1
    assert any(s["name"] == "gemini-3.5-flash" for s in ev.signals.get("model_ids", []))
