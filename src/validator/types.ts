import type { BrandColor } from '@/lib/brand'

export type Status = 'present' | 'partial' | 'missing'
export type Severity = 'critical' | 'high' | 'medium' | 'low'
export type Tone = 'neutral' | 'accent' | 'success' | 'warn' | 'danger'

export interface Source { title: string; uri: string }

export interface Overview { purpose: string; architecture: string; nuances: string[] }

export interface Finding {
  id: string; category: string; title: string; status: Status; severity: Severity
  location?: string; evidence: string; why: string; recommendation?: string | null; pattern: string
  sources: Source[]; applicability: 'always' | 'use_case'; included: boolean; weight: number
}

export interface ScanSummary {
  scanId: string; label: string; framework: string; overall: number
  band: string; useCase?: string | null; generatedAt: string
}

export const CATEGORIES: { id: string; label: string }[] = [
  { id: 'architecture', label: 'Architecture & Orchestration' },
  { id: 'functionality', label: 'Functionality & Capability' },
  { id: 'context', label: 'Prompt & Context Engineering' },
  { id: 'model', label: 'Model Strategy' },
  { id: 'security', label: 'Security & Credentials' },
  { id: 'performance', label: 'Performance, Cost & Efficiency' },
  { id: 'reliability', label: 'Reliability, Observability & Eval' },
]
export interface CategoryScore {
  id: string; label: string; score: number
  present: number; partial: number; missing: number; total: number
}
export interface ValidationReport {
  scan_id: string; source: Record<string, unknown>; use_case?: string | null
  framework: { primary?: string; confidence?: number; evidence?: string[] }
  overview: Overview
  band: { label: string; tone: Tone }; overall: number
  categories: CategoryScore[]; findings: Finding[]
  strengths: Finding[]; improvements: Finding[]
  use_case_fit: string; summary: string; scanned_files: number; loc: number; generated_at: string
}

export type ScanEvent =
  | { type: 'phase'; label: string }
  | { type: 'index'; framework: { primary?: string; confidence?: number; evidence?: string[] }; fileCount: number; loc: number; tree: string }
  | { type: 'overview'; overview: Overview }
  | { type: 'dispatch'; category: string; label: string }
  | { type: 'tool'; agent: string; tool: string; detail: string }
  | { type: 'search'; queries: string[]; sources: Source[] }
  | { type: 'check'; finding: Finding }
  | { type: 'category'; score: CategoryScore }
  | { type: 'report'; report: ValidationReport }
  | { type: 'error'; message: string }
  | { type: 'done' }

export const CATEGORY_COLOR: Record<string, BrandColor> = {
  architecture: 'blue', functionality: 'green', context: 'yellow',
  model: 'blue', security: 'red', performance: 'yellow', reliability: 'neutral',
}
