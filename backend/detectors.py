"""Deterministic framework + signal detection over file contents (best-effort)."""
from __future__ import annotations
import re

FRAMEWORK_FINGERPRINTS = [
    ("google-adk", [r"\bfrom google\.adk\b", r"\bgoogle\.adk\b", r"\bgoogle-adk\b"]),
    ("anthropic", [r"\bfrom anthropic\b", r"\bimport anthropic\b", r"claude-agent-sdk", r"@anthropic-ai/"]),
    ("langgraph", [r"\blanggraph\b", r"from langgraph", r"create_react_agent", r"StateGraph\("]),
    ("langchain", [r"\blangchain\b", r"from langchain", r"@langchain/"]),
    ("openai-agents", [r"\bfrom agents\b.*Agent", r"openai-agents", r"agents\.Runner"]),
    ("openai", [r"\bfrom openai\b", r"\bimport openai\b", r"openai\.OpenAI\(", r"AsyncOpenAI\("]),
    ("crewai", [r"\bcrewai\b", r"from crewai", r"\bCrew\(", r"\bAgent\(.*role="]),
    ("autogen", [r"\bautogen\b", r"from autogen", r"AssistantAgent\(", r"UserProxyAgent\("]),
    ("llamaindex", [r"\bllama_index\b", r"llamaindex", r"@llamaindex/"]),
    ("pydantic-ai", [r"\bpydantic_ai\b", r"from pydantic_ai", r"pydantic-ai"]),
    ("smolagents", [r"\bsmolagents\b", r"from smolagents", r"CodeAgent\(", r"ToolCallingAgent\("]),
    ("agno", [r"\bfrom agno\b", r"\bimport agno\b", r"\bagno\.agent\b"]),
    ("dspy", [r"\bimport dspy\b", r"\bfrom dspy\b", r"dspy\.(Module|Predict|ChainOfThought)"]),
    ("haystack", [r"\bhaystack\b", r"from haystack"]),
    ("semantic-kernel", [r"semantic_kernel", r"semantic-kernel"]),
    ("mastra", [r"@mastra/", r"\bnew Mastra\(", r"\bnew Agent\(.*instructions"]),
    ("vercel-ai", [r"\bfrom ['\"]ai['\"]", r"@ai-sdk/", r"\bgenerateText\(", r"\bstreamText\("]),
    ("google-genai", [r"\bfrom google import genai\b", r"\bgoogle\.genai\b", r"google-genai"]),
]

MODEL_ID_RE = re.compile(
    r"['\"]((?:gemini|gpt|claude|o\d|text-embedding|mistral|llama|command)[a-zA-Z0-9._\-]*)['\"]"
)
SECRET_PATTERNS = [
    ("google-api-key", re.compile(r"AIza[0-9A-Za-z_\-]{30,}")),
    ("aistudio-key", re.compile(r"\bAQ\.[A-Za-z0-9_\-]{8,}")),
    ("openai-key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("anthropic-key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("aws-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("generic-assign", re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*=\s*['\"][^'\"]{12,}['\"]")),
]

def detect_framework(files: dict[str, str]) -> dict:
    blob = "\n".join(files.values())
    best = ("custom", 0.0, [])
    for name, pats in FRAMEWORK_FINGERPRINTS:
        hits = [p for p in pats if re.search(p, blob)]
        if hits:
            conf = min(1.0, 0.4 + 0.2 * len(hits))
            if conf > best[1]:
                best = (name, conf, [f"matched /{h}/" for h in hits[:3]])
    return {"primary": best[0], "confidence": best[1], "evidence": best[2]}

def _iter_lines(files: dict[str, str]):
    for path, text in files.items():
        for i, line in enumerate(text.splitlines(), start=1):
            yield path, i, line

def _add(out, key, **item):
    out.setdefault(key, []).append(item)

def find_signals(files: dict[str, str]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    SIG = {
        "tools": re.compile(r"(@tool\b|def \w+_tool\b|FunctionTool\(|tools\s*=\s*\[|McpToolset\(|types\.Tool\()"),
        "agents": re.compile(r"(LlmAgent\(|Agent\(|SequentialAgent\(|ParallelAgent\(|LoopAgent\(|create_react_agent\()"),
        "orchestration": re.compile(r"(SequentialAgent\(|ParallelAgent\(|LoopAgent\(|sub_agents\s*=|StateGraph\(|workflow)"),
        "prompts": re.compile(r"(system_instruction|instruction\s*=|system_prompt|SYSTEM_PROMPT)"),
        "env": re.compile(r"(os\.getenv\(|os\.environ|process\.env\.)"),
        "tests": re.compile(r"(def test_|import pytest|describe\(|it\()"),
        "error_handling": re.compile(r"(try:|except |\.catch\(|retry|backoff|tenacity)"),
        "logging": re.compile(r"(logging\.|logger\.|console\.log|structlog)"),
        "tracing": re.compile(r"(opentelemetry|trace\.|tracer|langsmith|Cloud Trace|cloud_trace)"),
        "caching": re.compile(r"(cache|lru_cache|context_caching|CachedContent|ContextWindowCompression)"),
        "streaming": re.compile(r"(stream=True|generate_content_stream|run_async|StreamingResponse|text/event-stream)"),
        "memory": re.compile(r"(memory|MemoryBank|session\.state|checkpoint|conversation_history)"),
        "retrieval": re.compile(r"(retriev|vector|embedding|rag\b|VectorSearch|pinecone|faiss|chroma)"),
    }
    for path, i, line in _iter_lines(files):
        for key, rx in SIG.items():
            if rx.search(line):
                _add(out, key, file=path, line=i, excerpt=line.strip()[:200])
        for m in MODEL_ID_RE.finditer(line):
            _add(out, "model_ids", name=m.group(1), file=path, line=i, excerpt=line.strip()[:200])
        for label, rx in SECRET_PATTERNS:
            if rx.search(line):
                _add(out, "secrets", kind=label, file=path, line=i,
                     excerpt=rx.sub("***REDACTED***", line.strip())[:200])
    # loop termination: scan a 6-line forward window from each loop header
    lines_by_file = {p: t.splitlines() for p, t in files.items()}
    for path, lines in lines_by_file.items():
        for idx, line in enumerate(lines):
            if re.search(r"^\s*(while|for)\b.*:\s*$", line) or re.search(r"\b(while|for)\s*\(", line):
                window = " ".join(lines[idx: idx + 6])
                has_term = bool(re.search(r"(break|return|max_iter|max_iterations|stop|range\(|<|>)", window))
                _add(out, "loops", file=path, line=idx + 1, excerpt=line.strip()[:200],
                     meta={"has_termination": has_term})
    return out
