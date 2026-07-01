# Contributing to Aegis

Thanks for your interest! Aegis is a real, working multi-agent validator and we'd love help making it better.

## Getting set up

1. Install prerequisites: Python 3.10+, Node 18+, git.
2. Copy `.env.example` to `.env` and add a Google AI Studio key (<https://aistudio.google.com/apikey>).
3. `./app.sh start` → http://localhost:5176

## Running tests

```bash
# Backend (live ADK tests self-skip without a key)
cd backend && ../.venv/bin/python -m pytest -q

# Frontend
npm run test && npm run typecheck && npm run build
```

Please keep tests green and add tests for new behavior. The deterministic layers
(`ingest`, `indexer`, `detectors`, `rubric`, `scoring`, `export`) are unit-testable
without any API calls — prefer those over live tests where possible.

## Ways to contribute

- **New framework detectors** — add fingerprints in `backend/detectors.py` with a test.
- **New checks** — add a `CheckDef` in `backend/rubric.py` (category, weight, severity, guidance).
- **Prebuilt scanners** — optional integrations (e.g. detect-secrets, pip-audit, tree-sitter)
  with a graceful fallback so a missing dependency never breaks a scan.
- **UI/UX** — the portal is in `src/`; keep the clean, light, restrained aesthetic.

## Pull requests

- Keep changes focused; one topic per PR.
- Match the surrounding code style; small, well-named units.
- Never commit secrets. `.env`, `.aegis-history/`, and build output are git-ignored — keep it that way.
- Describe what changed and how you verified it (tests / manual run).

## Reporting issues

- Bugs and feature requests: open an issue with steps to reproduce.
- Security vulnerabilities: please report privately rather than in a public issue.
