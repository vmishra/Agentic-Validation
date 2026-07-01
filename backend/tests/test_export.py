import json, scoring, schemas, export

def _report():
    f = schemas.Finding(id="no-hardcoded-secrets", category="security", title="No secrets",
                        status="missing", severity="critical", evidence="c.py:1 — ***",
                        why="leak", recommendation="use env", pattern="secret-mgmt",
                        applicability="always", weight=3)
    ev = schemas.EvidencePack(file_count=2, total_loc=10, framework={"primary":"google-adk"})
    syn = schemas.SynthesisOutput(summary="Decent", use_case_fit="fits")
    return scoring.assemble_report("s1", {"kind":"zip"}, "an agent", ev, [f], syn)

def test_markdown_has_title_and_finding():
    md = export.to_markdown(_report())
    assert "# Agentic Validation Report" in md
    assert "No secrets" in md and "use env" in md

def test_json_roundtrips():
    data = json.loads(export.to_json(_report()))
    assert data["scan_id"] == "s1" and "categories" in data
