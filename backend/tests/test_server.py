from fastapi.testclient import TestClient
import server

client = TestClient(server.app)

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["model"] == server.config.MODEL

def test_scan_registers_github_source():
    r = client.post("/api/scan", json={"githubUrl": "https://github.com/x/y", "useCase": "demo"})
    assert r.status_code == 200
    sid = r.json()["scanId"]
    assert sid in server.SCANS
    assert server.SCANS[sid]["source"]["kind"] == "github"

def test_scan_registers_categories_and_spec():
    r = client.post("/api/scan", json={"githubUrl": "https://github.com/x/y",
                                        "categories": ["security", "performance"], "spec": "- must log"})
    e = server.SCANS[r.json()["scanId"]]
    assert e["categories"] == ["security", "performance"] and e["spec"] == "- must log"

def test_history_persist_list_and_load(tmp_path, monkeypatch):
    monkeypatch.setattr(server.config, "HISTORY_DIR", tmp_path)
    rep = {"scan_id": "hx1", "source": {"kind": "github", "url": "https://github.com/a/b"},
           "framework": {"primary": "google-adk"}, "overall": 0.5, "band": {"label": "Developing"},
           "use_case": "demo", "generated_at": "2026-06-30T00:00:00Z", "categories": [], "findings": []}
    server._persist(rep)
    assert server._load_report("hx1")["scan_id"] == "hx1"     # disk fallback (not in memory)
    listed = server.list_scans()
    assert any(s["scanId"] == "hx1" and s["label"].endswith("a/b") for s in listed)

def test_report_404_before_done():
    r = client.post("/api/scan", json={"githubUrl": "https://github.com/x/y"})
    sid = r.json()["scanId"]
    assert client.get(f"/api/scan/{sid}/report").status_code == 404
