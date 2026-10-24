import { useState } from 'react'
import { api } from '../../../lib/apiClient'
import type { Operation, OperationResult } from '../../../types'

export function useCleaning(datasetId: string, revision: number, reload: () => Promise<void>) {
  const [preview, setPreview] = useState<OperationResult | null>(null)
  const [busy, setBusy] = useState(false)
  async function prepare(operation: Operation) { setBusy(true); try { setPreview(await api.preview(datasetId, operation)) } finally { setBusy(false) } }
  async function apply(operation: Operation) { setBusy(true); try { await api.apply(datasetId, operation); setPreview(null); await reload() } finally { setBusy(false) } }
  return { preview, setPreview, busy, prepare, apply, revision }
}
