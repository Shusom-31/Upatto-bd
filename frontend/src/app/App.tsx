import { useEffect, useState } from 'react'
import { ArrowDownToLine, ArrowRight, Check, Clock3, FileSpreadsheet, Leaf, LockKeyhole, RotateCcw, Sparkles, WandSparkles } from 'lucide-react'
import { api, clearCredential, saveSession, storedSession } from '../lib/apiClient'
import type { Dataset, Operation, Profile, RowPage, Session } from '../types'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { FileUploader } from '../components/FileUploader'
import { DataTable } from '../components/DataTable'
import { WorkspaceLayout } from '../layouts/WorkspaceLayout'
import { OperationPanel } from '../features/cleaning/components/OperationPanel'
import { OperationPreview } from '../features/cleaning/components/OperationPreview'
import { useCleaning } from '../features/cleaning/hooks/useCleaning'
import { ResponsiveContainer, BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, ScatterChart, Scatter } from 'recharts'

type Section = 'overview' | 'clean' | 'charts' | 'exports' | 'help'

export default function App() {
  const [session, setSession] = useState<Session | null>(() => storedSession())
  const [dataset, setDataset] = useState<Dataset | null>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [page, setPage] = useState<RowPage | null>(null)
  const [section, setSection] = useState<Section>('overview')
  const [name, setName] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [chartKind, setChartKind] = useState('bar')
  const [chartX, setChartX] = useState('')
  const [chartY, setChartY] = useState('')
  const [chartData, setChartData] = useState<{ label?: string; value?: number; x?: number; y?: number }[]>([])
  const [chartNote, setChartNote] = useState('')
  const [history, setHistory] = useState<Record<string, unknown>[]>([])

  async function reload(pageNo = page?.page ?? 1) {
    if (!dataset) return
    const nextProfile = await api.profile(dataset.dataset_id)
    const [nextPage, nextHistory] = await Promise.all([api.rows(dataset.dataset_id, pageNo, nextProfile.revision), api.history(dataset.dataset_id)])
    setProfile(nextProfile); setPage(nextPage); setHistory(nextHistory.operations)
    setDataset(current => current ? { ...current, revision: nextProfile.revision, rows: nextProfile.rows, columns: nextProfile.columns } : current)
  }
  useEffect(() => { if (dataset) void reload().catch(e => setError(e.message)) }, [dataset?.dataset_id])
  const cleaning = useCleaning(dataset?.dataset_id ?? '', profile?.revision ?? dataset?.revision ?? 0, () => reload())

  async function beginWorkspace() {
    setError(''); if (!name.trim()) { setError('Please enter your name to start.'); return }
    setBusy(true)
    try { const created = await api.start(name.trim()); saveSession(created); setSession(created) }
    catch (e) { setError(message(e)) } finally { setBusy(false) }
  }
  async function upload(file: File) {
    if (!session) return
    setError(''); setBusy(true)
    try {
      const { sheets } = await api.inspect(session.session_id, file)
      let selectedSheet: string | undefined
      if (sheets.length > 1) {
        const selected = window.prompt(`This workbook has ${sheets.length} worksheets:\n${sheets.map((sheet, index) => `${index + 1}. ${sheet}`).join('\n')}\n\nEnter the worksheet name to use:`, sheets[0])
        if (selected === null) { setBusy(false); return }
        if (!sheets.includes(selected.trim())) throw new Error('Enter one of the worksheet names shown.')
        selectedSheet = selected.trim()
      }
      const next = await api.upload(session.session_id, file, selectedSheet)
      setDataset(next); setSection('overview')
      setNotice(`${file.name} is ready to explore`); window.setTimeout(() => setNotice(''), 4500)
    } catch (e) { setError(message(e)) } finally { setBusy(false) }
  }
  async function endWorkspace() {
    if (session) { try { await api.end(session.session_id) } catch { /* expired workspaces are already cleared */ } }
    clearCredential(); setSession(null); setDataset(null); setProfile(null); setPage(null); setError('')
  }
  async function pageTo(pageNo: number) { if (!dataset || !profile) return; try { setPage(await api.rows(dataset.dataset_id, pageNo, profile.revision)) } catch (e) { setError(message(e)) } }
  async function preview(op: Operation) { setError(''); try { await cleaning.prepare(op) } catch (e) { setError(message(e)) } }
  async function applyPreview() {
    if (!cleaning.preview || !dataset) return
    const config = lastOperation
    if (!config) return
    try { await cleaning.apply(config); setNotice('Your changes have been applied.'); window.setTimeout(() => setNotice(''), 4000) } catch (e) { setError(message(e)) }
  }
  const [lastOperation, setLastOperation] = useState<Operation | null>(null)
  function requestPreview(op: Operation) { setLastOperation(op); void preview(op) }
  async function undo() { if (!dataset || !profile) return; setError(''); try { await api.undo(dataset.dataset_id, profile.revision); await reload(1); setNotice('Previous change undone.') } catch (e) { setError(message(e)) } }
  async function reset() { if (!dataset || !profile || !window.confirm('Reset this dataset to its original upload?')) return; setError(''); try { await api.reset(dataset.dataset_id, profile.revision); await reload(1); setNotice('Dataset restored to the original upload.') } catch (e) { setError(message(e)) } }
  async function createChart() {
    if (!dataset || !profile || !chartX) return
    setError('')
    try {
      const kind = chartKind === 'scatter' ? 'scatter' : chartKind === 'histogram' ? 'histogram' : chartKind === 'line' ? 'line' : 'bar'
      const result = await api.chart(dataset.dataset_id, { kind, x: chartX, ...(chartY ? { y: chartY } : {}), aggregation: chartY ? 'mean' : 'count', revision: profile.revision })
      setChartData(result.data); setChartNote(result.sample_size ? `Showing ${result.sample_size.toLocaleString()} points · sample seed ${result.seed}` : `${result.data.length} groups · revision ${result.revision}`)
    } catch (e) { setError(message(e)) }
  }
  async function exportFile(format: string) { if (!dataset || !profile) return; setError(''); try { await api.export(dataset.dataset_id, format, profile.revision); setNotice(`${format.toUpperCase()} download is ready.`) } catch (e) { setError(message(e)) } }

  if (!session) return <div className="welcome-page"><div className="welcome-nav"><a className="brand" href="#"><span className="brand-mark"><Leaf size={19}/></span><span>Tathyashala<small>DATA, MADE CLEAR</small></span></a><span className="secure-tag"><LockKeyhole size={13}/> Private by design</span></div><div className="welcome-content"><div className="welcome-copy"><span className="welcome-kicker"><span/> A QUIETER WAY TO WORK WITH DATA</span><h1>Make sense of your<br/><em>spreadsheets.</em></h1><p>Clean up the messy bits, find the story in your data, and share work you feel good about.</p><div className="welcome-points"><div><span><WandSparkles size={17}/></span><p><b>Clean with confidence</b><small>See what changes before you apply them.</small></p></div><div><span><Sparkles size={17}/></span><p><b>Understand what you have</b><small>Spot gaps and patterns in a clear overview.</small></p></div><div><span><ArrowDownToLine size={17}/></span><p><b>Take your work with you</b><small>Download a tidy file or shareable report.</small></p></div></div></div><div className="welcome-card"><div className="card-step">YOUR WORKSPACE <span>01 / 02</span></div><h2>Start with your name</h2><p>We’ll use it to personalize your workspace. No account needed.</p><label className="field-label">Your name<Input autoFocus value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Shahriar" onKeyDown={e => e.key === 'Enter' && void beginWorkspace()}/></label>{error && <div className="alert error">{error}</div>}<Button className="wide-button" onClick={() => void beginWorkspace()} disabled={busy}>{busy ? 'Creating workspace…' : <>Start my workspace <ArrowRight size={17}/></>}</Button><div className="card-foot"><LockKeyhole size={13}/> Guest workspace · clears automatically after 60 minutes</div></div></div><div className="welcome-bottom"><span>MADE FOR THE MOMENT BEFORE THE ANALYSIS</span><span>CSV + EXCEL · NO CODE REQUIRED</span></div></div>

  return <WorkspaceLayout name={session.display_name} fileName={dataset?.dataset_name} section={section} onSection={setSection} onEnd={() => void endWorkspace()}><div className="content-wrap">
    {error && <div className="alert error"><span>{error}</span><button onClick={() => setError('')}>×</button></div>}{notice && <div className="alert success"><Check size={16}/>{notice}<button onClick={() => setNotice('')}>×</button></div>}
    {!dataset ? <div className="upload-view"><div className="page-intro"><div><div className="eyebrow">YOUR WORKSPACE IS READY</div><h1>Let’s bring your data in.</h1><p>Hi {session.display_name}, upload a spreadsheet and we’ll take a first look together.</p></div><div className="step-badge"><span>STEP 1 OF 4</span><strong>Upload a file</strong></div></div><div className="upload-grid"><FileUploader onFile={upload} busy={busy}/><aside className="upload-aside"><span className="aside-icon"><FileSpreadsheet size={18}/></span><h3>A small note before we begin</h3><p>We read the values in your file to build a preview. Your workspace is temporary, and your original upload stays as a reference while you work.</p><div className="aside-divider"/><div className="format-line"><Check size={14}/> Excel workbooks (.xlsx)</div><div className="format-line"><Check size={14}/> Comma separated files (.csv)</div><div className="format-line"><Clock3 size={14}/> Up to 20 MB · 60 minute session</div></aside></div></div>
      : profile && page && <>
        {section === 'overview' && <><div className="page-intro"><div><div className="eyebrow">A CLEAR FIRST LOOK</div><h1>Good to see you, {session.display_name}.</h1><p>Here’s what we found in <strong>{dataset.dataset_name}</strong>. Take a look around before making changes.</p></div><div className="step-badge complete"><Check size={15}/><span>FILE READY</span></div></div><div className="metric-grid"><Metric label="Total rows" value={profile.rows} helper="In your current dataset" tone="sage"/><Metric label="Columns" value={profile.columns} helper={`${profile.columns_with_issues} with missing values`} tone="lavender"/><Metric label="Empty cells" value={profile.missing_cells} helper={`${(profile.missing_rate * 100).toFixed(1)}% of all cells`} tone="sand"/><Metric label="Duplicate rows" value={profile.duplicate_rows} helper="Across every column" tone="rose"/></div><div className="overview-bottom"><div className="column-card"><div className="table-head"><div><span className="eyebrow">COLUMN GUIDE</span><h3>What’s in this file</h3></div><span className="subtle-count">{profile.column_profiles.length} columns</span></div><div className="column-list">{profile.column_profiles.map(col => <div className="column-item" key={col.name}><span className={`type-icon ${col.inferred_type}`}>{col.inferred_type === 'numeric' ? '#' : col.inferred_type === 'date' ? '◷' : 'Aa'}</span><span className="column-name"><b>{col.name}</b><small>{col.inferred_type} · {col.unique} unique values</small></span><span className={col.missing ? 'missing-badge' : 'clean-badge'}>{col.missing ? `${col.missing} empty` : 'Looks good'}</span></div>)}</div><button className="inline-link" onClick={() => setSection('clean')}>Explore cleaning options <ArrowRight size={15}/></button></div><DataTable page={page} onPage={pageTo}/></div></>}
        {section === 'clean' && <><div className="page-intro"><div><div className="eyebrow">A LITTLE TIDYING</div><h1>Clean, one step at a time.</h1><p>Choose an operation, preview its impact, then decide if it feels right.</p></div><div className="revision-badge"><span className="revision-dot"/> Revision {profile.revision}</div></div><div className="cleaning-grid"><OperationPanel columns={profile.column_profiles} revision={profile.revision} busy={cleaning.busy} onPreview={requestPreview}/><div className="cleaning-main">{cleaning.preview ? <OperationPreview result={cleaning.preview} busy={cleaning.busy} onCancel={() => cleaning.setPreview(null)} onApply={() => void applyPreview()}/> : <div className="calm-card"><div className="calm-icon"><Sparkles size={19}/></div><div><h3>Nothing changes until you say so.</h3><p>Every operation starts with a preview. Your original upload stays here, and you can undo any applied step.</p></div></div>}<DataTable page={page} onPage={pageTo}/></div></div><HistoryPanel history={history} onUndo={() => void undo()} onReset={() => void reset()} revision={profile.revision}/></>}
        {section === 'charts' && <><div className="page-intro"><div><div className="eyebrow">LOOK FOR A PATTERN</div><h1>Your data, in a different light.</h1><p>Build a simple chart from the current revision. The preview keeps the dataset itself on the server.</p></div><div className="revision-badge"><span className="revision-dot"/> Revision {profile.revision}</div></div><div className="chart-builder"><div className="chart-controls"><label>Chart style<select className="select" value={chartKind} onChange={e => setChartKind(e.target.value)}><option value="bar">Category counts</option><option value="histogram">Numeric distribution</option><option value="scatter">Scatter plot</option></select></label><label>{chartKind === 'scatter' ? 'X axis' : chartKind === 'histogram' ? 'Number column' : 'Category'}<select className="select" value={chartX} onChange={e => setChartX(e.target.value)}><option value="">Choose a column</option>{profile.column_profiles.map(col => <option key={col.name}>{col.name}</option>)}</select></label>{chartKind === 'scatter' && <label>Y axis<select className="select" value={chartY} onChange={e => setChartY(e.target.value)}><option value="">Choose a number</option>{profile.column_profiles.map(col => <option key={col.name}>{col.name}</option>)}</select></label>}<Button onClick={() => void createChart()} disabled={!chartX || busy}><Sparkles size={15}/> Make chart</Button></div><div className="chart-canvas">{chartData.length ? <><div className="table-head"><div><span className="eyebrow">CURRENT REVISION · {profile.revision}</span><h3>{chartX}{chartY ? ` and ${chartY}` : ''}</h3></div><span className="subtle-count">{chartNote}</span></div><ResponsiveContainer width="100%" height={320}>{chartKind === 'scatter' ? <ScatterChart margin={{ top: 12, right: 18, bottom: 10, left: 0 }}><CartesianGrid stroke="#e8e9e2" strokeDasharray="4 4"/><XAxis dataKey="x" type="number" name={chartX} tick={{ fill: '#7c8178', fontSize: 11 }}/><YAxis dataKey="y" type="number" name={chartY} tick={{ fill: '#7c8178', fontSize: 11 }}/><Tooltip/><Scatter data={chartData} fill="#688a71"/></ScatterChart> : <BarChart data={chartData} margin={{ top: 12, right: 18, bottom: 55, left: 0 }}><CartesianGrid stroke="#e8e9e2" vertical={false}/><XAxis dataKey="label" angle={-28} textAnchor="end" interval={0} height={75} tick={{ fill: '#7c8178', fontSize: 10 }}/><YAxis tick={{ fill: '#7c8178', fontSize: 11 }}/><Tooltip/><Bar dataKey="value" fill="#78977e" radius={[5, 5, 0, 0]} maxBarSize={46}/></BarChart>}</ResponsiveContainer></> : <div className="chart-empty"><div className="chart-empty-icon"><Sparkles size={20}/></div><h3>Your chart will appear here</h3><p>Pick a column, then make a chart from the current dataset revision.</p></div>}</div></div></>}
        {section === 'exports' && <><div className="page-intro"><div><div className="eyebrow">READY WHEN YOU ARE</div><h1>Take your work with you.</h1><p>Downloads are generated from revision {profile.revision} of your current dataset.</p></div><div className="step-badge complete"><Check size={15}/><span>REVISION {profile.revision}</span></div></div><div className="export-grid"><ExportCard icon="xlsx" title="Cleaned Excel workbook" detail="Cleaned data, a short summary and your operation log." tag=".XLSX" onClick={() => void exportFile('xlsx')}/><ExportCard icon="csv" title="Simple CSV" detail="A portable, UTF-8 copy of your current data." tag=".CSV" onClick={() => void exportFile('csv')}/><ExportCard icon="pdf" title="PDF summary report" detail="A compact overview and cleaning history for sharing." tag=".PDF" onClick={() => void exportFile('pdf')}/></div><div className="export-footnote"><LockKeyhole size={15}/><span>All files reflect the same frozen revision. Spreadsheet formulas, macros, formatting and layout are not included in this value-based export.</span></div></>}
        {section === 'help' && <div className="help-view"><div className="eyebrow">A QUICK GUIDE</div><h1>A few things to know.</h1><div className="help-cards"><Help title="Your data stays yours" text="Workspaces are temporary guest sessions. We keep your upload as an unchanged reference while you explore; sessions clear after 60 minutes without activity."/><Help title="Preview before changing" text="Cleaning operations show how many rows and cells are affected. Apply creates a new revision; Undo steps back, and Reset returns to the original upload."/><Help title="Understand the limits" text="This MVP handles CSV and value-based XLSX files. Workbook styling, formulas, macros, machine-learning preparation and Excel templates are not included yet."/></div><Button variant="secondary" onClick={() => setSection('overview')}>Back to overview</Button></div>}
      </>}
    </div></WorkspaceLayout>
}

