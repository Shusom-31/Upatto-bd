import { useRef, useState } from 'react'
import { FileSpreadsheet, UploadCloud } from 'lucide-react'

export function FileUploader({ onFile, busy }: { onFile: (file: File) => void; busy: boolean }) {
  const ref = useRef<HTMLInputElement>(null); const [drag, setDrag] = useState(false)
  const accept = (file?: File) => { if (file) onFile(file) }
  return <div className={`upload-zone ${drag ? 'dragging' : ''}`} onDragOver={e => { e.preventDefault(); setDrag(true) }} onDragLeave={() => setDrag(false)} onDrop={e => { e.preventDefault(); setDrag(false); accept(e.dataTransfer.files[0]) }}>
    <input ref={ref} type="file" accept=".csv,.xlsx" hidden onChange={e => accept(e.target.files?.[0])}/>
    <div className="upload-icon"><UploadCloud size={24}/></div><h3>{busy ? 'Reading your file…' : 'Drop a file to get started'}</h3><p>or <button className="text-button" disabled={busy} onClick={() => ref.current?.click()}>browse files</button> on your device</p>
    <button className="button button-secondary browse-button" disabled={busy} onClick={() => ref.current?.click()}><FileSpreadsheet size={16}/> Choose a spreadsheet</button>
    <div className="file-types"><span>.CSV</span><span>.XLSX</span><span>Up to 20 MB</span></div>
  </div>
}
