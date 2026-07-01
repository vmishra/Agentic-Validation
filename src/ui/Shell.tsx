import type { ReactNode } from 'react'
import { TopBar } from './TopBar'

export function Shell({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-full min-h-0 flex-col bg-surface">
      <TopBar />
      <main className="min-h-0 flex-1 overflow-hidden">{children}</main>
    </div>
  )
}
