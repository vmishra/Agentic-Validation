import type { ScanEvent, ScanSummary, ValidationReport } from '@/validator/types'

type Common = { useCase?: string; spec?: string; categories?: string[] }
export type ScanSource =
  | ({ kind: 'zip'; file: File } & Common)
  | ({ kind: 'folder'; path: string } & Common)
  | ({ kind: 'github'; url: string } & Common)

export async function createScan(source: ScanSource): Promise<string> {
  let res: Response
  if (source.kind === 'zip') {
    const fd = new FormData()
    fd.append('file', source.file)
    if (source.useCase) fd.append('useCase', source.useCase)
    if (source.spec) fd.append('spec', source.spec)
    if (source.categories) fd.append('categories', JSON.stringify(source.categories))
    res = await fetch('/api/scan', { method: 'POST', body: fd })
  } else {
    const body: Record<string, unknown> =
      source.kind === 'folder' ? { folderPath: source.path } : { githubUrl: source.url }
    body.useCase = source.useCase
    body.spec = source.spec
    body.categories = source.categories
    res = await fetch('/api/scan', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
    })
  }
  if (!res.ok) throw new Error((await res.text()) || 'Failed to start scan')
  return (await res.json()).scanId as string
}

export function openStream(scanId: string, onEvent: (e: ScanEvent) => void): EventSource {
  const es = new EventSource(`/api/scan/${scanId}/stream`)
  es.onmessage = (m) => {
    try { onEvent(JSON.parse(m.data) as ScanEvent) } catch { /* ignore keepalives */ }
  }
  return es
}

export async function listScans(): Promise<ScanSummary[]> {
  const r = await fetch('/api/scans')
  if (!r.ok) return []
  return r.json()
}

export async function getReport(scanId: string): Promise<ValidationReport> {
  const r = await fetch(`/api/scan/${scanId}/report`)
  if (!r.ok) throw new Error('Report not found')
  return r.json()
}