function Metric({ label, value, helper, tone }: { label: string; value: number; helper: string; tone: string }) { return <div className={`metric-card ${tone}`}><div className="metric-top"><span>{label}</span><span className="metric-spark">↗</span></div><strong>{value.toLocaleString()}</strong><small>{helper}</small></div> }
function HistoryPanel({ history, onUndo, onReset, revision }: { history: Record<string, unknown>[]; onUndo: () => void; onReset: () => void; revision: number }) { return <section className="history-card"><div className="history-heading"><div><span className="eyebrow">YOUR WORK SO FAR</span><h3>Operation history</h3></div><div className="history-actions"><Button variant="secondary" onClick={onUndo} disabled={!history.some(item => item.operation !== 'undo' && item.operation !== 'reset')}><RotateCcw size={14}/> Undo</Button><button className="text-button" onClick={onReset} disabled={revision === 0}>Reset to original</button></div></div>{history.length ? <div className="history-list">{history.slice().reverse().slice(0, 6).map((item, i) => <div className="history-item" key={`${item.revision}-${i}`}><span className="history-check"><Check size={13}/></span><span><b>{String(item.operation).replace(/_/g, ' ')}</b><small>{Array.isArray(item.columns) && item.columns.length ? item.columns.join(', ') : 'All columns'}</small></span><span className="history-count">{Number(item.affected_cells ?? item.affected_rows ?? 0).toLocaleString()} affected · rev {String(item.revision)}</span></div>)}</div> : <p className="empty-history">No changes yet. Your operation history will show here.</p>}</section> }
function ExportCard({ icon, title, detail, tag, onClick }: { icon: string; title: string; detail: string; tag: string; onClick: () => void }) { return <button className="export-card" onClick={onClick}><div className={`export-icon ${icon}`}>{icon === 'xlsx' ? <FileSpreadsheet size={20}/> : icon === 'csv' ? <ArrowDownToLine size={20}/> : <FileSpreadsheet size={20}/>}<span>{tag}</span></div><div className="export-card-copy"><h3>{title}</h3><p>{detail}</p></div><span className="export-arrow"><ArrowDownToLine size={17}/></span></button> }
function Help({ title, text }: { title: string; text: string }) { return <article className="help-card"><span className="help-bullet"><Check size={15}/></span><div><h3>{title}</h3><p>{text}</p></div></article> }
function message(error: unknown) { return error instanceof Error ? error.message : 'Something went wrong. Please try again.' }
