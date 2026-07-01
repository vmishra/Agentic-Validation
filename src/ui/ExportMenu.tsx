import { Download } from 'lucide-react'

export function ExportMenu({ scanId }: { scanId: string }) {
  return (
    <div className="flex items-center gap-1">
      <a href={`/api/scan/${scanId}/export?format=md`}
        className="inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-[12px] text-muted hover:bg-elev-1 hover:text-text">
        <Download size={13} /> .md
      </a>
      <a href={`/api/scan/${scanId}/export?format=json`}
        className="inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-[12px] text-muted hover:bg-elev-1 hover:text-text">
        <Download size={13} /> .json
      </a>
    </div>
  )
}
