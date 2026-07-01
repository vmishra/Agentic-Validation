"""Deterministic scoring + report assembly from findings + synthesis."""
from __future__ import annotations
import rubric
from schemas import Finding, CategoryScore, ValidationReport, SynthesisOutput, Overview

STATUS_SCORE = {"present": 1.0, "partial": 0.5, "missing": 0.0}
SEVERITY_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1}

def band_for(overall: float) -> dict:
    if overall >= 0.85: return {"label": "Production-ready", "tone": "success"}
    if overall >= 0.65: return {"label": "Solid, minor gaps", "tone": "accent"}
    if overall >= 0.45: return {"label": "Developing", "tone": "warn"}
    return {"label": "Needs significant work", "tone": "danger"}

def apply_relevance(findings: list[Finding], synthesis: SynthesisOutput, use_case: str | None) -> list[Finding]:
    decided = {d.check_id: d.included for d in synthesis.relevance}
    for f in findings:
        if f.applicability == "use_case":
            if f.id in decided:
                f.included = decided[f.id]
            else:
                f.included = bool(use_case)  # no decision + no use case -> exclude
    return findings

def score_category(findings: list[Finding], cat_id: str) -> CategoryScore:
    cat = rubric.category_meta(cat_id)
    fs = [f for f in findings if f.category == cat_id and f.included]
    wsum = sum(f.weight for f in fs) or 1
    score = sum(STATUS_SCORE[f.status] * f.weight for f in fs) / wsum
    return CategoryScore(
        id=cat_id, label=cat["label"], score=score,
        present=sum(1 for f in fs if f.status == "present"),
        partial=sum(1 for f in fs if f.status == "partial"),
        missing=sum(1 for f in fs if f.status == "missing"),
        total=len(fs),
    )

def _improvement_rank(f: Finding) -> float:
    return SEVERITY_RANK[f.severity] * f.weight + (1 if f.status == "missing" else 0)

def assemble_report(scan_id, source, use_case, evidence, findings, synthesis,
                    overview: Overview | None = None,
                    category_ids: list[str] | None = None) -> ValidationReport:
    findings = apply_relevance(findings, synthesis, use_case)
    ids = category_ids or rubric.category_ids()
    included = [f for f in findings if f.included and f.category in ids]
    categories = [score_category(findings, cid) for cid in ids]
    wsum = sum(f.weight for f in included) or 1
    overall = sum(STATUS_SCORE[f.status] * f.weight for f in included) / wsum
    strengths = sorted([f for f in included if f.status == "present"],
                       key=lambda f: -f.weight)[:5]
    improvements = sorted([f for f in included if f.status != "present"],
                          key=lambda f: -_improvement_rank(f))[:6]
    from datetime import datetime, timezone
    return ValidationReport(
        scan_id=scan_id, source=source, use_case=use_case,
        framework=evidence.framework, overview=overview or Overview(),
        band=band_for(overall), overall=overall,
        categories=categories, findings=findings, strengths=strengths, improvements=improvements,
        use_case_fit=synthesis.use_case_fit, summary=synthesis.summary,
        scanned_files=evidence.file_count, loc=evidence.total_loc,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
