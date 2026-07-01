import { useEffect, useRef } from 'react'
import { ChevronRight, FileSearch, Search, Wrench, CheckCircle2, MinusCircle, XCircle } from 'lucide-react'
import { useStore, type LogItem } from '@/state/store'
import { cn } from '@/lib/cn'

const STATUS_ICON = { present: CheckCircle2, partial: MinusCircle, missing: XCircle } as const
const STATUS_CLS = { present: 'text-success', partial: 'text-warn', missing: 'text-danger' } as const

export function ScanLog() {
  const log = useStore((s) => s.log)
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => { ref.current?.scrollTo({ top: ref.current.scrollHeight, behavior: 'smooth' }) }, [log.length])

  return (
    <div ref={ref} className="scroll-area min-h-0 flex-1 overflow-y-auto font-mono text-[12px]">
      {log.map((l, i) => <Row key={i} item={l} />)}
    </div>
  )
}

function Row({ item }: { item: LogItem }) {
  if (item.kind === 'phase') return <div className="flex items-center gap-2 py-1 text-subtle"><FileSearch size={13} /> {item.label}</div>
  if (item.kind === 'dispatch') return <div className="flex items-center gap-2 py-1.5 font-semibold text-text"><ChevronRight size={13} className="text-accent-strong" /> auditor · {item.label}</div>
  if (item.kind === 'tool') return <div className="flex items-center gap-2 py-0.5 pl-5 text-subtle"><Wrench size={12} /> {item.tool}({item.detail})</div>
  if (item.kind === 'search') return <div className="flex items-start gap-2 py-0.5 pl-5 text-accent-strong"><Search size={12} className="mt-0.5" /> <span>{item.queries.join(' · ') || 'search'}{item.sources.length ? ` — ${item.sources.length} sources` : ''}</span></div>
  if (item.kind === 'category') return <div className="py-1 pl-5 text-subtle">✓ {item.label}: {Math.round(item.score * 100)}%</div>
  const Icon = STATUS_ICON[item.finding.status]
  return (
    <div className="flex items-start gap-2 py-0.5 pl-5">
      <Icon size={13} className={cn('mt-0.5 shrink-0', STATUS_CLS[item.finding.status])} />
      <span className="text-muted"><span className="text-text">{item.finding.title}</span> — {item.finding.evidence}</span>
    </div>
  )
}
