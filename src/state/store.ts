import { create } from 'zustand'
import type { CategoryScore, Finding, Overview, ScanEvent, ScanSummary, ValidationReport } from '@/validator/types'
import { createScan, openStream, listScans, getReport, type ScanSource } from '@/lib/sse'

export type LogItem =
  | { kind: 'phase'; label: string }
  | { kind: 'dispatch'; category: string; label: string }
  | { kind: 'tool'; agent: string; tool: string; detail: string }
  | { kind: 'search'; queries: string[]; sources: { title: string; uri: string }[] }
  | { kind: 'check'; finding: Finding }
  | { kind: 'category'; label: string; score: number }

export interface ViewState {
  view: 'source' | 'scanning' | 'report'
  phases: string[]
  index?: { framework: { primary?: string }; fileCount: number; loc: number; tree: string }
  log: LogItem[]
  liveCategories: CategoryScore[]
  findings: Finding[]
  overview?: Overview
  report?: ValidationReport
  error?: string
}

// Explicitly resets every per-scan field so a new scan clears the previous one.
export function initialViewState(): ViewState {
  return {
    view: 'source', phases: [], index: undefined, log: [], liveCategories: [],
    findings: [], overview: undefined, report: undefined, error: undefined,
  }
}

export function applyEvent(s: ViewState, e: ScanEvent): ViewState {
  switch (e.type) {
    case 'phase':
      return { ...s, phases: [...s.phases, e.label], log: [...s.log, { kind: 'phase', label: e.label }] }
    case 'index':
      return { ...s, index: { framework: e.framework, fileCount: e.fileCount, loc: e.loc, tree: e.tree } }
    case 'overview':
      return { ...s, overview: e.overview }
    case 'dispatch':
      return { ...s, log: [...s.log, { kind: 'dispatch', category: e.category, label: e.label }] }
    case 'tool':
      return { ...s, log: [...s.log, { kind: 'tool', agent: e.agent, tool: e.tool, detail: e.detail }] }
    case 'search':
      return { ...s, log: [...s.log, { kind: 'search', queries: e.queries, sources: e.sources }] }
    case 'check':
      return { ...s, findings: [...s.findings, e.finding], log: [...s.log, { kind: 'check', finding: e.finding }] }
    case 'category':
      return {
        ...s, liveCategories: [...s.liveCategories.filter((c) => c.id !== e.score.id), e.score],
        log: [...s.log, { kind: 'category', label: e.score.label, score: e.score.score }],
      }
    case 'report':
      return { ...s, report: e.report, view: 'report' }
    case 'error':
      return { ...s, error: e.message }
    case 'done':
      return s
    default:
      return s
  }
}

interface Store extends ViewState {
  history: ScanSummary[]
  lastSource?: ScanSource
  startScan: (source: ScanSource) => Promise<void>
  retry: () => void
  loadHistory: () => Promise<void>
  openScan: (scanId: string) => Promise<void>
  reset: () => void
}

export const useStore = create<Store>((set, get) => ({
  ...initialViewState(),
  history: [],
  loadHistory: async () => {
    try { set({ history: await listScans() }) } catch { /* offline — keep current */ }
  },
  openScan: async (scanId) => {
    try {
      const report = await getReport(scanId)
      set({ ...initialViewState(), report, view: 'report' })
    } catch (err) {
      set({ error: (err as Error).message })
    }
  },
  startScan: async (source) => {
    set({ ...initialViewState(), view: 'scanning', lastSource: source })  // clear prior scan
    try {
      const scanId = await createScan(source)
      const es = openStream(scanId, (e) => {
        set((prev) => applyEvent(prev as ViewState, e))
        if (e.type === 'done') { es.close(); void get().loadHistory() }
      })
    } catch (err) {
      set({ error: (err as Error).message })
    }
  },
  retry: () => { const s = get().lastSource; if (s) void get().startScan(s) },
  reset: () => set({ ...initialViewState(), view: 'source' }),  // history is preserved
}))
