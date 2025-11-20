import { useState, useEffect } from 'react'
import { getDashboardStats } from '../services/api'
import { useCurrency } from '../context/CurrencyContext'
import './Dashboard.css'

function Dashboard() {
  const { formatAmount } = useCurrency()
  const [stats, setStats] = useState({
    total_expenses: 0,
    expense_count: 0,
    active_expense_count: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      setLoading(true)
      const data = await getDashboardStats()
      setStats(data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <div className="dashboard">
      <h2 className="page-title">Dashboard</h2>
      <div className="stats-grid">
        <div className="stat-card expense">
          <h3>Total Expenses</h3>
          <p className="stat-value">{formatAmount(stats.total_expenses || 0)}</p>
        </div>
        <div className="stat-card transactions">
          <h3>Total Count</h3>
          <p className="stat-value">{stats.expense_count || 0}</p>
        </div>
        <div className="stat-card transactions">
          <h3>Active Expenses</h3>
          <p className="stat-value">{stats.active_expense_count || 0}</p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
