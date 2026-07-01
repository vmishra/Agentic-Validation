import { useEffect } from 'react'
import { useStore } from '@/state/store'
import { Shell } from '@/ui/Shell'
import { SourceStep } from '@/ui/SourceStep'
import { Scanning } from '@/ui/Scanning'
import { Report } from '@/ui/Scorecard'

export function App() {
  const view = useStore((s) => s.view)
  const loadHistory = useStore((s) => s.loadHistory)
  const loadConfig = useStore((s) => s.loadConfig)
  useEffect(() => { void loadHistory(); void loadConfig() }, [loadHistory, loadConfig])
  return (
    <Shell>
      {view === 'source' && <SourceStep />}
      {view === 'scanning' && <Scanning />}
      {view === 'report' && <Report />}
    </Shell>
  )
}
