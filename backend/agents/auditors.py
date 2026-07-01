"""Per-category auditors.

Each category is a SINGLE LlmAgent with output_schema=CategoryFindings that reasons
over the BOUNDED evidence pack (from the deterministic scan) in one call. There is no
per-file tool loop: input size stays constant regardless of repo size, so the validator
scales to large repos, runs fewer calls, and one failing category never blocks the rest.

Static per-agent content (label, checklist, category id) is injected with %-formatting,
which leaves ADK's runtime placeholders ({use_case?}, {spec?}, {research_notes?},
{evidence?}) untouched for the framework to resolve from session state.
"""
from __future__ import annotations
from google.adk.agents import LlmAgent
import config, rubric
from agents._common import gen_config
from schemas import CategoryFindings

def _checklist(checks) -> str:
    return "\n".join(
        f"- id={c.id} | {c.title} | severity={c.severity} | weight={c.weight} | "
        f"applicability={c.applicability} | pattern={c.pattern}\n    guidance: {c.guidance}"
        for c in checks
    )

# %s slots (in order): category label, checklist, category id
AUDITOR_INSTRUCTION = """You audit the "%s" aspect of an AI-agent codebase from a static scan.

Stated use case (may be empty): {use_case?}
Custom requirements / spec (Markdown, may be empty — weigh if relevant): {spec?}
Research notes (grounded via Google Search): {research_notes?}

Evidence pack (deterministic scan as JSON — file tree, detected framework, tools, agents,
orchestration, models, prompts, secrets, loops, deps, each with path:line + an excerpt):
{evidence?}

For EACH check below decide present / partial / missing, grounded ONLY in the evidence
(do not invent code that isn't shown). Be specific and fair.

Checks:
%s

Output exactly one finding per check id with fields:
id, category="%s", title, status (present|partial|missing), severity,
location (the most relevant "path:line" from the evidence, or "" if not line-specific),
evidence (what the scan shows), why (why it matters), recommendation (null if present),
pattern, applicability, weight. Use the exact id/title/severity/weight/applicability/
pattern given in the checklist. Respond ONLY with JSON conforming to the schema."""

def build_category_auditor(cat: dict, checks) -> LlmAgent:
    cid = cat["id"]
    return LlmAgent(
        name=f"auditor_{cid}",
        model=config.MODEL,
        instruction=AUDITOR_INSTRUCTION % (cat["label"], _checklist(checks), cid),
        output_schema=CategoryFindings,
        output_key=f"findings_{cid}",
        generate_content_config=gen_config(0.1),
    )

def build_all_auditors(categories: list[str] | None = None,
                       spec_provided: bool = False) -> list[LlmAgent]:
    cats = categories or rubric.category_ids()
    auditors = [
        build_category_auditor(rubric.category_meta(cid), rubric.checks_for(cid))
        for cid in cats if rubric.checks_for(cid)
    ]
    if spec_provided:
        auditors.append(build_requirements_auditor())
    return auditors

# A spec-driven auditor: grades the code against the user's OWN requirements.
REQ_INSTRUCTION = """You validate an AI-agent codebase against the user's OWN requirements/spec,
from a static scan.

User requirements / spec (Markdown): {spec?}
Stated use case (may be empty): {use_case?}

Evidence pack (deterministic scan as JSON): {evidence?}

For EACH discrete requirement in the spec, decide present / partial / missing grounded in
the evidence, cite a location (path:line or ""), and give a concrete fix if not met.

Output one finding per requirement with fields:
id (a short kebab-case slug of the requirement), category="requirements", title (the
requirement, concise), status (present|partial|missing), severity (critical|high|medium|
low), location, evidence, why, recommendation (null if present), pattern="custom-requirement",
applicability="use_case", weight (1-3 by importance). Respond ONLY with JSON."""

def build_requirements_auditor() -> LlmAgent:
    return LlmAgent(
        name="auditor_requirements",
        model=config.MODEL,
        instruction=REQ_INSTRUCTION,
        output_schema=CategoryFindings,
        output_key="findings_requirements",
        generate_content_config=gen_config(0.0),
    )
