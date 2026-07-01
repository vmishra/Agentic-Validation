export type BrandColor = 'blue' | 'red' | 'yellow' | 'green' | 'neutral'

export const BRAND_VAR: Record<BrandColor, string> = {
  blue: 'var(--color-g-blue)',
  red: 'var(--color-g-red)',
  yellow: 'var(--color-g-yellow)',
  green: 'var(--color-g-green)',
  neutral: 'var(--text-subtle)',
}
