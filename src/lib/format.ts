export const fmtInt = (n: number) => new Intl.NumberFormat('en-US').format(Math.round(n))
export const fmtPct = (n: number) => `${Math.round(n * 100)}%`
