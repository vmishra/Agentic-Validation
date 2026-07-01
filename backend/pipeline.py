"""End-to-end scan pipeline: ingest -> index -> ADK run -> score -> report.
Yields SSE event dicts as it goes."""
from __future__ import annotations
import json, time
from typing import AsyncIterator
from google.adk.runners import InMemoryRunner
from google.genai import types
import ingest, indexer, scoring, rubric, config
from schemas import Finding, CategoryFindings, SynthesisOutput, Overview
from agents import coordinator

def _materialize(source: dict, scan_id: str):
    kind = source.get("kind")
    if kind == "zip":
        return ingest.ingest_zip(source["data"], scan_id)
    if kind == "folder":
        return ingest.ingest_folder(source["path"], scan_id)
    if kind == "github":
        return ingest.ingest_github(source["url"], scan_id)
    raise ingest.IngestError(f"Unknown source kind: {kind}")

def _collect_findings(state: dict) -> list[Finding]:
    findings: list[Finding] = []
    for key, raw in (state or {}).items():
        if not key.startswith("findings_") or not raw:
            continue
        if isinstance(raw, str):
            try: raw = json.loads(raw)
            except Exception: continue
        try:
            cf = CategoryFindings.model_validate(raw)
            findings.extend(cf.findings)
        except Exception:
            continue
    return findings

def _synthesis(state: dict) -> SynthesisOutput:
    raw = state.get("synthesis")
    if not raw:
        return SynthesisOutput()
    if isinstance(raw, str):
        try: raw = json.loads(raw)
        except Exception: return SynthesisOutput()
    try:
        return SynthesisOutput.model_validate(raw)
    except Exception:
        return SynthesisOutput()

def _overview(state: dict) -> Overview:
    raw = state.get("overview")
    if not raw:
        return Overview()
    if isinstance(raw, str):
        try: raw = json.loads(raw)
        except Exception: return Overview()
    try:
        return Overview.model_validate(raw)
    except Exception:
        return Overview()

def _safe_source(source: dict) -> dict:
    return {k: v for k, v in source.items() if k != "data"}  # never echo zip bytes

async def run_scan(scan_id: str, source: dict, use_case: str | None,
                   categories: list[str] | None = None, spec: str | None = None) -> AsyncIterator[dict]:
    coordinator.reset_seen()
    spec = (spec or "").strip()
    try:
        yield {"type": "phase", "label": "Ingesting submission…"}
        workspace = _materialize(source, scan_id)

        yield {"type": "phase", "label": "Indexing files…"}
        evidence = indexer.build_evidence(workspace)
        yield {"type": "index", "framework": evidence.framework,
               "fileCount": evidence.file_count, "loc": evidence.total_loc,
               "tree": evidence.file_tree}

        if not config.api_key():
            yield {"type": "error",
                   "message": "No GEMINI_API_KEY configured — returning static index only."}
            yield {"type": "done"}
            return

        root = coordinator.build_root_agent(categories, bool(spec))
        runner = InMemoryRunner(agent=root, app_name="aegis")
        session = await runner.session_service.create_session(
            app_name="aegis", user_id="aegis",
            state={
                "use_case": use_case or "",
                "spec": spec,
                "evidence": indexer.compact_evidence(evidence),
                "framework": evidence.framework.get("primary", ""),
                "model_ids": json.dumps(evidence.signals.get("model_ids", [])),
                "deps": json.dumps(evidence.signals.get("deps", {})),
            },
        )
        # Run the ADK agents. A single sub-agent blip (transient 429/503/safety) would
        # otherwise abort the whole ParallelAgent TaskGroup — instead we capture it and
        # still assemble a report from whatever findings landed in state (graceful
        # degradation), only failing hard if nothing usable was produced.
        adk_error: BaseException | None = None
        deadline = time.monotonic() + config.RUN_TIMEOUT_S
        try:
            async for event in runner.run_async(
                user_id="aegis", session_id=session.id,
                new_message=types.Content(role="user", parts=[types.Part(text="Validate this agent.")]),
            ):
                for sse in coordinator.event_to_sse(event):
                    yield sse
                if time.monotonic() > deadline:  # backstop: stop consuming, assemble what's done
                    adk_error = TimeoutError(f"scan exceeded {config.RUN_TIMEOUT_S}s")
                    break
        except BaseException as exc:  # noqa: BLE001 — includes ExceptionGroup from ParallelAgent
            adk_error = exc

        final = await runner.session_service.get_session(
            app_name="aegis", user_id="aegis", session_id=session.id)
        state = final.state if final else {}
        findings = _collect_findings(state)
        synthesis = _synthesis(state)
        overview = _overview(state)

        if not findings:
            msg = "Validation produced no findings."
            if adk_error:
                msg = f"Validation failed: {str(adk_error)[:200]}"
            yield {"type": "error", "message": msg}
            yield {"type": "done"}
            return
        if overview.purpose or overview.architecture:
            yield {"type": "overview", "overview": overview.model_dump()}
        if adk_error:
            yield {"type": "phase",
                   "label": "Some auditors degraded; report assembled from completed categories."}

        run_cats = list(categories) if categories else rubric.category_ids()
        if any(f.category == "requirements" for f in findings) and "requirements" not in run_cats:
            run_cats.append("requirements")
        report = scoring.assemble_report(scan_id, _safe_source(source), use_case, evidence,
                                         findings, synthesis, overview, run_cats)
        for cat in report.categories:
            for f in [x for x in report.findings if x.category == cat.id and x.included]:
                yield {"type": "check", "finding": f.model_dump()}
            yield {"type": "category", "score": cat.model_dump()}
        yield {"type": "report", "report": report.model_dump()}
        yield {"type": "done"}
    except Exception as exc:  # noqa: BLE001
        yield {"type": "error", "message": str(exc)[:300]}
        yield {"type": "done"}
    finally:
        ingest.cleanup(scan_id)
