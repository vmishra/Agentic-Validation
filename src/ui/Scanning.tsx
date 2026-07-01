import { RotateCcw } from 'lucide-react'
import { useStore } from '@/state/store'
import { AgentGraph } from './AgentGraph'
import { ScanLog } from './ScanLog'
import { fmtInt } from '@/lib/format'

export function Scanning() {
  const index = useStore((s) => s.index)
  const overview = useStore((s) => s.overview)
  const error = useStore((s) => s.error)
  const retry = useStore((s) => s.retry)
  const reset = useStore((s) => s.reset)
  return (
    <div className="mx-auto flex h-full max-w-4xl flex-col gap-4 p-6">
      <div className="flex items-center gap-3 text-[13px] text-muted">
        <span className="inline-flex h-2 w-2 animate-pulse rounded-full bg-accent" />
        Validating…
        {index && <span className="text-subtle">· {index.framework.primary ?? 'unknown'} · {fmtInt(index.fileCount)} files · {fmtInt(index.loc)} LOC</span>}
      </div>
      <AgentGraph />
      {overview?.purpose && (
        <div className="rounded-md border border-border bg-surface-raised px-3 py-2 text-[12px] text-muted">
          <span className="font-medium text-text">Detected · </span>{overview.purpose}
        </div>
      )}
      {error && (
        <div className="rounded-md border border-border bg-danger-soft p-3">
          <p className="text-[13px] text-danger">{error}</p>
          <div className="mt-2 flex gap-2">
            <button type="button" onClick={() => retry()}
              className="inline-flex items-center gap-1.5 rounded-md bg-accent px-3 py-1.5 text-[12px] font-semibold text-white hover:opacity-90">
              <RotateCcw size={13} /> Retry scan
            </button>
            <button type="button" onClick={() => reset()}
              className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-[12px] text-muted hover:bg-elev-1 hover:text-text">
              New scan
            </button>
          </div>
        </div>
      )}
      <ScanLog />
    </div>
  )
}
