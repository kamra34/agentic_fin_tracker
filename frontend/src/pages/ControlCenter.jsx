import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  getCategoriesWithStats,
  getAccountsWithStats,
  getIncomeTemplates,
  getExpenseTemplates
} from '../services/api'
import { useCurrency } from '../context/CurrencyContext'
import './ControlCenter.css'

function ControlCenter() {
  const navigate = useNavigate()
  const { formatAmount } = useCurrency()
  const [stats, setStats] = useState({
    categories: [],
    accounts: [],
    incomeTemplates: [],
    expenseTemplates: []
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      const [categoriesData, accountsData, incomesData, expenseTemplatesData] = await Promise.all([
        getCategoriesWithStats(),
        getAccountsWithStats(),
        getIncomeTemplates(),
        getExpenseTemplates()
      ])
      setStats({
        categories: categoriesData,
        accounts: accountsData,
        incomeTemplates: incomesData,
        expenseTemplates: expenseTemplatesData
      })
    } catch (error) {
      console.error('Error loading control center data:', error)
    } finally {
      setLoading(false)
    }
  }

  const calculateTotalMonthlyIncome = () => {
    return stats.incomeTemplates.reduce((sum, income) => sum + (income.current_amount || 0), 0)
  }

  const calculateTotalRecurringExpenses = () => {
    return stats.expenseTemplates.reduce((sum, expense) => sum + (expense.amount || 0), 0)
  }

  const calculateNetMonthly = () => {
    return calculateTotalMonthlyIncome() - calculateTotalRecurringExpenses()
  }

  const modules = [
    {
      id: 'categories',
      title: 'Categories',
      description: 'Organize expenses and income into categories',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M4 6H20M4 12H20M4 18H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          <circle cx="7" cy="6" r="1" fill="currentColor"/>
          <circle cx="7" cy="12" r="1" fill="currentColor"/>
          <circle cx="7" cy="18" r="1" fill="currentColor"/>
        </svg>
      ),
      count: stats.categories.length,
      countLabel: 'Categories',
      route: '/management/categories',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: '#667eea'
    },
    {
      id: 'income',
      title: 'Income Sources',
      description: 'Manage recurring income streams',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      ),
      count: stats.incomeTemplates.length,
      countLabel: 'Sources',
      subtitle: formatAmount(calculateTotalMonthlyIncome()),
      subtitleLabel: 'Monthly Total',
      route: '/management/income',
      gradient: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
      color: '#10b981'
    },
    {
      id: 'recurring',
      title: 'Recurring Expenses',
      description: 'Set up automatic monthly expenses',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
          <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        </svg>
      ),
      count: stats.expenseTemplates.length,
      countLabel: 'Templates',
      subtitle: formatAmount(calculateTotalRecurringExpenses()),
      subtitleLabel: 'Monthly Total',
      route: '/management/recurring',
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
      color: '#f59e0b'
    },
    {
      id: 'accounts',
      title: 'Payment Accounts',
      description: 'Track spending across accounts',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="2" y="5" width="20" height="14" rx="2" stroke="currentColor" strokeWidth="2"/>
          <path d="M2 10H22" stroke="currentColor" strokeWidth="2"/>
          <path d="M6 15H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        </svg>
      ),
      count: stats.accounts.length,
      countLabel: 'Accounts',
      route: '/management/accounts',
      gradient: 'linear-gradient(135deg, #06b6d4 0%, #22d3ee 100%)',
      color: '#06b6d4'
    }
  ]

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading Control Center...</p>
      </div>
    )
  }

  return (
    <div className="control-center">
      {/* Header */}
      <div className="cc-header">
        <div className="cc-header-content">
          <h1 className="cc-title">Control Center</h1>
          <p className="cc-subtitle">Your complete financial overview and system configuration</p>
        </div>
      </div>

      {/* Statistics Overview Boxes */}
      <div className="stats-section">
        <h2 className="stats-section-title">System Overview</h2>
        <div className="stats-boxes-grid">
          <div className="stats-box stats-box-categories">
            <div className="stats-box-header">
              <div className="stats-box-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M4 6H20M4 12H20M4 18H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <circle cx="7" cy="6" r="1" fill="currentColor"/>
                  <circle cx="7" cy="12" r="1" fill="currentColor"/>
                  <circle cx="7" cy="18" r="1" fill="currentColor"/>
                </svg>
              </div>
              <span className="stats-box-label">Categories</span>
            </div>
            <div className="stats-box-number">{stats.categories.length}</div>
            <div className="stats-box-footer">Total categories</div>
          </div>

          <div className="stats-box stats-box-income">
            <div className="stats-box-header">
              <div className="stats-box-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <span className="stats-box-label">Income Sources</span>
            </div>
            <div className="stats-box-number">{stats.incomeTemplates.length}</div>
            <div className="stats-box-footer">Active income sources</div>
          </div>

          <div className="stats-box stats-box-recurring">
            <div className="stats-box-header">
              <div className="stats-box-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                  <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </div>
              <span className="stats-box-label">Recurring Expenses</span>
            </div>
            <div className="stats-box-number">{stats.expenseTemplates.length}</div>
            <div className="stats-box-footer">Active recurring expenses</div>
          </div>

          <div className="stats-box stats-box-accounts">
            <div className="stats-box-header">
              <div className="stats-box-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="2" y="5" width="20" height="14" rx="2" stroke="currentColor" strokeWidth="2"/>
                  <path d="M2 10H22" stroke="currentColor" strokeWidth="2"/>
                  <path d="M6 15H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </div>
              <span className="stats-box-label">Payment Accounts</span>
            </div>
            <div className="stats-box-number">{stats.accounts.length}</div>
            <div className="stats-box-footer">Total payment accounts</div>
          </div>
        </div>
      </div>

      {/* Modules Grid */}
      <div className="modules-section">
        <h2 className="modules-title">Management Modules</h2>
        <div className="modules-grid">
          {modules.map((module) => (
            <div
              key={module.id}
              className="module-card"
              onClick={() => navigate(module.route)}
              style={{ '--module-color': module.color }}
            >
              <div className="module-header">
                <div className="module-icon-wrapper" style={{ background: module.gradient }}>
                  {module.icon}
                </div>
                <div className="module-badge">{module.count}</div>
              </div>
              <div className="module-body">
                <h3 className="module-title">{module.title}</h3>
                <p className="module-description">{module.description}</p>
                {module.subtitle && (
                  <div className="module-stats">
                    <span className="module-stat-value">{module.subtitle}</span>
                    <span className="module-stat-label">{module.subtitleLabel}</span>
                  </div>
                )}
              </div>
              <div className="module-footer">
                <span className="module-count-label">{module.countLabel}</span>
                <svg className="module-arrow" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M7 3L14 10L7 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2 className="quick-actions-title">Quick Actions</h2>
        <div className="quick-actions-grid">
          <button className="quick-action-btn" onClick={() => navigate('/management/categories')}>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Add Category
          </button>
          <button className="quick-action-btn" onClick={() => navigate('/management/income')}>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Add Income Source
          </button>
          <button className="quick-action-btn" onClick={() => navigate('/management/recurring')}>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Add Recurring Expense
          </button>
          <button className="quick-action-btn" onClick={() => navigate('/management/accounts')}>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Add Payment Account
          </button>
        </div>
      </div>
    </div>
  )
}

export default ControlCenter
