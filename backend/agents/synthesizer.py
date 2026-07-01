"""Synthesizer: qualitative judgement only (relevance + summary + use-case fit +
selected strengths/improvements). All numeric scoring is done in scoring.py."""
from __future__ import annotations
from google.adk.agents import LlmAgent
import config
from agents._common import gen_config
from schemas import SynthesisOutput

INSTRUCTION = """You finalize an agent-code audit.

Stated use case (may be empty): {use_case?}
Custom requirements / spec (Markdown, may be empty): {spec?}

Per-category findings (JSON in state):
architecture={findings_architecture?}
functionality={findings_functionality?}
context={findings_context?}
model={findings_model?}
security={findings_security?}
performance={findings_performance?}
reliability={findings_reliability?}

Produce:
- relevance: for each finding whose applicability is "use_case", decide included
  true/false given the use case (e.g. RAG is irrelevant if the agent isn't knowledge-
  based). If no use case is given, set included=false for use_case checks.
- summary: 2-3 sentence executive summary of the agent's agentic maturity.
- use_case_fit: 1-2 sentences on how well the code matches the stated use case (or note
  that no use case was provided).
- strength_ids / improvement_ids: the most important present / not-present check ids.
Respond ONLY with JSON conforming to the schema."""

def build_synthesizer() -> LlmAgent:
    return LlmAgent(
        name="synthesizer",
        model=config.MODEL,
        instruction=INSTRUCTION,
        output_schema=SynthesisOutput,
        output_key="synthesis",
        generate_content_config=gen_config(0.1),
    )
