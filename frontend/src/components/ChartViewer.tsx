import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'

export function ChartViewer({ data, title }: { data: { label?: string; value?: number }[]; title: string }) {
  return <section className="chart-canvas"><div className="table-head"><div><span className="eyebrow">DATA VISUALIZATION</span><h3>{title}</h3></div></div><ResponsiveContainer width="100%" height={300}><BarChart data={data} margin={{ top: 12, right: 18, bottom: 45, left: 0 }}><CartesianGrid stroke="#e8e9e2" vertical={false}/><XAxis dataKey="label" angle={-25} textAnchor="end" height={60} tick={{ fill: '#7c8178', fontSize: 10 }}/><YAxis tick={{ fill: '#7c8178', fontSize: 11 }}/><Tooltip/><Bar dataKey="value" fill="#78977e" radius={[5, 5, 0, 0]}/></BarChart></ResponsiveContainer></section>
}
