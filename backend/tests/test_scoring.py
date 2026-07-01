import scoring, schemas

def _f(id, cat, status, weight=1, sev="medium", appl="always"):
    return schemas.Finding(id=id, category=cat, title=id, status=status, severity=sev,
                           evidence="x", why="y", pattern="p", applicability=appl, weight=weight)

def test_band_thresholds():
    assert scoring.band_for(0.9)["label"] == "Production-ready"
    assert scoring.band_for(0.7)["label"] == "Solid, minor gaps"
    assert scoring.band_for(0.5)["label"] == "Developing"
    assert scoring.band_for(0.2)["label"] == "Needs significant work"

def test_score_category_weighted():
    fs = [_f("a","security","present",weight=3), _f("b","security","missing",weight=1)]
    cs = scoring.score_category(fs, "security")
    assert abs(cs.score - 0.75) < 1e-6
    assert cs.present == 1 and cs.missing == 1 and cs.total == 2

def test_assemble_report_respects_category_filter():
    fs = [_f("a", "security", "present", weight=1), _f("b", "performance", "missing", weight=1)]
    rep = scoring.assemble_report("s", {"kind": "folder"}, None, schemas.EvidencePack(),
                                  fs, schemas.SynthesisOutput(), None, ["security"])
    assert {c.id for c in rep.categories} == {"security"}
    assert rep.overall == 1.0  # only the present security finding counts

def test_requirements_category_label():
    fs = [_f("r1", "requirements", "missing", weight=2, appl="use_case")]
    rep = scoring.assemble_report("s", {"kind": "folder"}, None, schemas.EvidencePack(),
                                  fs, schemas.SynthesisOutput(), None, ["requirements"])
    assert rep.categories[0].label == "Custom Requirements"

def test_excluded_findings_dropped_from_score():
    fs = [_f("a","security","present",weight=1), _f("b","security","missing",weight=1,appl="use_case")]
    fs[1].included = False
    cs = scoring.score_category(fs, "security")
    assert cs.score == 1.0 and cs.total == 1
