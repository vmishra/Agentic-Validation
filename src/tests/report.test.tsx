import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { useStore } from '@/state/store'
import { Report } from '@/ui/Scorecard'
import type { ValidationReport } from '@/validator/types'

const report: ValidationReport = {
  scan_id: 's', source: { kind: 'folder' }, use_case: 'demo',
  framework: { primary: 'google-adk' },
  overview: { purpose: 'Audits BigQuery cost from query history.', architecture: 'Single ADK root agent + MCP tools.', nuances: ['Minimal footprint'] },
  band: { label: 'Developing', tone: 'warn' }, overall: 0.5,
  categories: [{ id: 'security', label: 'Security & Credentials', score: 0.4, present: 1, partial: 0, missing: 1, total: 2 }],
  findings: [{ id: 'no-hardcoded-secrets', category: 'security', title: 'No hardcoded secrets', status: 'missing', severity: 'critical', location: 'config.py:3', evidence: 'hardcoded key', why: 'leak', recommendation: 'use env', pattern: 'secret-mgmt', sources: [], applicability: 'always', included: true, weight: 3 }],
  strengths: [], improvements: [], use_case_fit: 'Partial fit', summary: 'Needs work', scanned_files: 3, loc: 40, generated_at: '',
}

describe('Report', () => {
  beforeEach(() => { useStore.setState({ ...useStore.getState(), report, view: 'report' }) })
  it('renders band, category, and a finding with its fix', () => {
    render(<Report />)
    expect(screen.getByText('Developing')).toBeTruthy()
    expect(screen.getByText('No hardcoded secrets')).toBeTruthy()
    expect(screen.getByText(/use env/)).toBeTruthy()
    expect(screen.getByText(/Audits BigQuery cost/)).toBeTruthy()
    expect(screen.getByText(/config\.py:3/)).toBeTruthy()
  })
})
