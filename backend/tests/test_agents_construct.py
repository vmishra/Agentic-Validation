def test_research_agent_only_has_google_search():
    from agents.research import build_research_agent
    a = build_research_agent()
    assert a.output_key == "research_notes"
    assert len(a.tools) == 1  # google_search only (ADK constraint)

def test_build_all_auditors_count():
    from agents.auditors import build_all_auditors
    aud = build_all_auditors()
    assert len(aud) == 7
    assert all(a.output_schema is not None and not a.tools for a in aud)  # single schema agents, no tool loop
    assert len(build_all_auditors(spec_provided=True)) == 8       # + requirements auditor
    assert len(build_all_auditors(["security", "model"])) == 2     # category filter

def test_synthesizer_has_schema_no_tools():
    from agents.synthesizer import build_synthesizer
    s = build_synthesizer()
    assert s.output_schema is not None
    assert not s.tools  # output_schema cannot mix with tools
