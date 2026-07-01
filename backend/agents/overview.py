"""Overview sub-agent: infers what the scanned app actually is — purpose,
architecture, and notable nuances — from the deterministic evidence pack.
Runs early so it survives even if a downstream auditor degrades."""
from __future__ import annotations
from google.adk.agents import LlmAgent
import config
from agents._common import gen_config
from schemas import Overview

INSTRUCTION = """You inspect an AI-agent codebase and summarize it for a reviewer.

Stated use case (may be empty): {use_case?}
Custom requirements / spec (Markdown, may be empty): {spec?}

Evidence pack (deterministic scan, JSON — file tree, framework, tools, agents,
orchestration, models, prompts, deps): {evidence?}

From the EVIDENCE (not assumptions), produce:
- purpose: 1-2 concrete sentences on what this app/agent actually does (its job),
  inferred from entry points, tools, prompts, and data.
- architecture: 1-3 sentences on how it's built — framework, agent/orchestration
  shape, tools, model(s), retrieval/data, and notable libraries.
- nuances: up to 4 short strings on notable or unusual design choices, interesting
  patterns, or visible risks/gaps.
Be specific and grounded. Respond ONLY with JSON conforming to the schema."""

def build_overview_agent() -> LlmAgent:
    return LlmAgent(
        name="overview",
        model=config.MODEL,
        instruction=INSTRUCTION,
        output_schema=Overview,
        output_key="overview",
        generate_content_config=gen_config(0.1),
    )
