import { useState } from 'react'
import { FolderGit2, Github, Upload, Play, FileText, Check, History, ChevronRight } from 'lucide-react'
import { useStore } from '@/state/store'
import { Segmented, SectionLabel } from './primitives'
import { CATEGORIES } from '@/validator/types'
import { fmtPct } from '@/lib/format'
import { cn } from '@/lib/cn'

type Tab = 'github' | 'folder' | 'zip'
const EXAMPLES = [
  'A support agent that answers product questions from our docs and files tickets.',
  'A coding agent that reviews PRs and comments inline.',
  'A research agent that searches the web and writes cited briefs.',
]

export function SourceStep() {
  const startScan = useStore((s) => s.startScan)
  const openScan = useStore((s) => s.openScan)
  const history = useStore((s) => s.history)
  const error = useStore((s) => s.error)

  const [tab, setTab] = useState<Tab>('github')
  const [url, setUrl] = useState('')
  const [path, setPath] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [useCase, setUseCase] = useState('')
  const [spec, setSpec] = useState('')
  const [specName, setSpecName] = useState('')
  const [cats, setCats] = useState<string[]>(CATEGORIES.map((c) => c.id))

  const canScan = (tab === 'github' && url.trim()) || (tab === 'folder' && path.trim()) || (tab === 'zip' && !!file)
  const toggleCat = (id: string) =>
    setCats((prev) => (prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]))
  const allOn = cats.length === CATEGORIES.length

  const onScan = () => {
    const common = { useCase, spec, categories: cats.length ? cats : undefined }
    if (tab === 'github') void startScan({ kind: 'github', url: url.trim(), ...common })
    else if (tab === 'folder') void startScan({ kind: 'folder', path: path.trim(), ...common })
    else if (file) void startScan({ kind: 'zip', file, ...common })
  }

  const onSpecFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) { setSpec(await f.text()); setSpecName(f.name) }
  }

  return (
    <div className="scroll-area mx-auto h-full max-w-2xl overflow-y-auto px-8 py-10">
      <h1 className="text-[26px] font-semibold text-text">Validate an agent</h1>
      <p className="mt-1 text-[14px] text-muted">
        Point Aegis at an agent codebase. A real ADK multi-agent validator scans it on
        Gemini 3.5 Flash, infers what it does, and scores it with concrete fix locations.
      </p>

      <div className="mt-6">
        <Segmented
          value={tab}
          onChange={(v) => setTab(v as Tab)}
          options={[
            { value: 'github', label: 'GitHub URL' },
            { value: 'folder', label: 'Local folder' },
            { value: 'zip', label: 'Upload .zip' },
          ]}
        />
      </div>

      <div className="mt-4 rounded-lg border border-border bg-surface-raised p-4" style={{ boxShadow: 'var(--shadow-1)' }}>
        {tab === 'github' && (
          <label className="flex items-center gap-2.5">
            <Github size={18} className="text-accent-strong" />
            <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://github.com/org/repo"
              className="w-full bg-transparent text-[14px] text-text outline-none placeholder:text-subtle" />
          </label>
        )}
        {tab === 'folder' && (
          <label className="flex items-center gap-2.5">
            <FolderGit2 size={18} className="text-accent-strong" />
            <input value={path} onChange={(e) => setPath(e.target.value)} placeholder="/Users/you/projects/my-agent"
              className="w-full bg-transparent font-mono text-[13px] text-text outline-none placeholder:text-subtle" />
          </label>
        )}
        {tab === 'zip' && (
          <label className={cn('flex cursor-pointer items-center gap-2.5 text-[14px]', file ? 'text-text' : 'text-subtle')}>
            <Upload size={18} className="text-accent-strong" />
            {file ? file.name : 'Choose a .zip of your agent project'}
            <input type="file" accept=".zip" className="hidden" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
          </label>
        )}
      </div>

      {/* use case */}
      <div className="mt-5">
        <SectionLabel className="mb-1.5">What is this agent supposed to do? (optional)</SectionLabel>
        <textarea value={useCase} onChange={(e) => setUseCase(e.target.value)} rows={2}
          placeholder="Describe the intended behavior so Aegis can judge use-case fit…"
          className="w-full rounded-lg border border-border bg-surface-raised p-3 text-[13px] text-text outline-none focus:border-accent" />
        <div className="mt-2 flex flex-wrap gap-1.5">
          {EXAMPLES.map((ex) => (
            <button key={ex} type="button" onClick={() => setUseCase(ex)}
              className="rounded-full border border-border px-2.5 py-1 text-[11px] text-muted hover:bg-elev-1 hover:text-text">
              {ex.slice(0, 38)}…
            </button>
          ))}
        </div>
      </div>

      {/* what to validate (filters) */}
      <div className="mt-5">
        <div className="mb-1.5 flex items-center gap-2">
          <SectionLabel>What to validate</SectionLabel>
          <button type="button" onClick={() => setCats(allOn ? [] : CATEGORIES.map((c) => c.id))}
            className="ml-auto text-[11px] text-accent-strong hover:underline">
            {allOn ? 'Clear all' : 'Select all'}
          </button>
        </div>
        <div className="grid grid-cols-2 gap-1.5">
          {CATEGORIES.map((c) => {
            const on = cats.includes(c.id)
            return (
              <button key={c.id} type="button" onClick={() => toggleCat(c.id)}
                className={cn('flex items-center gap-2 rounded-md border px-2.5 py-1.5 text-left text-[12px] transition-colors',
                  on ? 'border-accent bg-accent-soft text-accent-strong' : 'border-border text-muted hover:bg-elev-1')}>
                <span className={cn('flex h-3.5 w-3.5 items-center justify-center rounded-[4px] border',
                  on ? 'border-accent bg-accent text-white' : 'border-border-strong')}>
                  {on && <Check size={11} strokeWidth={3} />}
                </span>
                {c.label}
              </button>
            )
          })}
        </div>
        <p className="mt-1.5 text-[11px] text-subtle">All categories run by default. Uncheck any to narrow the scan.</p>
      </div>

      {/* custom requirements spec */}
      <div className="mt-5">
        <div className="mb-1.5 flex items-center gap-2">
          <SectionLabel>Custom requirements (Markdown, optional)</SectionLabel>
          <label className="ml-auto inline-flex cursor-pointer items-center gap-1.5 rounded-md border border-border px-2 py-0.5 text-[11px] text-muted hover:bg-elev-1 hover:text-text">
            <FileText size={12} /> {specName || 'Upload .md'}
            <input type="file" accept=".md,.markdown,.txt" className="hidden" onChange={onSpecFile} />
          </label>
        </div>
        <textarea value={spec} onChange={(e) => setSpec(e.target.value)} rows={3}
          placeholder={'Paste or upload your own spec, e.g.\n- The agent MUST never hardcode secrets\n- The agent MUST cite sources for factual claims'}
          className="w-full rounded-lg border border-border bg-surface-raised p-3 font-mono text-[12px] text-text outline-none focus:border-accent" />
        <p className="mt-1.5 text-[11px] text-subtle">Each requirement is graded against the code as its own finding.</p>
      </div>

      {error && <p className="mt-4 text-[13px] text-danger">{error}</p>}

      <button type="button" onClick={onScan} disabled={!canScan}
        className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-md bg-accent px-5 py-2.5 text-[14px] font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50">
        <Play size={16} /> Scan
      </button>

      {/* recent scans */}
      {history.length > 0 && (
        <div className="mt-8">
          <div className="mb-2 flex items-center gap-1.5">
            <History size={13} className="text-subtle" />
            <SectionLabel>Recent scans</SectionLabel>
          </div>
          <div className="flex flex-col gap-1.5">
            {history.slice(0, 8).map((h) => (
              <button key={h.scanId} type="button" onClick={() => void openScan(h.scanId)}
                className="group flex items-center gap-2 rounded-md border border-border bg-surface-raised px-3 py-2 text-left hover:border-accent">
                <span className="min-w-0 flex-1">
                  <span className="block truncate font-mono text-[12px] text-text">{h.label}</span>
                  <span className="text-[11px] text-subtle">
                    {h.framework || 'unknown'}{h.useCase ? ` · ${h.useCase.slice(0, 40)}` : ''}
                  </span>
                </span>
                <span className="shrink-0 font-mono text-[12px] text-muted">{fmtPct(h.overall)}</span>
                <ChevronRight size={14} className="shrink-0 text-subtle group-hover:text-accent-strong" />
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
