import { useStore } from '@/state/store'
import { CATEGORY_COLOR } from '@/validator/types'
import { Dot } from './primitives'
import { cn } from '@/lib/cn'

const NODES = [
  { id: 'architecture', label: 'Architecture' },
  { id: 'functionality', label: 'Functionality' },
  { id: 'context', label: 'Context' },
  { id: 'model', label: 'Model' },
  { id: 'security', label: 'Security' },
  { id: 'performance', label: 'Performance' },
  { id: 'reliability', label: 'Reliability' },
]

export function AgentGraph() {
  const log = useStore((s) => s.log)
  const liveCategories = useStore((s) => s.liveCategories)
  const dispatched = new Set(log.filter((l) => l.kind === 'dispatch').map((l) => (l as { category: string }).category))
  const done = new Set(liveCategories.map((c) => c.id))
  const searched = log.some((l) => l.kind === 'search')

  return (
    <div className="rounded-lg border border-border bg-surface-raised p-4" style={{ boxShadow: 'var(--shadow-1)' }}>
      <div className="mb-3 flex flex-wrap items-center gap-2 text-[12px] text-subtle">
        <span className={cn('inline-flex items-center gap-1.5 rounded-full px-2 py-0.5',
          searched ? 'bg-accent-soft text-accent-strong' : 'text-subtle')}>
          Research · google_search {searched ? '✓' : '…'}
        </span>
        <span>→ Coordinator → 7 auditors → Synthesizer</span>
      </div>
      <div className="grid grid-cols-7 gap-2">
        {NODES.map((n) => {
          const state = done.has(n.id) ? 'done' : dispatched.has(n.id) ? 'active' : 'idle'
          return (
            <div key={n.id}
              className={cn('flex flex-col items-center gap-1.5 rounded-md border p-2 text-center transition-colors',
                state === 'done' ? 'border-border bg-elev-1' : state === 'active' ? 'border-accent bg-accent-soft' : 'border-border opacity-50')}>
              <Dot color={CATEGORY_COLOR[n.id]} size={8} glow={state === 'active'} />
              <span className="text-[10px] leading-tight text-muted">{n.label}</span>
              <span className="text-[10px] text-subtle">{state === 'done' ? '✓' : state === 'active' ? '…' : ''}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
