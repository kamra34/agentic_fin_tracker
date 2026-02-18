import { useState, useEffect } from 'react'
import {
  getMonthlyInitialData,
  getMonthlyAllData,
  createExpense,
  updateExpense,
  deleteExpense,
  getSubcategories,
  generateMonthlyIncomes,
  createMonthlyIncome,
  updateMonthlyIncome,
  deleteMonthlyIncome,
  generateExpensesFromTemplates
} from '../services/api'
import { useCurrency } from '../context/CurrencyContext'
import './MonthlyExpenses.css'

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

function MonthlyExpenses() {
  const { formatAmount } = useCurrency()
  const currentDate = new Date()
  const currentYear = currentDate.getFullYear()
  const currentMonth = currentDate.getMonth() + 1
  const [selectedYear, setSelectedYear] = useState(currentYear)
  const [selectedMonth, setSelectedMonth] = useState(currentMonth)
  const [expenses, setExpenses] = useState([])
  const [summary, setSummary] = useState({ total: 0, count: 0, by_category: {} })
  const [availableMonths, setAvailableMonths] = useState([])
  const [categories, setCategories] = useState([])
  const [subcategories, setSubcategories] = useState([])
  const [accounts, setAccounts] = useState([])
  const [accountAllocation, setAccountAllocation] = useState({ allocations: [] })
  const [monthlyIncomes, setMonthlyIncomes] = useState([])
  const [incomeTotal, setIncomeTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [showIncomeForm, setShowIncomeForm] = useState(false)
  const [showExpenseModal, setShowExpenseModal] = useState(false)
  const [showIncomeModal, setShowIncomeModal] = useState(false)
  const [editingExpense, setEditingExpense] = useState(null)
  const [editingIncome, setEditingIncome] = useState(null)
  const [formData, setFormData] = useState({
    date: '',
    category_id: '',
    subcategory_id: '',
    custom_subcategory: '', // For manual text entry
    amount: '',
    status: true,
    account_id: ''
  })
  const [incomeFormData, setIncomeFormData] = useState({
    source_name: '',
    amount: '',
    description: ''
  })
  const [expenseFilters, setExpenseFilters] = useState({
    category_id: '',
    account_id: '',
    search: ''
  })

  const isCurrentMonth = selectedYear === currentYear && selectedMonth === currentMonth

  const getMonthOptionsForYear = (year) => {
    const months = availableMonths
      .filter(m => m.year === year)
      .map(m => m.month)

    // Always keep current and selected month visible in dropdowns, even without expense rows.
    if (year === currentYear) {
      months.push(currentMonth)
    }
    if (year === selectedYear) {
      months.push(selectedMonth)
    }

    return [...new Set(months)].sort((a, b) => b - a)
  }

  const yearOptions = [...new Set([...availableMonths.map(m => m.year), currentYear, selectedYear])]
    .sort((a, b) => b - a)
  const monthOptions = getMonthOptionsForYear(selectedYear)

  useEffect(() => {
    loadInitialData()
  }, [])

  useEffect(() => {
    if (selectedYear && selectedMonth) {
      loadMonthlyData()
    }
  }, [selectedYear, selectedMonth])

  const loadInitialData = async () => {
    try {
      // Use combined endpoint - reduces 3 API calls to 1
      const data = await getMonthlyInitialData()
      setAvailableMonths(data.months)
      setCategories(data.categories)
      setAccounts(data.accounts)
    } catch (error) {
      console.error('Error loading initial data:', error)
    }
  }

  const loadMonthlyData = async () => {
    try {
      setLoading(true)
      // Use combined endpoint - reduces 5 API calls to 1
      const data = await getMonthlyAllData(selectedYear, selectedMonth)
      setExpenses(data.expenses)
      setSummary(data.summary)
      setAccountAllocation(data.allocation)
      setMonthlyIncomes(data.incomes)
      setIncomeTotal(data.income_total.total || 0)
    } catch (error) {
      console.error('Error loading monthly data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleMonthChange = (year, month) => {
    setSelectedYear(year)
    setSelectedMonth(month)
    setShowAddForm(false)
    setEditingExpense(null)
  }

  const handlePreviousMonth = () => {
    let newMonth = selectedMonth - 1
    let newYear = selectedYear
    if (newMonth < 1) {
      newMonth = 12
      newYear -= 1
    }
    handleMonthChange(newYear, newMonth)
  }

  const handleNextMonth = () => {
    let newMonth = selectedMonth + 1
    let newYear = selectedYear
    if (newMonth > 12) {
      newMonth = 1
      newYear += 1
    }
    // Don't allow future months
    const futureDate = new Date(newYear, newMonth - 1)
    if (futureDate <= currentDate) {
      handleMonthChange(newYear, newMonth)
    }
  }

  const handleFormChange = async (e) => {
    const { name, value, type, checked } = e.target
    const newFormData = {
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    }
    setFormData(newFormData)

    // Load subcategories when category changes
    if (name === 'category_id' && value) {
      try {
        const category = categories.find(c => c.id === parseInt(value))
        if (category && category.subcategories) {
          setSubcategories(category.subcategories)
        } else {
          const subs = await getSubcategories(value)
          setSubcategories(subs)
        }
      } catch (error) {
        console.error('Error loading subcategories:', error)
      }
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    // Validate that payment account is selected
    if (!formData.account_id) {
      alert('Please select a payment account')
      return
    }

    try {
      const expenseData = {
        category_id: parseInt(formData.category_id),
        amount: parseFloat(formData.amount),
        account_id: parseInt(formData.account_id)
      }

      // Handle subcategory: use custom text if provided, otherwise use selected ID
      if (formData.custom_subcategory && formData.custom_subcategory.trim()) {
        // User entered custom text - use the old text field
        expenseData.subcategory = formData.custom_subcategory.trim()
        expenseData.subcategory_id = null
      } else if (formData.subcategory_id) {
        // User selected from dropdown
        expenseData.subcategory_id = parseInt(formData.subcategory_id)
      } else {
        // No subcategory
        expenseData.subcategory_id = null
      }

      // Only include date and status for create operations, not updates
      if (!editingExpense) {
        expenseData.date = formData.date || getDefaultDate()
        expenseData.status = formData.status
      }

      if (editingExpense) {
        await updateExpense(editingExpense.id, expenseData)
      } else {
        await createExpense(expenseData)
      }

      // Refresh data
      await loadMonthlyData()

      // Reset form
      setShowAddForm(false)
      setShowExpenseModal(false)
      setEditingExpense(null)
      resetForm()
    } catch (error) {
      console.error('Error saving expense:', error)
      alert('Failed to save expense: ' + (error.message || 'Unknown error'))
    }
  }

  const handleEdit = (expense) => {
    setEditingExpense(expense)
    setFormData({
      date: expense.date,
      category_id: expense.category_id?.toString() || '',
      subcategory_id: expense.subcategory_id?.toString() || '',
      custom_subcategory: expense.subcategory || '', // Load custom text if exists
      amount: expense.amount.toString(),
      status: expense.status !== undefined ? expense.status : true,
      account_id: expense.account_id?.toString() || ''
    })
    setShowExpenseModal(true)
    // Load subcategories for the category
    if (expense.category_id) {
      const category = categories.find(c => c.id === expense.category_id)
      if (category && category.subcategories) {
        setSubcategories(category.subcategories)
      } else {
        getSubcategories(expense.category_id).then(setSubcategories)
      }
    }
  }

  const handleDelete = async (expenseId) => {
    if (window.confirm('Are you sure you want to delete this expense?')) {
      try {
        await deleteExpense(expenseId)
        await loadMonthlyData()
      } catch (error) {
        console.error('Error deleting expense:', error)
        alert('Failed to delete expense')
      }
    }
  }

  const handleCancelForm = () => {
    setShowAddForm(false)
    setShowExpenseModal(false)
    setEditingExpense(null)
    resetForm()
  }

  const resetForm = () => {
    setFormData({
      date: '',
      category_id: '',
      subcategory_id: '',
      custom_subcategory: '',
      amount: '',
      status: true,
      account_id: ''
    })
    setSubcategories([])
  }

  const getDefaultDate = () => {
    const year = selectedYear
    const month = String(selectedMonth).padStart(2, '0')
    const day = String(currentDate.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  // Income handlers
  const handleGenerateIncome = async () => {
    try {
      const monthStr = `${selectedYear}-${String(selectedMonth).padStart(2, '0')}`
      await generateMonthlyIncomes(monthStr)
      await loadMonthlyData()
      alert('Income generated successfully from templates!')
    } catch (error) {
      console.error('Error generating income:', error)
      alert('Failed to generate income: ' + (error.message || 'Unknown error'))
    }
  }

  const handleAddOneTimeIncome = () => {
    setEditingIncome(null)
    setIncomeFormData({ source_name: '', amount: '', description: '' })
    setShowIncomeModal(true)
  }

  const handleEditIncome = (income) => {
    setEditingIncome(income)
    setIncomeFormData({
      source_name: income.source_name,
      amount: income.amount.toString(),
      description: income.description || ''
    })
    setShowIncomeModal(true)
  }

  const handleIncomeSubmit = async (e) => {
    e.preventDefault()
    try {
      const monthStr = `${selectedYear}-${String(selectedMonth).padStart(2, '0')}`
      if (editingIncome) {
        await updateMonthlyIncome(editingIncome.id, {
          source_name: incomeFormData.source_name,
          amount: parseFloat(incomeFormData.amount),
          description: incomeFormData.description
        })
      } else {
        await createMonthlyIncome({
          month: monthStr,
          source_name: incomeFormData.source_name,
          amount: parseFloat(incomeFormData.amount),
          is_one_time: true,
          description: incomeFormData.description
        })
      }
      setShowIncomeModal(false)
      setEditingIncome(null)
      setIncomeFormData({ source_name: '', amount: '', description: '' })
      await loadMonthlyData()
    } catch (error) {
      console.error('Error saving income:', error)
      alert('Failed to save income: ' + (error.message || 'Unknown error'))
    }
  }

  const handleDeleteIncome = async (incomeId) => {
    if (window.confirm('Are you sure you want to delete this income entry?')) {
      try {
        await deleteMonthlyIncome(incomeId)
        await loadMonthlyData()
      } catch (error) {
        console.error('Error deleting income:', error)
        alert('Failed to delete income')
      }
    }
  }

  const handleCancelIncomeForm = () => {
    setShowIncomeModal(false)
    setEditingIncome(null)
    setIncomeFormData({ source_name: '', amount: '', description: '' })
  }

  // Expense template handler
  const handleGenerateExpenses = async () => {
    try {
      await generateExpensesFromTemplates(selectedYear, selectedMonth)
      await loadMonthlyData()
      alert('Expenses generated successfully from templates!')
    } catch (error) {
      console.error('Error generating expenses:', error)
      alert('Failed to generate expenses: ' + (error.message || 'Unknown error'))
    }
  }

  // Filter expenses based on selected filters
  const filteredExpenses = expenses.filter(expense => {
    // Category filter
    if (expenseFilters.category_id && expense.category_id !== parseInt(expenseFilters.category_id)) {
      return false
    }
    // Account filter
    if (expenseFilters.account_id && expense.account_id !== parseInt(expenseFilters.account_id)) {
      return false
    }
    // Search filter (searches in category name, subcategory name, and account name)
    if (expenseFilters.search) {
      const searchLower = expenseFilters.search.toLowerCase()
      const categoryMatch = (expense.category_name || '').toLowerCase().includes(searchLower)
      const subcategoryMatch = (expense.subcategory_name || '').toLowerCase().includes(searchLower)
      const accountMatch = (expense.account_name || '').toLowerCase().includes(searchLower)
      if (!categoryMatch && !subcategoryMatch && !accountMatch) {
        return false
      }
    }
    return true
  })

  const handleResetFilters = () => {
    setExpenseFilters({
      category_id: '',
      account_id: '',
      search: ''
    })
  }

  if (loading && expenses.length === 0) {
    return <div className="loading">Loading...</div>
  }

  return (
    <div className="monthly-expenses">
      <div className="page-header">
        <h2 className="page-title">Monthly Expenses</h2>
      </div>

      {/* Modern Month & Year Selector */}
      <div className="month-year-selector-card">
        <div className="selector-header">
          <div className="selector-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2"/>
              <path d="M3 10H21" stroke="currentColor" strokeWidth="2"/>
              <path d="M8 2V6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <path d="M16 2V6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
          <h3 className="selector-title">Select Period</h3>
          {isCurrentMonth && <span className="current-badge">Current Month</span>}
        </div>

        <div className="selector-controls">
          <div className="selector-group">
            <label htmlFor="year-select">Year</label>
            <select
              id="year-select"
              value={selectedYear}
              onChange={(e) => {
                const year = parseInt(e.target.value)
                const monthsInYear = getMonthOptionsForYear(year)
                const month = monthsInYear.length > 0
                  ? monthsInYear[0]
                  : (year === currentYear ? currentMonth : 1)
                handleMonthChange(year, month)
              }}
              className="year-select"
            >
              {yearOptions.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>

          <div className="selector-divider"></div>

          <div className="selector-group selector-group-month">
            <label htmlFor="month-select">Month</label>
            <select
              id="month-select"
              value={selectedMonth}
              onChange={(e) => handleMonthChange(selectedYear, parseInt(e.target.value))}
              className="month-select"
            >
              {monthOptions.map(month => (
                <option key={month} value={month}>
                  {MONTH_NAMES[month - 1]}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="selected-period-display">
          <span className="period-label">Selected Period:</span>
          <span className="period-value">{MONTH_NAMES[selectedMonth - 1]} {selectedYear}</span>
        </div>

        {/* Compact KPI Chips */}
        <div className="kpi-chips-container">
          <div className="kpi-chip kpi-income">
            <div className="kpi-icon">↑</div>
            <div className="kpi-content">
              <span className="kpi-label">Income</span>
              <span className="kpi-value">{formatAmount(incomeTotal)}</span>
            </div>
          </div>

          <div className="kpi-chip kpi-expenses">
            <div className="kpi-icon">↓</div>
            <div className="kpi-content">
              <span className="kpi-label">Expenses</span>
              <span className="kpi-value">{formatAmount(summary.total)}</span>
            </div>
          </div>

          <div className={`kpi-chip kpi-net ${incomeTotal - summary.total >= 0 ? 'kpi-positive' : 'kpi-negative'}`}>
            <div className="kpi-icon">{incomeTotal - summary.total >= 0 ? '✓' : '⚠'}</div>
            <div className="kpi-content">
              <span className="kpi-label">Net</span>
              <span className="kpi-value">{formatAmount(incomeTotal - summary.total)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Payment Account Allocation with Animated Flow */}
      {accountAllocation.allocations && accountAllocation.allocations.length > 0 && (
        <div className="account-allocation-flow-section">
          <div className="flow-section-header">
            <h3 className="flow-section-title">Payment Allocations</h3>
            <p className="flow-section-subtitle">Money flow to accounts</p>
          </div>
          <div className="allocation-flow-container">
            {accountAllocation.allocations
              .filter(allocation => allocation.total_amount > 0)
              .map((allocation, index) => (
                <div key={index} className="allocation-flow-row">
                  <div className="flow-amount">
                    <span className="amount-value">{formatAmount(allocation.total_amount)}</span>
                    <span className="amount-label">{allocation.expense_count} {allocation.expense_count === 1 ? 'expense' : 'expenses'}</span>
                  </div>
                  <div className="flow-arrow-container">
                    <div className="flow-arrow">
                      <div className="arrow-line"></div>
                      <div className="arrow-head"></div>
                      <div className="arrow-particles"></div>
                    </div>
                  </div>
                  <div className="flow-account">
                    <span className="account-name">{allocation.account_name || 'Unassigned'}</span>
                    {allocation.owner_name && (
                      <span className="account-owner">{allocation.owner_name}</span>
                    )}
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Income Section */}
      <div className="income-section">
        <div className="section-header">
          <h3>Income for {MONTH_NAMES[selectedMonth - 1]} {selectedYear}</h3>
          <div className="income-actions">
            <button onClick={handleGenerateIncome} className="btn-generate">
              Generate from Templates
            </button>
            <button onClick={handleAddOneTimeIncome} className="btn-add-income">
              + Add One-Time Income
            </button>
          </div>
        </div>

        {showIncomeForm && !editingIncome && (
          <div className="income-form-card">
            <h4>Add One-Time Income</h4>
            <form onSubmit={handleIncomeSubmit} className="income-form">
              <div className="form-group">
                <label htmlFor="income-source">Source Name</label>
                <input
                  type="text"
                  id="income-source"
                  value={incomeFormData.source_name}
                  onChange={(e) => setIncomeFormData({ ...incomeFormData, source_name: e.target.value })}
                  required
                  placeholder="e.g., Bonus, Freelance Project"
                />
              </div>
              <div className="form-group">
                <label htmlFor="income-amount">Amount</label>
                <input
                  type="number"
                  id="income-amount"
                  step="0.01"
                  min="0"
                  value={incomeFormData.amount}
                  onChange={(e) => setIncomeFormData({ ...incomeFormData, amount: e.target.value })}
                  placeholder="e.g., 5000"
                />
              </div>
              <div className="form-group">
                <label htmlFor="income-description">Description (Optional)</label>
                <input
                  type="text"
                  id="income-description"
                  value={incomeFormData.description}
                  onChange={(e) => setIncomeFormData({ ...incomeFormData, description: e.target.value })}
                  placeholder="Additional details"
                />
              </div>
              <div className="form-actions">
                <button type="submit" className="btn-submit">
                  Add Income
                </button>
                <button type="button" onClick={handleCancelIncomeForm} className="btn-cancel">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {monthlyIncomes.length > 0 ? (
          <div className="income-list">
            {monthlyIncomes.map((income) => (
              <div key={income.id} className="income-item">
                <div className="income-info">
                  <div className="income-source">
                    {income.source_name}
                    {income.is_one_time && <span className="one-time-badge">One-time</span>}
                    {!income.is_one_time && <span className="recurring-badge">Recurring</span>}
                  </div>
                  {income.description && (
                    <div className="income-description">{income.description}</div>
                  )}
                </div>
                <div className="income-amount">{formatAmount(income.amount)}</div>
                <div className="income-actions">
                  <button onClick={() => handleEditIncome(income)} className="btn-edit-small">
                    Edit
                  </button>
                  <button onClick={() => handleDeleteIncome(income.id)} className="btn-delete-small">
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>No income recorded for this month.</p>
            <p>Click "Generate from Templates" to create income from your recurring sources, or add one-time income manually.</p>
          </div>
        )}
      </div>


      {/* Expenses Section */}
      <div className="expenses-section">
        <div className="section-header">
          <h3>Expenses for {MONTH_NAMES[selectedMonth - 1]} {selectedYear}</h3>
          {isCurrentMonth && (
            <div className="expense-actions">
              <button onClick={handleGenerateExpenses} className="btn-generate">
                Generate from Templates
              </button>
              <button onClick={() => setShowExpenseModal(true)} className="btn-add-expense">
                + Add Expense
              </button>
            </div>
          )}
        </div>

        {/* Filters Section */}
        {expenses.length > 0 && (
          <div className="filters-section">
            <div className="filters-row">
              <div className="filter-group">
                <label htmlFor="filter-category">Filter by Category</label>
                <select
                  id="filter-category"
                  value={expenseFilters.category_id}
                  onChange={(e) => setExpenseFilters({ ...expenseFilters, category_id: e.target.value })}
                  className="filter-select"
                >
                  <option value="">All Categories</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label htmlFor="filter-account">Filter by Account</label>
                <select
                  id="filter-account"
                  value={expenseFilters.account_id}
                  onChange={(e) => setExpenseFilters({ ...expenseFilters, account_id: e.target.value })}
                  className="filter-select"
                >
                  <option value="">All Accounts</option>
                  {accounts.map((acc) => (
                    <option key={acc.id} value={acc.id}>{acc.name} - {acc.owner_name}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label htmlFor="filter-search">Search</label>
                <input
                  type="text"
                  id="filter-search"
                  value={expenseFilters.search}
                  onChange={(e) => setExpenseFilters({ ...expenseFilters, search: e.target.value })}
                  placeholder="Search category, subcategory, or account..."
                  className="filter-input"
                />
              </div>

              <div className="filter-group filter-actions">
                <label>&nbsp;</label>
                <button onClick={handleResetFilters} className="btn-reset-filters">
                  Reset Filters
                </button>
              </div>
            </div>
            <div className="filter-results">
              Showing {filteredExpenses.length} of {expenses.length} expenses
            </div>
          </div>
        )}

        {expenses.length === 0 ? (
          <p className="empty-state">No expenses for this month</p>
        ) : filteredExpenses.length === 0 ? (
          <p className="empty-state">No expenses match your filters</p>
        ) : (
          <div className="expenses-table">
            <div className="table-header">
              <div className="col-date">Date</div>
              <div className="col-category">Category</div>
              <div className="col-subcategory">Subcategory</div>
              <div className="col-amount">Amount</div>
              <div className="col-account">Payment Account</div>
              {isCurrentMonth && <div className="col-actions">Actions</div>}
            </div>
            {filteredExpenses.map((expense) => (
              <div key={expense.id} className="table-row">
                <div className="col-date">{expense.date}</div>
                <div className="col-category">{expense.category_name || expense.category || '-'}</div>
                <div className="col-subcategory">{expense.subcategory_name || expense.subcategory || '-'}</div>
                <div className="col-amount">{formatAmount(expense.amount)}</div>
                <div className="col-account">{expense.account_name || '-'}</div>
                {isCurrentMonth && (
                  <div className="col-actions">
                    <button onClick={() => handleEdit(expense)} className="btn-edit">
                      Edit
                    </button>
                    <button onClick={() => handleDelete(expense.id)} className="btn-delete">
                      Delete
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Edit Income Modal */}
      {showIncomeModal && (
        <div className="modal-overlay" onClick={handleCancelIncomeForm}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingIncome ? 'Edit Income' : 'Add One-Time Income'}</h3>
              <button className="modal-close" onClick={handleCancelIncomeForm}>
                &times;
              </button>
            </div>

            <form onSubmit={handleIncomeSubmit}>
              <div className="form-group">
                <label htmlFor="modal-income-source">Source Name</label>
                <input
                  type="text"
                  id="modal-income-source"
                  value={incomeFormData.source_name}
                  onChange={(e) => setIncomeFormData({ ...incomeFormData, source_name: e.target.value })}
                  required
                  className="form-input"
                  placeholder="e.g., Bonus, Freelance Project"
                />
              </div>
              <div className="form-group">
                <label htmlFor="modal-income-amount">Amount</label>
                <input
                  type="number"
                  id="modal-income-amount"
                  step="0.01"
                  min="0"
                  value={incomeFormData.amount}
                  onChange={(e) => setIncomeFormData({ ...incomeFormData, amount: e.target.value })}
                  required
                  className="form-input"
                  placeholder="e.g., 5000"
                />
              </div>
              <div className="form-group">
                <label htmlFor="modal-income-description">Description (Optional)</label>
                <input
                  type="text"
                  id="modal-income-description"
                  value={incomeFormData.description}
                  onChange={(e) => setIncomeFormData({ ...incomeFormData, description: e.target.value })}
                  className="form-input"
                  placeholder="Additional details"
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={handleCancelIncomeForm}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  {editingIncome ? 'Update' : 'Add'} Income
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add/Edit Expense Modal */}
      {showExpenseModal && (
        <div className="modal-overlay" onClick={handleCancelForm}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingExpense ? 'Edit Expense' : 'Add New Expense'}</h3>
              <button className="modal-close" onClick={handleCancelForm}>
                &times;
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="modal-date">Date</label>
                  <input
                    type="date"
                    id="modal-date"
                    name="date"
                    value={formData.date || getDefaultDate()}
                    onChange={handleFormChange}
                    required
                    max={`${selectedYear}-${String(selectedMonth).padStart(2, '0')}-31`}
                    min={`${selectedYear}-${String(selectedMonth).padStart(2, '0')}-01`}
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="modal-amount">Amount</label>
                  <input
                    type="number"
                    id="modal-amount"
                    name="amount"
                    value={formData.amount}
                    onChange={handleFormChange}
                    step="0.01"
                    min="0"
                    required
                    placeholder="0.00"
                    className="form-input"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="modal-category_id">Category</label>
                  <select
                    id="modal-category_id"
                    name="category_id"
                    value={formData.category_id}
                    onChange={handleFormChange}
                    required
                    className="form-input"
                  >
                    <option value="">Select a category</option>
                    {categories.map((cat) => (
                      <option key={cat.id} value={cat.id}>
                        {cat.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="modal-subcategory_id">Subcategory (Optional)</label>
                  <select
                    id="modal-subcategory_id"
                    name="subcategory_id"
                    value={formData.subcategory_id}
                    onChange={(e) => {
                      handleFormChange(e)
                      // Clear custom text when selecting from dropdown
                      if (e.target.value) {
                        setFormData(prev => ({ ...prev, custom_subcategory: '' }))
                      }
                    }}
                    className="form-input"
                    disabled={!formData.category_id || (subcategories.length === 0 && !formData.custom_subcategory)}
                  >
                    <option value="">Select a subcategory</option>
                    {subcategories.map((sub) => (
                      <option key={sub.id} value={sub.id}>
                        {sub.name}
                      </option>
                    ))}
                  </select>
                  <div style={{ margin: '0.5rem 0', textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                    — or —
                  </div>
                  <input
                    type="text"
                    id="modal-custom-subcategory"
                    name="custom_subcategory"
                    value={formData.custom_subcategory}
                    onChange={(e) => {
                      handleFormChange(e)
                      // Clear dropdown when typing custom text
                      if (e.target.value) {
                        setFormData(prev => ({ ...prev, subcategory_id: '' }))
                      }
                    }}
                    placeholder="Or type custom subcategory..."
                    className="form-input"
                    disabled={!formData.category_id}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="modal-account_id">Payment Account</label>
                <select
                  id="modal-account_id"
                  name="account_id"
                  value={formData.account_id}
                  onChange={handleFormChange}
                  required
                  className="form-input"
                >
                  <option value="">Select a payment account</option>
                  {accounts.map((account) => (
                    <option key={account.id} value={account.id}>
                      {account.name} ({account.owner_name})
                    </option>
                  ))}
                </select>
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={handleCancelForm}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  {editingExpense ? 'Update' : 'Add'} Expense
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default MonthlyExpenses
