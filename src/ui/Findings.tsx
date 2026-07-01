import { useStore } from '@/state/store'
import { CATEGORY_COLOR } from '@/validator/types'
import { Dot } from './primitives'
import { fmtPct } from '@/lib/format'
import { FindingCard } from './FindingCard'

export function Findings() {
  const report = useStore((s) => s.report)
  if (!report) return null
  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-5">
      {report.categories.map((cat) => {
        const findings = report.findings.filter((f) => f.category === cat.id && f.included)
        if (!findings.length) return null
        return (
          <section key={cat.id}>
            <div className="mb-2 flex items-center gap-2">
              <Dot color={CATEGORY_COLOR[cat.id]} size={9} />
              <h3 className="text-[14px] font-semibold text-text">{cat.label}</h3>
              <span className="ml-auto font-mono text-[12px] text-subtle">{cat.present}/{cat.total} · {fmtPct(cat.score)}</span>
            </div>
            <div className="flex flex-col gap-2">{findings.map((f) => <FindingCard key={f.id} f={f} />)}</div>
          </section>
        )
      })}
    </div>
  )
}
