import { Check, X } from 'lucide-react'
import type { OperationResult } from '../../../types'
import { Button } from '../../../components/ui/Button'
export function OperationPreview({ result, onApply, onCancel, busy }: { result: OperationResult; onApply: () => void; onCancel: () => void; busy: boolean }) {
  return <div className="preview-panel"><div className="preview-heading"><div><span className="eyebrow">PREVIEW</span><h3>Review this change</h3></div><button className="icon-button" onClick={onCancel} aria-label="Cancel preview"><X size={17}/></button></div>
    <p className="impact-line"><strong>{result.affected_cells.toLocaleString()}</strong> cells and <strong>{result.affected_rows.toLocaleString()}</strong> rows are affected.</p>
    {result.warnings.map((warning, i) => <p key={i} className="warning-note">{warning}</p>)}
    <div className="mini-preview">{result.preview.slice(0, 3).map((row, i) => <div key={i}>{Object.values(row).slice(0, 4).map((cell, j) => <span key={j}>{cell == null ? '—' : String(cell)}</span>)}</div>)}</div>
    <div className="preview-actions"><Button variant="secondary" onClick={onCancel}>Cancel</Button><Button onClick={onApply} disabled={busy}><Check size={15}/> Apply change</Button></div>
  </div>
}
