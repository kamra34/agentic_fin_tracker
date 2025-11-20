import { useState, useEffect } from 'react'
import { getDashboardStats, getIncomeTemplates, getExpenseTemplates } from '../services/api'
import { useCurrency } from '../context/CurrencyContext'
import './Dashboard.css'

function Dashboard() {
  const { formatAmount } = useCurrency()
  const [stats, setStats] = useState({
    total_expenses: 0,
    expense_count: 0,
    active_expense_count: 0
  })
  const [incomeTemplates, setIncomeTemplates] = useState([])
  const [expenseTemplates, setExpenseTemplates] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      setLoading(true)
      const [dashboardData, incomesData, expensesData] = await Promise.all([
        getDashboardStats(),
        getIncomeTemplates(),
        getExpenseTemplates()
      ])
      setStats(dashboardData)
      setIncomeTemplates(incomesData)
      setExpenseTemplates(expensesData)
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const calculateTotalMonthlyIncome = () => {
    return incomeTemplates.reduce((sum, income) => sum + (income.current_amount || 0), 0)
  }

  const calculateTotalRecurringExpenses = () => {
    return expenseTemplates.reduce((sum, expense) => sum + (expense.amount || 0), 0)
  }

  const calculateNetMonthly = () => {
    return calculateTotalMonthlyIncome() - calculateTotalRecurringExpenses()
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <div className="dashboard">
      <h2 className="page-title">Dashboard</h2>

      {/* KPI Dashboard */}
      <div className="kpi-dashboard">
        <div className="kpi-card kpi-primary">
          <div className="kpi-label">MONTHLY INCOME</div>
          <div className="kpi-value">{formatAmount(calculateTotalMonthlyIncome())}</div>
          <div className="kpi-sublabel">{incomeTemplates.length} active sources</div>
        </div>

        <div className="kpi-card kpi-danger">
          <div className="kpi-label">RECURRING EXPENSES</div>
          <div className="kpi-value">{formatAmount(calculateTotalRecurringExpenses())}</div>
          <div className="kpi-sublabel">{expenseTemplates.length} monthly obligations</div>
        </div>

        <div className={`kpi-card ${calculateNetMonthly() >= 0 ? 'kpi-success' : 'kpi-warning'}`}>
          <div className="kpi-label">NET MONTHLY</div>
          <div className="kpi-value">{formatAmount(calculateNetMonthly())}</div>
          <div className="kpi-sublabel">After recurring expenses</div>
        </div>
      </div>

      {/* Original Stats Grid */}
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
