import { Sparkles, TriangleAlert, RotateCcw } from 'lucide-react'
import { useStore } from '@/state/store'
import { CATEGORY_COLOR, type ValidationReport, type Tone } from '@/validator/types'
import { Badge, Dot, SectionLabel } from './primitives'
import { fmtInt, fmtPct } from '@/lib/format'
import { BRAND_VAR } from '@/lib/brand'
import { Findings } from './Findings'
import { ExportMenu } from './ExportMenu'
import { OverviewPanel } from './OverviewPanel'

const TONE_VAR: Record<Tone, string> = {
  success: 'var(--success)', warn: 'var(--warn)', danger: 'var(--danger)',
  accent: 'var(--accent)', neutral: 'var(--text-subtle)',
}

export function Report() {
  const report = useStore((s) => s.report)
  const reset = useStore((s) => s.reset)
  if (!report) return null
  return (
    <div className="grid h-full min-h-0 grid-cols-[24rem_minmax(0,1fr)]">
      <aside className="hairline-r scroll-area min-h-0 overflow-y-auto bg-surface p-4">
        <Scorecard report={report} />
      </aside>
      <main className="flex min-h-0 flex-col">
        <div className="hairline-b flex items-center gap-2 px-4 py-2">
          <span className="text-[13px] font-medium text-text">Findings</span>
          <span className="text-[11px] text-subtle">· real ADK validator · Gemini 3.5 Flash</span>
          <div className="ml-auto flex items-center gap-2">
            <ExportMenu scanId={report.scan_id} />
            <button onClick={reset} className="inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-[12px] text-muted hover:bg-elev-1 hover:text-text">
              <RotateCcw size={13} /> New scan
            </button>
          </div>
        </div>
        <div className="scroll-area min-h-0 flex-1 overflow-y-auto p-4">
          <div className="mx-auto mb-5 max-w-4xl">
            <OverviewPanel overview={report.overview} framework={report.framework.primary} />
          </div>
          <Findings />
        </div>
      </main>
    </div>
  )
}

function Scorecard({ report }: { report: ValidationReport }) {
  const includedCount = report.findings.filter((f) => f.included).length
  const presentCount = report.findings.filter((f) => f.status === 'present' && f.included).length
  return (
    <div className="flex flex-col gap-5">
      <div>
        <SectionLabel>Overall readiness</SectionLabel>
        <div className="mt-3 flex items-center gap-4">
          <ScoreRing value={report.overall} tone={report.band.tone} />
          <div>
            <Badge tone={report.band.tone}>{report.band.label}</Badge>
            <p className="mt-1.5 font-mono text-[11px] text-subtle">
              {presentCount}/{includedCount} checks · {fmtInt(report.scanned_files)} files
            </p>
          </div>
        </div>
        {report.summary && <p className="mt-3 text-[12px] leading-relaxed text-muted">{report.summary}</p>}
        {report.use_case_fit && (
          <p className="mt-2 rounded-md bg-elev-1 p-2.5 text-[12px] text-muted"><span className="font-semibold text-text">Use-case fit · </span>{report.use_case_fit}</p>
        )}
      </div>

      <div>
        <SectionLabel className="mb-2">By category</SectionLabel>
        <div className="flex flex-col gap-2">
          {report.categories.map((c) => (
            <div key={c.id}>
              <div className="flex items-center gap-1.5 text-[11px]">
                <Dot color={CATEGORY_COLOR[c.id]} size={7} />
                <span className="text-muted">{c.label}</span>
                <span className="ml-auto font-mono text-subtle">{fmtPct(c.score)}</span>
              </div>
              <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-elev-2">
                <div className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.max(3, c.score * 100)}%`, background: BRAND_VAR[CATEGORY_COLOR[c.id]] }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {report.strengths.length > 0 && (
        <div>
          <div className="mb-2 flex items-center gap-1.5"><Sparkles size={13} className="text-success" /><SectionLabel>Strengths</SectionLabel></div>
          <ul className="flex flex-col gap-1.5">
            {report.strengths.map((f) => <li key={f.id} className="text-[12px] text-muted">✅ {f.title}</li>)}
          </ul>
        </div>
      )}
      {report.improvements.length > 0 && (
        <div>
          <div className="mb-2 flex items-center gap-1.5"><TriangleAlert size={13} className="text-warn" /><SectionLabel>Areas to improve</SectionLabel></div>
          <ul className="flex flex-col gap-1.5">
            {report.improvements.map((f) => <li key={f.id} className="text-[12px] text-muted">{f.status === 'missing' ? '❌' : '🟡'} {f.title}</li>)}
          </ul>
        </div>
      )}
    </div>
  )
}

function ScoreRing({ value, tone }: { value: number; tone: Tone }) {
  const r = 26, c = 2 * Math.PI * r, off = c * (1 - value)
  return (
    <div className="relative" style={{ width: 68, height: 68 }}>
      <svg width="68" height="68" viewBox="0 0 68 68" className="-rotate-90">
        <circle cx="34" cy="34" r={r} fill="none" stroke="var(--elev-2)" strokeWidth="6" />
        <circle cx="34" cy="34" r={r} fill="none" stroke={TONE_VAR[tone]} strokeWidth="6" strokeLinecap="round"
          strokeDasharray={c} strokeDashoffset={off} style={{ transition: 'stroke-dashoffset 600ms var(--ease-spring)' }} />
      </svg>
      <span className="absolute inset-0 flex items-center justify-center font-mono text-[17px] font-semibold text-text">{fmtPct(value)}</span>
    </div>
  )
}
