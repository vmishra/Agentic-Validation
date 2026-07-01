import schemas

def test_finding_defaults():
    f = schemas.Finding(
        id="multi-agent", category="architecture", title="Multi-agent topology",
        status="present", severity="high", evidence="agent.py:10 — 3 agents",
        why="decomposition", pattern="orchestrator-workers", applicability="always", weight=3,
    )
    assert f.included is True and f.sources == []

def test_formatter_schema_roundtrips_json():
    cf = schemas.CategoryFindings.model_validate({
        "category": "security",
        "findings": [{
            "id": "secrets", "category": "security", "title": "No hardcoded secrets",
            "status": "missing", "severity": "critical", "evidence": "config.py:3 — AIza...",
            "why": "leak", "recommendation": "use env", "pattern": "secret-management",
            "applicability": "always", "weight": 3,
        }],
    })
    assert cf.findings[0].status == "missing"

def test_synthesis_output_schema():
    s = schemas.SynthesisOutput(relevance=[], summary="ok", use_case_fit="fits",
                                strength_ids=[], improvement_ids=[])
    assert s.summary == "ok"
