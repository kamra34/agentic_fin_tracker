import { useState, useEffect } from 'react'
import { getAdminUsers, getAdminLoginHistory, getAdminActivity } from '../services/api'
import './Admin.css'

// Backend stores naive UTC timestamps; make sure JS parses them as UTC, then show local time.
function fmtTime(s) {
  if (!s) return '—'
  const iso = /[zZ]|[+\-]\d{2}:\d{2}$/.test(s) ? s : s + 'Z'
  const d = new Date(iso)
  return isNaN(d.getTime()) ? s : d.toLocaleString()
}

// Map an API path to a friendly "page" name (the SPA only tells the backend which API it called).
function pathToPage(path) {
  if (!path) return '—'
  const rules = [
    [/\/api\/expenses\/monthly/, 'Monthly'],
    [/\/api\/expenses/, 'Expenses'],
    [/\/api\/dashboard/, 'Dashboard'],
    [/\/api\/savings/, 'Savings'],
    [/\/api\/incomes/, 'Income'],
    [/\/api\/accounts/, 'Accounts'],
    [/\/api\/categories|\/api\/subcategories/, 'Categories'],
    [/\/api\/chat/, 'Chat (AI)'],
    [/\/api\/auth\/profile/, 'Profile'],
    [/\/api\/auth\/me/, 'Session check'],
  ]
  for (const [re, label] of rules) if (re.test(path)) return label
  return path
}

function Admin() {
  const [users, setUsers] = useState([])
  const [logins, setLogins] = useState([])
  const [activity, setActivity] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        const [u, l, a] = await Promise.all([
          getAdminUsers(),
          getAdminLoginHistory({ limit: 100 }),
          getAdminActivity({ limit: 200 }),
        ])
        setUsers(Array.isArray(u) ? u : [])
        setLogins(Array.isArray(l) ? l : [])
        setActivity(Array.isArray(a) ? a : [])
        setError('')
      } catch (e) {
        setError(e.message?.includes('403') || e.message?.toLowerCase().includes('privile')
          ? "You don't have access to the admin area."
          : (e.message || 'Failed to load admin data'))
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <div className="loading">Loading admin…</div>
  if (error) {
    return (
      <div className="admin-page">
        <h2 className="page-title">Admin</h2>
        <div className="admin-error">{error}</div>
      </div>
    )
  }

  return (
    <div className="admin-page">
      <div className="page-header">
        <h2 className="page-title">Admin — Users & Sessions</h2>
        <p className="page-subtitle">Login history and activity. Times shown in your local timezone.</p>
      </div>

      {/* Users */}
      <div className="admin-section">
        <h3 className="admin-section-title">Users</h3>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>User</th><th>Email</th><th>Role</th><th>Last login</th>
                <th className="num">Logins</th><th className="num">Actions</th><th>Status</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr><td colSpan={7} className="muted">No users yet.</td></tr>
              ) : users.map(u => (
                <tr key={u.id}>
                  <td>{u.full_name}</td>
                  <td className="muted">{u.email}</td>
                  <td>{u.is_superuser ? <span className="badge badge-admin">admin</span> : <span className="badge">user</span>}</td>
                  <td>{fmtTime(u.last_login)}</td>
                  <td className="num">{u.login_count}</td>
                  <td className="num">{u.activity_count}</td>
                  <td>{u.is_active ? 'active' : <span className="muted">inactive</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Login history */}
      <div className="admin-section">
        <h3 className="admin-section-title">Login history <span className="count-pill">{logins.length}</span></h3>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr><th>When</th><th>User</th><th>Device</th><th>IP</th><th>Result</th></tr>
            </thead>
            <tbody>
              {logins.length === 0 ? (
                <tr><td colSpan={5} className="muted">No logins recorded yet.</td></tr>
              ) : logins.map(l => (
                <tr key={l.id}>
                  <td>{fmtTime(l.created_at)}</td>
                  <td>{l.user_name || l.email || '—'}</td>
                  <td title={l.user_agent || ''}>{l.device || '—'}</td>
                  <td className="muted">{l.ip_address || '—'}</td>
                  <td>{l.success
                    ? <span className="badge badge-ok">success</span>
                    : <span className="badge badge-fail">failed</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Activity */}
      <div className="admin-section">
        <h3 className="admin-section-title">Activity <span className="count-pill">{activity.length}</span></h3>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr><th>When</th><th>User</th><th>Page</th><th>Request</th><th className="num">Status</th></tr>
            </thead>
            <tbody>
              {activity.length === 0 ? (
                <tr><td colSpan={5} className="muted">No activity recorded yet.</td></tr>
              ) : activity.map(a => (
                <tr key={a.id}>
                  <td>{fmtTime(a.created_at)}</td>
                  <td>{a.user_name || a.email || '—'}</td>
                  <td>{pathToPage(a.path)}</td>
                  <td className="muted" title={a.path}>{a.method} {a.path}</td>
                  <td className="num">{a.status_code}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Admin
