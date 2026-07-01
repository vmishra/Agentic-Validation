import { CheckCircle2, MinusCircle, XCircle } from 'lucide-react'
import type { Finding } from '@/validator/types'
import { Badge, type Tone } from './primitives'
import { cn } from '@/lib/cn'

const META = {
  present: { Icon: CheckCircle2, cls: 'text-success', label: 'Present' },
  partial: { Icon: MinusCircle, cls: 'text-warn', label: 'Partial' },
  missing: { Icon: XCircle, cls: 'text-danger', label: 'Missing' },
} as const
const SEV_TONE: Record<Finding['severity'], Tone> = { critical: 'danger', high: 'danger', medium: 'warn', low: 'neutral' }

export function FindingCard({ f }: { f: Finding }) {
  const m = META[f.status]
  return (
    <div className="rounded-md border border-border bg-surface-raised p-3.5"
      style={f.status !== 'present' ? { borderLeftWidth: 3, borderLeftColor: f.status === 'missing' ? 'var(--danger)' : 'var(--warn)' } : undefined}>
      <div className="flex items-start gap-2.5">
        <m.Icon size={16} className={cn('mt-0.5 shrink-0', m.cls)} />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[13px] font-semibold text-text">{f.title}</span>
            <span className={cn('text-[11px] font-medium', m.cls)}>{m.label}</span>
            {f.status !== 'present' && <Badge tone={SEV_TONE[f.severity]}>{f.severity}</Badge>}
            <span className="ml-auto font-mono text-[10px] text-subtle">{f.pattern}</span>
          </div>
          {f.location && (
            <p className="mt-1 font-mono text-[11px] font-medium text-accent-strong">↳ {f.location}</p>
          )}
          <p className="mt-1 whitespace-pre-wrap font-mono text-[11px] text-subtle">{f.evidence}</p>
          <p className="mt-1.5 text-[12px] leading-relaxed text-muted">{f.why}</p>
          {f.recommendation && (
            <p className="mt-2 rounded-md bg-accent-soft px-2.5 py-1.5 text-[12px] leading-relaxed text-accent-strong">
              <span className="font-semibold">Fix · </span>{f.recommendation}
            </p>
          )}
          {f.sources.length > 0 && (
            <p className="mt-1.5 text-[11px] text-subtle">
              Sources:{' '}
              {f.sources.map((s, i) => (
                <span key={i}>
                  {i > 0 ? ', ' : ''}
                  <a href={s.uri} target="_blank" rel="noreferrer" className="text-accent-strong underline">{s.title || s.uri}</a>
                </span>
              ))}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
