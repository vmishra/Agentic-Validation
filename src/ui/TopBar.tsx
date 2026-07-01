import { ShieldCheck, Moon, Sun } from 'lucide-react'
import { useState } from 'react'
import { IconButton } from './primitives'

export function TopBar() {
  const [dark, setDark] = useState(false)
  const toggle = () => {
    const next = !dark
    setDark(next)
    document.documentElement.setAttribute('data-theme', next ? 'dark' : 'light')
  }
  return (
    <header className="hairline-b flex items-center gap-2.5 px-5 py-3">
      <ShieldCheck size={19} strokeWidth={1.7} className="text-accent-strong" />
      <span className="text-[15px] font-semibold text-text">Aegis</span>
      <span className="text-[12px] text-subtle">· Agentic Validation</span>
      <div className="ml-auto flex items-center gap-3">
        <span className="hidden items-center gap-1.5 text-[11px] text-subtle sm:inline-flex">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-success" /> gemini-3.5-flash
        </span>
        <IconButton label="Toggle theme" onClick={toggle}>
          {dark ? <Sun size={16} /> : <Moon size={16} />}
        </IconButton>
      </div>
    </header>
  )
}
