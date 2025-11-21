import { useState, useEffect } from 'react'
import { getDashboardInitialData, getExpenseAnalytics } from '../services/api'
import { useCurrency } from '../context/CurrencyContext'
import ExpenseKPICard from '../components/ExpenseKPICard'
import SavingsKPICard from '../components/SavingsKPICard'
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
  const [savingsSummary, setSavingsSummary] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
    fetchAnalytics()
  }, [])

  const fetchStats = async () => {
    try {
      setLoading(true)
      // Use combined endpoint - reduces 3 API calls to 1
      const data = await getDashboardInitialData()
      setStats(data.stats)
      setIncomeTemplates(data.income_templates)
      setExpenseTemplates(data.expense_templates)
      setSavingsSummary(data.savings_summary)
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchAnalytics = async () => {
    try {
      const data = await getExpenseAnalytics()
      setAnalytics(data)
    } catch (error) {
      console.error('Error fetching analytics:', error)
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

  const getTotalSavingsValue = () => {
    return savingsSummary?.total_value || 0
  }

  const getTotalInvestments = () => {
    if (!savingsSummary || !savingsSummary.accounts_by_type) return 0
    const investment = savingsSummary.accounts_by_type['investment']
    const crypto = savingsSummary.accounts_by_type['crypto']
    return (investment?.value || 0) + (crypto?.value || 0)
  }

  const getTotalSavingsOnly = () => {
    if (!savingsSummary || !savingsSummary.accounts_by_type) return 0
    const bankSavings = savingsSummary.accounts_by_type['bank_savings']
    return bankSavings?.value || 0
  }

  return (
    <div className="dashboard">
      {/* First Row KPIs */}
      <div className="kpi-dashboard">
        <div className="kpi-card kpi-primary">
          <div className="kpi-label">MONTHLY INCOME</div>
          <div className="kpi-value">{formatAmount(calculateTotalMonthlyIncome())}</div>
          <div className="kpi-sublabel">{incomeTemplates.length} active sources</div>
        </div>

        <div className="kpi-card kpi-danger">
          <div className="kpi-label">MONTHLY RECURRING EXPENSES</div>
          <div className="kpi-value">{formatAmount(calculateTotalRecurringExpenses())}</div>
          <div className="kpi-sublabel">{expenseTemplates.length} monthly obligations</div>
        </div>

        <div className={`kpi-card ${calculateNetMonthly() >= 0 ? 'kpi-success' : 'kpi-warning'}`}>
          <div className="kpi-label">NET MONTHLY</div>
          <div className="kpi-value">{formatAmount(calculateNetMonthly())}</div>
          <div className="kpi-sublabel">After recurring expenses</div>
        </div>
      </div>

      {/* Second Row KPIs */}
      <div className="kpi-dashboard kpi-dashboard-secondary">
        <div className="kpi-card kpi-investments">
          <div className="kpi-label">TOTAL INVESTMENTS</div>
          <div className="kpi-value">{formatAmount(getTotalInvestments())}</div>
          <div className="kpi-sublabel">Stocks & Crypto</div>
        </div>

        <div className="kpi-card kpi-savings">
          <div className="kpi-label">TOTAL SAVINGS</div>
          <div className="kpi-value">{formatAmount(getTotalSavingsOnly())}</div>
          <div className="kpi-sublabel">Bank savings accounts</div>
        </div>

        <div className={`kpi-card ${savingsSummary?.total_profit_loss >= 0 ? 'kpi-profit' : 'kpi-loss'}`}>
          <div className="kpi-label">INVESTMENT RETURN</div>
          <div className="kpi-value">
            {savingsSummary?.total_profit_loss >= 0 ? '+' : ''}{formatAmount(savingsSummary?.total_profit_loss || 0)}
          </div>
          <div className="kpi-sublabel">
            {savingsSummary?.total_profit_loss >= 0 ? '+' : ''}{savingsSummary?.profit_loss_percentage || 0}% return
          </div>
        </div>
      </div>

      {/* Savings & Investments Section */}
      {savingsSummary && (
        <div className="analytics-section">
          <h3 className="section-title">Savings & Investments</h3>
          <div className="analytics-grid">
            <SavingsKPICard savingsSummary={savingsSummary} />
          </div>
        </div>
      )}

      {/* Rich Expense Analytics KPI Card */}
      {analytics && (
        <div className="analytics-section">
          <h3 className="section-title">Expense Analytics</h3>
          <div className="analytics-grid">
            <ExpenseKPICard analytics={analytics} />
          </div>
        </div>
      )}

    </div>
  )
}

export default Dashboard
