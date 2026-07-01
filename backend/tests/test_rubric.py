import rubric

def test_seven_categories():
    ids = {c["id"] for c in rubric.CATEGORIES}
    assert ids == {"architecture","functionality","context","model","security","performance","reliability"}

def test_every_check_has_valid_category():
    cat_ids = {c["id"] for c in rubric.CATEGORIES}
    for c in rubric.CHECKS:
        assert c.category in cat_ids
        assert c.severity in {"critical","high","medium","low"}
        assert c.applicability in {"always","use_case"}
        assert c.weight > 0 and c.guidance

def test_check_ids_unique_and_reasonable_count():
    ids = [c.id for c in rubric.CHECKS]
    assert len(ids) == len(set(ids))
    assert len(ids) >= 28

def test_security_has_secrets_check():
    assert any(c.id == "no-hardcoded-secrets" for c in rubric.checks_for("security"))
