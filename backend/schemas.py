"""Pydantic models shared across the pipeline and API."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

Status = Literal["present", "partial", "missing"]
Severity = Literal["critical", "high", "medium", "low"]
Applicability = Literal["always", "use_case"]

class Signal(BaseModel):
    name: str | None = None
    kind: str | None = None
    file: str
    line: int = 0
    excerpt: str = ""
    meta: dict = Field(default_factory=dict)

class DepInfo(BaseModel):
    manifest: str = ""
    packages: list[dict] = Field(default_factory=list)

class Source(BaseModel):
    """A grounding citation. Typed (no bare dict) so it is valid as part of an
    LLM output_schema under the Gemini Developer API (no additionalProperties)."""
    title: str = ""
    uri: str = ""

class EvidencePack(BaseModel):
    file_count: int = 0
    total_loc: int = 0
    languages: dict[str, int] = Field(default_factory=dict)
    size_bytes: int = 0
    framework: dict = Field(default_factory=dict)   # {primary, confidence, evidence:[]}
    file_tree: str = ""
    signals: dict = Field(default_factory=dict)      # name -> list[Signal] | DepInfo (serialized)

class Finding(BaseModel):
    id: str
    category: str
    title: str
    status: Status
    severity: Severity
    location: str = ""          # primary "path:line" to fix (empty if not code-specific)
    evidence: str
    why: str
    recommendation: str | None = None
    pattern: str
    sources: list[Source] = Field(default_factory=list)
    applicability: Applicability = "always"
    included: bool = True
    weight: float = 1

class CategoryFindings(BaseModel):
    category: str
    findings: list[Finding]

class RelevanceDecision(BaseModel):
    check_id: str
    included: bool
    reason: str = ""

class SynthesisOutput(BaseModel):
    relevance: list[RelevanceDecision] = Field(default_factory=list)
    summary: str = ""
    use_case_fit: str = ""
    strength_ids: list[str] = Field(default_factory=list)
    improvement_ids: list[str] = Field(default_factory=list)

class Overview(BaseModel):
    """What the scanned app actually is — inferred from the code, not the rubric."""
    purpose: str = ""
    architecture: str = ""
    nuances: list[str] = Field(default_factory=list)

class CategoryScore(BaseModel):
    id: str
    label: str
    score: float
    present: int
    partial: int
    missing: int
    total: int

class ValidationReport(BaseModel):
    scan_id: str
    source: dict
    use_case: str | None = None
    framework: dict = Field(default_factory=dict)        # {primary, ...}
    overview: Overview = Field(default_factory=Overview)
    band: dict = Field(default_factory=dict)             # {label, tone}
    overall: float = 0
    categories: list[CategoryScore] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    strengths: list[Finding] = Field(default_factory=list)
    improvements: list[Finding] = Field(default_factory=list)
    use_case_fit: str = ""
    summary: str = ""
    scanned_files: int = 0
    loc: int = 0
    generated_at: str = ""
