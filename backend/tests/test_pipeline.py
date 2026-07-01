import pipeline, schemas

def test_collect_findings_from_state():
    state = {
        "findings_security": {"category": "security", "findings": [
            {"id":"no-hardcoded-secrets","category":"security","title":"No secrets",
             "status":"missing","severity":"critical","evidence":"c.py:1 — ***",
             "why":"leak","recommendation":"env","pattern":"secret-mgmt",
             "applicability":"always","weight":3}]},
    }
    findings = pipeline._collect_findings(state)
    assert findings and findings[0].id == "no-hardcoded-secrets"

def test_synthesis_from_state_handles_missing():
    syn = pipeline._synthesis({})
    assert isinstance(syn, schemas.SynthesisOutput)
