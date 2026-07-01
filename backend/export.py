"""Render a ValidationReport to Markdown / JSON for reuse."""
from __future__ import annotations
from schemas import ValidationReport

def to_json(report: ValidationReport) -> str:
    return report.model_dump_json(indent=2)

def to_markdown(report: ValidationReport) -> str:
    L = []
    L.append("# Agentic Validation Report")
    L.append("")
    L.append(f"- **Source:** {report.source}")
    L.append(f"- **Framework:** {report.framework.get('primary','?')}")
    if report.use_case:
        L.append(f"- **Use case:** {report.use_case}")
    pct = round(report.overall * 100)
    L.append(f"- **Overall readiness:** {pct}% — {report.band.get('label','')}")
    L.append(f"- **Scanned:** {report.scanned_files} files · {report.loc} LOC")
    L.append("")
    L.append(f"_{report.summary}_")
    if report.use_case_fit:
        L.append("")
        L.append(f"**Use-case fit:** {report.use_case_fit}")
    L.append("")
    L.append("## Category scores")
    for c in report.categories:
        L.append(f"- **{c.label}** — {round(c.score*100)}% ({c.present}/{c.total} present)")
    L.append("")
    L.append("## Findings")
    for c in report.categories:
        L.append(f"### {c.label}")
        for f in [x for x in report.findings if x.category == c.id and x.included]:
            mark = {"present":"✅","partial":"🟡","missing":"❌"}[f.status]
            ref = f" `{f.location}`" if f.location else ""
            L.append(f"- {mark} **{f.title}** ({f.severity}){ref} — {f.evidence}")
            L.append(f"  - _Why:_ {f.why}")
            if f.recommendation:
                L.append(f"  - _Fix:_ {f.recommendation}")
            if f.sources:
                srcs = ", ".join(f"[{s.title or 'src'}]({s.uri})" for s in f.sources)
                L.append(f"  - _Sources:_ {srcs}")
        L.append("")
    return "\n".join(L)
