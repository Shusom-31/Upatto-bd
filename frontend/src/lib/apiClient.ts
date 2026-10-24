import type { Dataset, Operation, OperationResult, Profile, RowPage, Session } from '../types'

const base = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'
let credential = sessionStorage.getItem('tathyashala_token') ?? ''
export function setCredential(token: string) { credential = token; sessionStorage.setItem('tathyashala_token', token) }
export function clearCredential() { credential = ''; sessionStorage.removeItem('tathyashala_token'); sessionStorage.removeItem('tathyashala_session') }
export function storedSession(): Session | null { const raw = sessionStorage.getItem('tathyashala_session'); return raw ? JSON.parse(raw) as Session : null }
export function saveSession(session: Session) { setCredential(session.token); sessionStorage.setItem('tathyashala_session', JSON.stringify(session)) }

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  if (credential) headers.set('X-Workspace-Token', credential)
  if (init.body && !(init.body instanceof FormData)) headers.set('Content-Type', 'application/json')
  const response = await fetch(`${base}${path}`, { ...init, headers })
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}))
    throw new Error(payload.detail ?? `Request failed (${response.status})`)
  }
  return response.status === 204 ? undefined as T : response.json() as Promise<T>
}

export const api = {
  start: (display_name: string) => request<Session>('/sessions', { method: 'POST', body: JSON.stringify({ display_name }) }),
  end: (sessionId: string) => request<void>(`/sessions/${sessionId}`, { method: 'DELETE' }),
  upload: (sessionId: string, file: File, sheet?: string) => {
    const form = new FormData(); form.append('file', file); if (sheet) form.append('sheet_name', sheet)
    return request<Dataset>(`/sessions/${sessionId}/datasets`, { method: 'POST', body: form })
  },
  inspect: (sessionId: string, file: File) => {
    const form = new FormData(); form.append('file', file)
    return request<{ sheets: string[] }>(`/sessions/${sessionId}/datasets/inspect`, { method: 'POST', body: form })
  },
  profile: (id: string) => request<Profile>(`/datasets/${id}/profile`),
  rows: (id: string, page: number, revision: number) => request<RowPage>(`/datasets/${id}/rows?page=${page}&page_size=50&revision=${revision}`),
  preview: (id: string, op: Operation) => request<OperationResult>(`/datasets/${id}/operations/preview`, { method: 'POST', body: JSON.stringify(op) }),
  apply: (id: string, op: Operation) => request<OperationResult>(`/datasets/${id}/operations`, { method: 'POST', body: JSON.stringify(op) }),
  history: (id: string) => request<{ revision: number; operations: Record<string, unknown>[] }>(`/datasets/${id}/history`),
  undo: (id: string, revision: number) => request<{ revision: number }>(`/datasets/${id}/undo?expected_revision=${revision}`, { method: 'POST' }),
  reset: (id: string, revision: number) => request<{ revision: number }>(`/datasets/${id}/reset?expected_revision=${revision}`, { method: 'POST' }),
  chart: (id: string, payload: object) => request<{ kind: string; revision: number; data: { label?: string; value?: number; x?: number; y?: number }[]; sample_size?: number; seed?: number }>(`/datasets/${id}/charts`, { method: 'POST', body: JSON.stringify(payload) }),
  export: async (id: string, format: string, revision: number) => {
    const response = await fetch(`${base}/datasets/${id}/exports`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Workspace-Token': credential }, body: JSON.stringify({ format, revision }) })
    if (!response.ok) { const payload = await response.json().catch(() => ({})); throw new Error(payload.detail ?? 'Export failed') }
    const blob = await response.blob(); const url = URL.createObjectURL(blob); const anchor = document.createElement('a'); anchor.href = url
    anchor.download = response.headers.get('Content-Disposition')?.match(/filename="?([^";]+)"?/)?.[1] ?? `tathyashala.${format}`
    anchor.click(); URL.revokeObjectURL(url)
  },
}
