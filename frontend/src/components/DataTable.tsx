import { ChevronLeft, ChevronRight } from 'lucide-react'
import type { RowPage } from '../types'

export function DataTable({ page, onPage }: { page: RowPage; onPage: (next: number) => void }) {
  return <section className="table-card">
    <div className="table-head"><div><span className="eyebrow">DATA PREVIEW</span><h3>Your rows, at a glance</h3></div><span className="row-count">{page.total_rows.toLocaleString()} rows</span></div>
    <div className="table-scroll"><table><thead><tr><th className="index-cell">#</th>{page.columns.map(col => <th key={col}>{col}</th>)}</tr></thead>
      <tbody>{page.rows.map((row, ri) => <tr key={ri}><td className="index-cell">{(page.page - 1) * page.page_size + ri + 1}</td>{page.columns.map(col => <td key={col}>{row[col] === null || row[col] === undefined || row[col] === '' ? <span className="empty-value">Empty</span> : String(row[col])}</td>)}</tr>)}</tbody>
    </table></div>
    <div className="pagination"><span>Showing {page.total_rows ? (page.page - 1) * page.page_size + 1 : 0}–{Math.min(page.page * page.page_size, page.total_rows)} of {page.total_rows.toLocaleString()}</span><div><button aria-label="Previous page" disabled={page.page <= 1} onClick={() => onPage(page.page - 1)}><ChevronLeft size={16}/></button><span className="page-number">{page.page}</span><button aria-label="Next page" disabled={page.page * page.page_size >= page.total_rows} onClick={() => onPage(page.page + 1)}><ChevronRight size={16}/></button></div></div>
  </section>
}
