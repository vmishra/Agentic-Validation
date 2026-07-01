"""Research sub-agent: grounds model currency, CVEs, best practices via Google Search.
ADK forbids mixing google_search with other tools, so it is its own agent."""
from __future__ import annotations
from google.adk.agents import LlmAgent
from google.adk.tools import google_search
import config
from agents._common import gen_config

INSTRUCTION = """You are a research assistant grounding an agent-code audit.

Detected framework: {framework?}
Model ids found in the code: {model_ids?}
Dependencies: {deps?}

Using Google Search, produce a concise, sourced briefing (<=200 words) covering:
1. Are the model ids current and available, or retired/deprecated? Name the current
   equivalents if any are stale.
2. Any well-known security CVEs in the listed dependencies.
3. One or two current best-practice notes for this framework's agent design.
Always include source URLs inline. If you cannot verify something, say so."""

def build_research_agent() -> LlmAgent:
    return LlmAgent(
        name="research",
        model=config.MODEL,
        instruction=INSTRUCTION,
        tools=[google_search],
        output_key="research_notes",
        generate_content_config=gen_config(0.2),
    )
