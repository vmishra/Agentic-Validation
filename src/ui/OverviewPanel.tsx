import { Compass } from 'lucide-react'
import type { Overview } from '@/validator/types'
import { SectionLabel } from './primitives'

export function OverviewPanel({ overview, framework }: { overview?: Overview; framework?: string }) {
  if (!overview || (!overview.purpose && !overview.architecture)) return null
  return (
    <div className="rounded-lg border border-border bg-surface-raised p-4" style={{ boxShadow: 'var(--shadow-1)' }}>
      <div className="mb-2 flex items-center gap-1.5">
        <Compass size={14} strokeWidth={1.7} className="text-accent-strong" />
        <SectionLabel>What this is</SectionLabel>
        {framework && (
          <span className="ml-auto rounded-full border border-border px-2 py-0.5 font-mono text-[11px] text-subtle">{framework}</span>
        )}
      </div>
      {overview.purpose && <p className="text-[13px] leading-relaxed text-text">{overview.purpose}</p>}
      {overview.architecture && (
        <p className="mt-2 text-[12px] leading-relaxed text-muted">
          <span className="font-medium text-text">Architecture · </span>{overview.architecture}
        </p>
      )}
      {overview.nuances?.length > 0 && (
        <ul className="mt-2.5 flex flex-col gap-1">
          {overview.nuances.map((n, i) => (
            <li key={i} className="flex items-start gap-1.5 text-[12px] text-muted">
              <span className="mt-1.5 inline-block h-1 w-1 shrink-0 rounded-full bg-accent-strong" />{n}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
