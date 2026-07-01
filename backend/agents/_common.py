"""Shared generation config for all Aegis agents.

Robustness: every model call retries transient errors (429/5xx) with backoff, so a
single blip during the parallel auditor burst doesn't fail a category. Low temperature
keeps verdicts reproducible (LLM-as-judge; numeric scoring stays in Python)."""
from __future__ import annotations
from google.genai import types

# Exponential backoff with jitter. Covers rate limits (429), request timeout/conflict
# (408/409), and transient server/connection errors (5xx). google-genai also retries
# transport-level connection errors when retry options are configured.
_RETRY = types.HttpRetryOptions(
    attempts=6,           # ~1+2+4+8+16s of backoff before giving up
    initial_delay=1.0,
    max_delay=30.0,
    exp_base=2.0,
    jitter=0.3,
    http_status_codes=[408, 409, 429, 500, 502, 503, 504],
)

def gen_config(temperature: float | None = None) -> types.GenerateContentConfig:
    kw: dict = {"http_options": types.HttpOptions(retry_options=_RETRY)}
    if temperature is not None:
        kw["temperature"] = temperature
    return types.GenerateContentConfig(**kw)
