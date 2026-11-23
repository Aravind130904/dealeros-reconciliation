import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './style.css'

const API = 'http://127.0.0.1:8000/api'
const reasons = ['', 'MISSING_IN_B', 'ORPHAN_IN_B', 'DUPLICATE_IN_B', 'VALUE_MISMATCH', 'LOCATION_MISMATCH', 'DATE_MISMATCH']

function money(value) {
  if (value === null || value === undefined || value === '') return '—'
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(Number(value))
}

function App() {
  const [orgs, setOrgs] = useState([])
  const [org, setOrg] = useState('ORG-A')
  const [reason, setReason] = useState('')
  const [sort, setSort] = useState('')
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch(`${API}/orgs/`).then(r => r.json()).then(data => {
      setOrgs(data.organizations || [])
      if (data.organizations?.length) setOrg(data.organizations[0])
    }).catch(() => setError('Could not connect to backend. Start Django on port 8000.'))
  }, [])

  useEffect(() => {
    if (!org) return
    setLoading(true)
    setError('')
    const params = new URLSearchParams({ org })
    if (reason) params.set('reason', reason)
    if (sort) params.set('sort', sort)
    fetch(`${API}/disagreements/?${params}`)
      .then(async response => {
        const data = await response.json()
        if (!response.ok) throw new Error(data.error || 'Request failed')
        setRows(data.results || [])
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [org, reason, sort])

  return <main className="app">
    <header className="header">
      <div><div className="eyebrow">DEALEROS · DATA QUALITY</div><h1>Reconciliation</h1><p>Compare records from System A and System B.</p></div>
      <div className="org-picker"><label htmlFor="org">Organization</label><select id="org" value={org} onChange={e => setOrg(e.target.value)}>{orgs.map(o => <option key={o}>{o}</option>)}</select></div>
    </header>
    <section className="toolbar">
      <label>Filter by reason<select value={reason} onChange={e => setReason(e.target.value)}><option value="">All disagreements</option>{reasons.slice(1).map(r => <option key={r} value={r}>{r.replaceAll('_', ' ')}</option>)}</select></label>
      <button className="sort" onClick={() => setSort(prev => prev === 'value' ? '-value' : 'value')}>Sort by A value {sort === 'value' ? '↑' : sort === '-value' ? '↓' : '↕'}</button>
      <div className="count">{rows.length} disagreement{rows.length !== 1 ? 's' : ''}</div>
    </section>
    {error && <div className="error">{error}</div>}
    <section className="table-wrap"><table><thead><tr><th>Reason</th><th>Record ID</th><th>Location</th><th>System A</th><th>System B</th><th>Difference</th></tr></thead><tbody>
      {loading ? <tr><td colSpan="6" className="empty">Loading…</td></tr> : rows.length === 0 ? <tr><td colSpan="6" className="empty">No disagreements found for this filter.</td></tr> : rows.map((row, i) => <tr key={`${row.record_id}-${row.reason}-${i}`}>
        <td><span className={`badge ${row.reason.toLowerCase()}`}>{row.reason.replaceAll('_', ' ')}</span></td><td className="record">{row.record_id}</td><td>{row.location || '—'}</td><td>{money(row.a_value)}</td><td>{money(row.b_value)}</td><td className={row.difference && Number(row.difference) !== 0 ? 'negative' : ''}>{money(row.difference)}</td>
      </tr>)}
    </tbody></table></section>
    <footer>Tenant data is filtered by organization on the backend before comparison.</footer>
  </main>
}

createRoot(document.getElementById('root')).render(<App />)
