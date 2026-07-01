"""The validation rubric: categories + checks. Framework-agnostic, benchmarked
against Anthropic 'Building Effective Agents' patterns, ADK multi-agent/workflow
patterns, and the OWASP LLM/agentic Top 10. Volatile specifics (model currency,
CVEs) are grounded at runtime by the Research agent."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class CheckDef:
    id: str
    category: str
    title: str
    pattern: str
    applicability: str   # always | use_case
    weight: float
    severity: str        # critical | high | medium | low
    guidance: str

CATEGORIES = [
    {"id": "architecture", "label": "Architecture & Orchestration", "color": "blue"},
    {"id": "functionality", "label": "Functionality & Capability", "color": "green"},
    {"id": "context", "label": "Prompt & Context Engineering", "color": "yellow"},
    {"id": "model", "label": "Model Strategy", "color": "blue"},
    {"id": "security", "label": "Security & Credentials", "color": "red"},
    {"id": "performance", "label": "Performance, Cost & Efficiency", "color": "yellow"},
    {"id": "reliability", "label": "Reliability, Observability & Eval", "color": "neutral"},
]

def _c(*a, **k):  # tiny helper
    return CheckDef(*a, **k)

CHECKS = [
    # ---- architecture ----
    _c("multi-agent-decomposition", "architecture", "Work decomposed across specialised agents",
       "Multi-agent system / orchestrator-workers", "use_case", 3, "high",
       "Present if there are multiple agents with distinct roles; partial if 2; missing if a single monolithic agent does everything. Use evidence from agents/orchestration signals."),
    _c("orchestration-pattern", "architecture", "Explicit, appropriate orchestration pattern",
       "Routing / Parallel / Sequential / Evaluator-optimizer", "always", 2, "medium",
       "Present if an explicit pattern (sequential/parallel/router/loop/graph) is used; partial if implicit; missing if control flow is ad-hoc."),
    _c("agent-boundaries", "architecture", "Sub-agents have single, clear responsibilities",
       "Separation of concerns", "use_case", 2, "medium",
       "Judge whether each agent/tool has a focused responsibility vs a god-agent."),
    _c("loop-termination", "architecture", "Loops have explicit termination / max iterations",
       "Bounded agent loop", "always", 2, "high",
       "Present if loops have break/max_iterations/stop conditions (loops signal meta.has_termination); missing if unbounded while-True without exit."),
    _c("state-handoff", "architecture", "Explicit context/state passing between steps",
       "Structured handoff / shared state", "use_case", 1, "medium",
       "Present if state passed via explicit keys/return values; missing if global mutable soup."),
    _c("reusable-skills", "architecture", "Reusable skills / capability modules",
       "Skills / tool packs", "use_case", 1, "low",
       "Present if reusable skills/hooks/tool modules are authored; partial otherwise."),
    # ---- functionality ----
    _c("tools-defined", "functionality", "Tool choice & definitions are well-formed",
       "Tool use / function calling", "use_case", 3, "high",
       "Judge tool CHOICE and quality: are the right tools present for the task, with typed params and "
       "clear, action-oriented descriptions, and no redundant/overlapping tools? Present if well-chosen "
       "and well-formed; partial if untyped/sparse/over-broad; missing if the use case needs tools but none exist."),
    _c("tool-arg-validation", "functionality", "Tool arguments are validated",
       "Schema-validated tool I/O", "use_case", 1, "medium",
       "Present if tool inputs validated; partial if minimal; missing if none."),
    _c("structured-outputs", "functionality", "Structured outputs where parsed downstream",
       "Structured output / response schema", "use_case", 1, "low",
       "Present if response schemas/typed outputs used where needed."),
    _c("grounding-rag", "functionality", "Grounded retrieval when the use case needs knowledge",
       "RAG / grounding", "use_case", 2, "high",
       "Only relevant if the stated use case implies answering from a knowledge base/docs. Present if retrieval+grounding exists; missing if it answers from parametric memory."),
    _c("use-case-coverage", "functionality", "Capabilities match the stated use case",
       "Requirement coverage", "use_case", 3, "high",
       "Compare detected capabilities (tools, agents, retrieval) to the user's stated use case; flag gaps. If no use case is given, mark partial and note it could not be assessed."),
    # ---- context ----
    _c("system-prompt-quality", "context", "System prompt & instruction quality",
       "Prompt engineering (system instructions + few-shot/ICL)", "always", 2, "medium",
       "Judge the system prompt AND per-agent/per-tool instructions: do they define role, rules, "
       "output format, and constraints clearly? Credit few-shot / in-context examples where the task "
       "benefits. Present if substantive and specific; partial if thin/generic; missing if absent."),
    _c("context-window-mgmt", "context", "Context-window management for long sessions",
       "Compaction / summary / sliding window / turn cap", "use_case", 2, "medium",
       "Present if compaction/summary/sliding-window/turn-cap present; relevant mainly for conversational/long-running agents."),
    _c("context-hygiene", "context", "Retrieves relevant context vs stuffing everything",
       "Context engineering", "always", 1, "low",
       "Judge whether prompts assemble targeted context vs dumping large blobs."),
    _c("memory-scope", "context", "Memory scoped & isolated per user",
       "Per-user memory isolation", "use_case", 2, "high",
       "If memory/state is used across users, present only if scoped per user; missing if shared/global (cross-user leak risk)."),
    _c("token-budget", "context", "Token-budget discipline",
       "Cost-aware context", "always", 1, "low",
       "Present if there is evidence of bounding tokens/inputs; else partial."),
    # ---- model ----
    _c("model-tiering", "model", "Right model per task (tiering & adaptation ladder)",
       "Model routing / tiering; prompt→RAG→tune ladder", "use_case", 2, "medium",
       "Present if cheaper models route simple work and stronger models handle hard reasoning, and the "
       "adaptation choice fits (use the cheapest technique that hits the bar — prompt, then RAG, then "
       "fine-tune; don't fine-tune to fix a prompt problem). Partial if one tier everywhere."),
    _c("model-currency", "model", "Models are current & version-pinned (not retired)",
       "Model currency / pinning", "always", 2, "high",
       "Use research_notes (Google Search) to judge whether the model ids found are current/available and pinned. Missing if a retired/deprecated id is used."),
    _c("generation-params", "model", "Sane generation parameters",
       "Decoding params", "always", 1, "low",
       "Present if temperature/max-tokens etc. set appropriately for the task; partial if defaults everywhere for a task that needs control."),
    _c("model-fallbacks", "model", "Fallbacks/retries on model errors",
       "Resilient model calls", "always", 1, "medium",
       "Present if 429/503/transient errors are retried/handled; missing if unhandled."),
    # ---- security ----
    _c("no-hardcoded-secrets", "security", "No hardcoded secrets / API keys",
       "Secret management", "always", 3, "critical",
       "Missing (critical) if any secret literal is detected in code; present if keys come from env/secret store. Cite the masked evidence."),
    _c("prompt-injection-defense", "security", "Prompt-injection defenses",
       "OWASP LLM01", "use_case", 2, "high",
       "Present if untrusted input / tool output is handled defensively (sanitization, instruction separation); relevant when the agent consumes external/tool/web content."),
    _c("excessive-agency", "security", "Tool permissions are least-privilege",
       "OWASP LLM06 Excessive Agency", "use_case", 2, "high",
       "Flag over-broad/dangerous tools (shell, file delete, network) without gating; present if scoped + gated."),
    _c("output-handling-pii", "security", "Sensitive data / PII handled before logging/return",
       "OWASP LLM02 / data handling", "use_case", 1, "medium",
       "Present if PII/sensitive output is redacted before logs/return; relevant if the agent handles user/personal data."),
    _c("tool-authz", "security", "Tool auth & identity propagation",
       "Least privilege / on-behalf-of", "use_case", 1, "medium",
       "Present if tools authenticate and propagate the user's identity where acting on their behalf."),
    _c("code-exec-sandbox", "security", "Code-exec / dangerous tools are sandboxed",
       "Sandboxing", "use_case", 1, "high",
       "If the agent runs code/shell, present only if sandboxed/constrained; missing if arbitrary exec."),
    _c("dependency-cves", "security", "No known-vulnerable dependencies",
       "Supply chain", "always", 1, "medium",
       "Use research_notes to flag pinned deps with known CVEs; present if none known."),
    # ---- performance ----
    _c("parallelization", "performance", "Independent work runs in parallel",
       "Parallelization", "use_case", 2, "medium",
       "Present if independent sub-tasks fan out concurrently; partial if serialised unnecessarily."),
    _c("caching", "performance", "Caching where beneficial",
       "Prompt/context caching", "always", 1, "low",
       "Present if context/prompt caching or memoization used for repeated work."),
    _c("streaming", "performance", "Responses stream to the user",
       "Streaming UX", "use_case", 1, "low",
       "Present if outputs stream; relevant for interactive agents."),
    _c("runaway-guards", "performance", "Guards against runaway loops / cost",
       "Cost guardrails", "always", 1, "medium",
       "Present if iteration/time/token guards bound worst-case cost; overlaps loop-termination but scored for cost."),
    # ---- reliability ----
    _c("error-handling", "reliability", "Error handling & graceful degradation",
       "Resilience", "always", 2, "high",
       "Present if tool/model errors are caught and degrade gracefully; missing if errors crash the run."),
    _c("idempotent-writes", "reliability", "Idempotent writes / safe retries",
       "Idempotency", "use_case", 1, "medium",
       "If the agent performs writes/side-effects, present only if retries are idempotent (no double-submit)."),
    _c("observability", "reliability", "Tracing + structured logging",
       "Observability", "always", 2, "high",
       "Present if tracing/spans + structured logs per step; partial if logging only; missing if none."),
    _c("tests", "reliability", "Automated tests for agents/tools/routing",
       "Testing", "always", 2, "high",
       "Present if unit+integration tests exist; partial if some; missing if none."),
    _c("evals", "reliability", "Evals: golden set, negative tests, edge cases",
       "Agent evaluation", "use_case", 2, "medium",
       "Present if eval/golden datasets + negative/edge tests exist (ideally CI-wired); missing if no evals."),
]

def checks_for(category: str) -> list[CheckDef]:
    return [c for c in CHECKS if c.category == category]

def check_ids() -> set[str]:
    return {c.id for c in CHECKS}

# Categories that aren't in the static rubric but can appear in a run (spec-driven).
EXTRA_CATEGORIES = {
    "requirements": {"id": "requirements", "label": "Custom Requirements", "color": "blue"},
}

def category_meta(cid: str) -> dict:
    for c in CATEGORIES:
        if c["id"] == cid:
            return c
    return EXTRA_CATEGORIES.get(cid, {"id": cid, "label": cid.replace("_", " ").title(), "color": "neutral"})

def category_ids() -> list[str]:
    return [c["id"] for c in CATEGORIES]
