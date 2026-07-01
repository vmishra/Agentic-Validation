# Architecture

Aegis validates an AI-agent codebase by combining a **deterministic static scan** with a
**Google ADK multi-agent system** on Gemini. Scoring is computed in Python (never by the
LLM) so results are reproducible.

## Pipeline

```
Ingest → Indexer (evidence pack) → ADK agents (stream) → Scoring (Python) → Report
```

1. **Ingest** (`backend/ingest.py`) — materializes a submission into a sandboxed temp
   workspace. Three sources: `.zip` upload, local folder, or `git clone` of a public
   GitHub URL. Enforces size/file caps and rejects zip-slip / path traversal; the
   workspace is deleted after the scan.

2. **Indexer** (`backend/indexer.py`, `detectors.py`) — walks the workspace with no LLM and
   builds an **evidence pack**: detected language(s) and agent framework, plus signals
   (tools, sub-agents, orchestration, loops, model ids, prompts, secrets, deps, tests,
   logging, caching, …), each with a `path:line` and a short excerpt. Binary files are
   skipped via a NUL-byte sniff; lockfiles/minified bundles/data dumps and build/cache
   directories are ignored; hidden dotfiles are included. `compact_evidence()` produces a
   **bounded** JSON view so input size stays constant regardless of repo size.

3. **ADK agents** (`backend/agents/`) — a `Coordinator` runs a `SequentialAgent`:
   - **Overview** — infers the app's purpose, architecture, and nuances from the evidence.
   - **Research** — an isolated agent whose only tool is `google_search`, used to ground
     model currency, dependency CVEs, and framework best practices.
   - **Auditors** — a `ParallelAgent` fans out to one auditor per selected category (plus a
     spec-driven "requirements" auditor when a custom spec is provided). Each auditor is a
     **single `LlmAgent` with a structured `output_schema`** that reasons over the bounded
     evidence pack and emits findings. No per-file tool loop → predictable cost and latency.
   - **Synthesizer** — produces qualitative judgement only (executive summary, use-case fit,
     and which `use_case` checks are relevant).

4. **Scoring** (`backend/scoring.py`) — deterministic. Each finding is `present|partial|missing`
   (1 / 0.5 / 0) with a weight; categories and the overall score are weighted means, mapped
   to a readiness band. The LLM never invents numbers.

5. **Streaming & report** (`backend/server.py`, `pipeline.py`) — ADK events are mapped to
   SSE and streamed to the UI; the final report is assembled and persisted to disk.

## ADK constraints honored

- `google_search` cannot share an agent with other tools → it's its own Research agent.
- `output_schema` cannot be combined with `tools` on one agent → auditors are schema-only,
  reasoning from the evidence pack rather than a tool loop.
- State flows between agents via `output_key` + `{var}` instruction templating.

## Robustness

- **Constant input size** — auditors read the bounded evidence pack, not the whole repo, so
  the validator scales from tiny repos to large ones.
- **Retries** — every model call retries transient errors (429 / 408 / 5xx / connection)
  with exponential backoff + jitter.
- **Graceful degradation** — if a category's agent fails, the pipeline assembles a partial
  report from the categories that completed instead of aborting.
- **Backstop** — a wall-clock limit (`AEGIS_RUN_TIMEOUT`) stops a runaway scan and reports
  what finished.

## Data model (selected)

- `EvidencePack` — the deterministic scan output.
- `Finding` — `{id, category, title, status, severity, location, evidence, why,
  recommendation, pattern, sources, applicability, weight}`.
- `ValidationReport` — `{overview, band, overall, categories[], findings[], strengths[],
  improvements[], use_case_fit, summary, …}`.

## Frontend

A React + Vite single-page app (`src/`) with a three-state flow (source → scanning →
report), a zustand store that folds SSE events via a pure `applyEvent` reducer, and a Vite
dev proxy from `/api` to the backend.
