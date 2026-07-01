import { describe, it, expect } from 'vitest'
import { applyEvent, initialViewState } from '@/state/store'
import type { ScanEvent } from '@/validator/types'

const ev = (e: ScanEvent) => e

describe('applyEvent', () => {
  it('records phases and index', () => {
    let s = initialViewState()
    s = applyEvent(s, ev({ type: 'phase', label: 'Ingesting…' }))
    s = applyEvent(s, ev({ type: 'index', framework: { primary: 'google-adk' }, fileCount: 3, loc: 40, tree: 'a' }))
    expect(s.phases).toContain('Ingesting…')
    expect(s.index?.fileCount).toBe(3)
  })

  it('collects findings and category scores into the log', () => {
    let s = initialViewState()
    s = applyEvent(s, ev({ type: 'dispatch', category: 'security', label: 'Security' }))
    s = applyEvent(s, ev({ type: 'check', finding: { id: 'x', category: 'security', title: 'T', status: 'missing', severity: 'high', evidence: 'e', why: 'w', pattern: 'p', sources: [], applicability: 'always', included: true, weight: 1 } }))
    s = applyEvent(s, ev({ type: 'category', score: { id: 'security', label: 'Security', score: 0.5, present: 0, partial: 0, missing: 1, total: 1 } }))
    expect(s.findings).toHaveLength(1)
    expect(s.liveCategories[0].id).toBe('security')
  })

  it('stores the report on report event', () => {
    let s = initialViewState()
    const report: any = { scan_id: 's', categories: [], findings: [], overall: 0.5, band: { label: 'Developing', tone: 'warn' } }
    s = applyEvent(s, ev({ type: 'report', report }))
    expect(s.report?.scan_id).toBe('s')
    expect(s.view).toBe('report')
  })

  it('captures errors', () => {
    const s = applyEvent(initialViewState(), ev({ type: 'error', message: 'boom' }))
    expect(s.error).toBe('boom')
  })
})
