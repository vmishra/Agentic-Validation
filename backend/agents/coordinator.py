"""Assemble the root ADK agent and map ADK events to SSE event dicts."""
from __future__ import annotations
from google.adk.agents import SequentialAgent, ParallelAgent
import rubric
from agents.overview import build_overview_agent
from agents.research import build_research_agent
from agents.auditors import build_all_auditors
from agents.synthesizer import build_synthesizer

_SEEN_AUTHORS: set[str] = set()  # reset per run by the pipeline

def build_root_agent(categories: list[str] | None = None,
                     spec_provided: bool = False) -> SequentialAgent:
    overview = build_overview_agent()
    research = build_research_agent()
    auditors = build_all_auditors(categories, spec_provided)
    parallel = ParallelAgent(name="auditors", sub_agents=auditors)
    synth = build_synthesizer()
    # overview + research run first so a partial report still has them if an auditor degrades
    return SequentialAgent(name="aegis_coordinator", sub_agents=[overview, research, parallel, synth])

_CAT_IDS = set(rubric.category_ids()) | set(rubric.EXTRA_CATEGORIES)
_CAT_LABEL = {cid: rubric.category_meta(cid)["label"] for cid in _CAT_IDS}

def _category_of(author: str) -> str | None:
    for cid in _CAT_IDS:
        if author.endswith(cid):
            return cid
    return None

def event_to_sse(event) -> list[dict]:
    out: list[dict] = []
    author = getattr(event, "author", "") or ""
    # dispatch (first time we see an auditor_<cat>)
    if author.startswith("auditor_"):
        cid = _category_of(author)
        if cid and author not in _SEEN_AUTHORS:
            _SEEN_AUTHORS.add(author)
            out.append({"type": "dispatch", "category": cid, "label": _CAT_LABEL[cid]})
    # tool calls
    get_calls = getattr(event, "get_function_calls", None)
    if callable(get_calls):
        for fc in (get_calls() or []):
            out.append({"type": "tool", "agent": author, "tool": getattr(fc, "name", "tool"),
                        "detail": str(getattr(fc, "args", {}))[:160]})
    # google_search grounding
    gm = getattr(event, "grounding_metadata", None)
    if gm:
        queries = list(getattr(gm, "web_search_queries", None) or [])
        sources = []
        for chunk in (getattr(gm, "grounding_chunks", None) or []):
            web = getattr(chunk, "web", None)
            if web and getattr(web, "uri", None):
                sources.append({"title": getattr(web, "title", "") or web.uri, "uri": web.uri})
        if queries or sources:
            out.append({"type": "search", "queries": queries, "sources": sources})
    return out

def reset_seen() -> None:
    _SEEN_AUTHORS.clear()
