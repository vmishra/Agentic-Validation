/**
 * Small shared UI primitives. Kept deliberately plain, the visual interest
 * comes from typography, spacing, and the one accent hairline, not from busy
 * chrome. Google brand colour appears only as agent identity dots and pillar
 * accents.
 */

import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'
import type { BrandColor } from '@/lib/brand'
import { BRAND_VAR } from '@/lib/brand'

export function Dot({ color, size = 8, glow = false }: { color: BrandColor; size?: number; glow?: boolean }) {
  return (
    <span
      className="inline-block shrink-0 rounded-full"
      style={{
        width: size,
        height: size,
        background: BRAND_VAR[color],
        boxShadow: glow ? `0 0 0 3px color-mix(in oklch, ${BRAND_VAR[color]} 22%, transparent)` : undefined,
      }}
    />
  )
}

export function Panel({
  children,
  className,
  pad = true,
}: {
  children: ReactNode
  className?: string
  pad?: boolean
}) {
  return (
    <div
      className={cn(
        'rounded-lg border border-border bg-surface-raised',
        pad && 'p-5',
        className,
      )}
      style={{ boxShadow: 'var(--shadow-1)' }}
    >
      {children}
    </div>
  )
}

export function SectionLabel({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn('text-[11px] font-medium uppercase tracking-[0.08em] text-subtle', className)}>
      {children}
    </div>
  )
}

export type Tone = 'neutral' | 'accent' | 'success' | 'warn' | 'danger'

const TONE_CLASS: Record<Tone, string> = {
  neutral: 'border-border text-muted bg-elev-1',
  accent: 'text-accent-strong',
  success: 'text-success',
  warn: 'text-warn',
  danger: 'text-danger',
}
const TONE_BG: Record<Tone, string> = {
  neutral: '',
  accent: 'bg-accent-soft border-transparent',
  success: 'bg-success-soft border-transparent',
  warn: 'bg-warn-soft border-transparent',
  danger: 'bg-danger-soft border-transparent',
}

export function Badge({ children, tone = 'neutral', className }: { children: ReactNode; tone?: Tone; className?: string }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[11px] font-medium',
        TONE_CLASS[tone],
        TONE_BG[tone],
        className,
      )}
    >
      {children}
    </span>
  )
}

export function IconButton({
  children,
  onClick,
  label,
  active = false,
  className,
}: {
  children: ReactNode
  onClick?: () => void
  label: string
  active?: boolean
  className?: string
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      title={label}
      className={cn(
        'inline-flex h-8 w-8 items-center justify-center rounded-md border border-border text-muted transition-colors',
        'hover:bg-elev-1 hover:text-text',
        active && 'border-accent text-accent-strong bg-accent-soft',
        className,
      )}
    >
      {children}
    </button>
  )
}

export function Segmented<T extends string>({
  options,
  value,
  onChange,
}: {
  options: { value: T; label: string }[]
  value: T
  onChange: (v: T) => void
}) {
  return (
    <div className="inline-flex rounded-lg border border-border bg-elev-1 p-0.5">
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          onClick={() => onChange(o.value)}
          className={cn(
            'rounded-md px-3 py-1 text-[13px] font-medium transition-colors',
            value === o.value ? 'bg-surface-raised text-text shadow-sm' : 'text-muted hover:text-text',
          )}
          style={value === o.value ? { boxShadow: 'var(--shadow-1)' } : undefined}
        >
          {o.label}
        </button>
      ))}
    </div>
  )
}

export function Toggle({
  checked,
  onChange,
  label,
}: {
  checked: boolean
  onChange: (v: boolean) => void
  label: string
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      onClick={() => onChange(!checked)}
      className={cn(
        'relative h-5 w-9 shrink-0 rounded-full border transition-colors',
        checked ? 'border-transparent bg-danger' : 'border-border bg-elev-2',
      )}
    >
      <span
        className={cn(
          'absolute top-0.5 h-3.5 w-3.5 rounded-full bg-white transition-all',
          checked ? 'left-[18px]' : 'left-0.5',
        )}
        style={{ boxShadow: '0 1px 2px oklch(0% 0 0 / 0.3)' }}
      />
    </button>
  )
}
