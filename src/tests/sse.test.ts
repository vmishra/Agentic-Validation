import { describe, it, expect, vi } from 'vitest'

describe('createScan', () => {
  it('POSTs JSON for github source', async () => {
    const fetchMock = vi.fn(async () => ({ ok: true, json: async () => ({ scanId: 'abc' }) }))
    vi.stubGlobal('fetch', fetchMock as unknown as typeof fetch)
    const { createScan } = await import('@/lib/sse')
    const id = await createScan({ kind: 'github', url: 'https://github.com/x/y', useCase: 'demo' })
    expect(id).toBe('abc')
    const [, opts] = fetchMock.mock.calls[0] as any
    expect(JSON.parse(opts.body).githubUrl).toBe('https://github.com/x/y')
  })
})
