import { useState, useEffect } from 'react'
import {
  getMonthlyExpenses,
  getMonthlySummary,
  getAvailableMonths,
  createExpense,
  updateExpense,
  deleteExpense,
  getCategories,
  getSubcategories,
  getAccounts,
  getMonthlyAccountAllocation,
  getMonthlyIncomes,
  generateMonthlyIncomes,
  getMonthlyIncomeTotal,
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
  const [selectedYear, setSelectedYear] = useState(currentDate.getFullYear())
  const [selectedMonth, setSelectedMonth] = useState(currentDate.getMonth() + 1)
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
  const [editingExpense, setEditingExpense] = useState(null)
  const [editingIncome, setEditingIncome] = useState(null)
  const [formData, setFormData] = useState({
    date: '',
    category_id: '',
    subcategory_id: '',
    amount: '',
    status: true,
    account_id: ''
  })
  const [incomeFormData, setIncomeFormData] = useState({
    source_name: '',
    amount: '',
    description: ''
  })

  const isCurrentMonth = selectedYear === currentDate.getFullYear() &&
                         selectedMonth === (currentDate.getMonth() + 1)

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
      const [months, cats, accts] = await Promise.all([
        getAvailableMonths(),
        getCategories(),
        getAccounts()
      ])
      setAvailableMonths(months)
      setCategories(cats)
      setAccounts(accts)
    } catch (error) {
      console.error('Error loading initial data:', error)
    }
  }

  const loadMonthlyData = async () => {
    try {
      setLoading(true)
      const monthStr = `${selectedYear}-${String(selectedMonth).padStart(2, '0')}`
      const [expensesData, summaryData, allocationData, incomesData, totalData] = await Promise.all([
        getMonthlyExpenses(selectedYear, selectedMonth),
        getMonthlySummary(selectedYear, selectedMonth),
        getMonthlyAccountAllocation(selectedYear, selectedMonth),
        getMonthlyIncomes(monthStr),
        getMonthlyIncomeTotal(monthStr)
      ])
      setExpenses(expensesData)
      setSummary(summaryData)
      setAccountAllocation(allocationData)
      setMonthlyIncomes(incomesData)
      setIncomeTotal(totalData.total || 0)
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
        date: formData.date || getDefaultDate(),
        category_id: parseInt(formData.category_id),
        subcategory_id: formData.subcategory_id ? parseInt(formData.subcategory_id) : null,
        amount: parseFloat(formData.amount),
        status: formData.status,
        account_id: parseInt(formData.account_id)
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
      amount: expense.amount.toString(),
      status: expense.status,
      account_id: expense.account_id?.toString() || ''
    })
    setShowAddForm(true)
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
    setEditingExpense(null)
    resetForm()
  }

  const resetForm = () => {
    setFormData({
      date: '',
      category_id: '',
      subcategory_id: '',
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
    setShowIncomeForm(true)
  }

  const handleEditIncome = (income) => {
    setEditingIncome(income)
    setIncomeFormData({
      source_name: income.source_name,
      amount: income.amount.toString(),
      description: income.description || ''
    })
    setShowIncomeForm(true)
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
      setShowIncomeForm(false)
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
    setShowIncomeForm(false)
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

  if (loading && expenses.length === 0) {
    return <div className="loading">Loading...</div>
  }

  return (
    <div className="monthly-expenses">
      <div className="page-header">
        <h2 className="page-title">Monthly Expenses</h2>
      </div>

      {/* Month Navigator */}
      <div className="month-navigator">
        <button onClick={handlePreviousMonth} className="nav-btn">
          ← Previous
        </button>
        <h3 className="current-month">
          {MONTH_NAMES[selectedMonth - 1]} {selectedYear}
          {isCurrentMonth && <span className="current-badge">Current</span>}
        </h3>
        <button
          onClick={handleNextMonth}
          className="nav-btn"
          disabled={selectedYear === currentDate.getFullYear() && selectedMonth === (currentDate.getMonth() + 1)}
        >
          Next →
        </button>
      </div>

      {/* Month Selector Dropdown */}
      <div className="month-selector">
        <label>Jump to month:</label>
        <select
          value={`${selectedYear}-${selectedMonth}`}
          onChange={(e) => {
            const [year, month] = e.target.value.split('-')
            handleMonthChange(parseInt(year), parseInt(month))
          }}
          className="month-select"
        >
          {availableMonths.map((m) => (
            <option key={`${m.year}-${m.month}`} value={`${m.year}-${m.month}`}>
              {MONTH_NAMES[m.month - 1]} {m.year}
            </option>
          ))}
        </select>
      </div>

      {/* Summary Stats */}
      <div className="summary-cards">
        <div className="summary-card">
          <h4>Total Income</h4>
          <p className="summary-value" style={{ color: '#10b981' }}>{formatAmount(incomeTotal)}</p>
          <p className="summary-label">{monthlyIncomes.length} {monthlyIncomes.length === 1 ? 'source' : 'sources'}</p>
        </div>
        <div className="summary-card">
          <h4>Total Expenses</h4>
          <p className="summary-value" style={{ color: '#ef4444' }}>{formatAmount(summary.total)}</p>
          <p className="summary-label">{summary.count} {summary.count === 1 ? 'expense' : 'expenses'}</p>
        </div>
        <div className="summary-card">
          <h4>Net Income</h4>
          <p className="summary-value" style={{ color: incomeTotal - summary.total >= 0 ? '#10b981' : '#ef4444' }}>
            {formatAmount(incomeTotal - summary.total)}
          </p>
          <p className="summary-label">{incomeTotal - summary.total >= 0 ? 'Surplus' : 'Deficit'}</p>
        </div>
      </div>

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

        {showIncomeForm && (
          <div className="income-form-card">
            <h4>{editingIncome ? 'Edit Income' : 'Add One-Time Income'}</h4>
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
                  required
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
                  {editingIncome ? 'Update' : 'Add'} Income
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

      {/* Payment Account Allocation */}
      {accountAllocation.allocations && accountAllocation.allocations.length > 0 && (
        <div className="account-allocation-section">
          <h3>Payment Account Allocation</h3>
          <div className="allocation-cards">
            {accountAllocation.allocations.map((allocation, index) => (
              <div key={index} className="allocation-card">
                <div className="allocation-header">
                  <h4>{allocation.account_name || 'Unassigned'}</h4>
                  {allocation.owner_name && (
                    <span className="owner-name">{allocation.owner_name}</span>
                  )}
                </div>
                <div className="allocation-amount">{formatAmount(allocation.total_amount)}</div>
                <div className="allocation-details">
                  {allocation.expense_count} {allocation.expense_count === 1 ? 'expense' : 'expenses'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add Expense Buttons (only for current month) */}
      {isCurrentMonth && !showAddForm && (
        <div className="expense-actions">
          <button onClick={handleGenerateExpenses} className="btn-generate">
            Generate from Templates
          </button>
          <button onClick={() => setShowAddForm(true)} className="btn-add-expense">
            + Add Expense
          </button>
        </div>
      )}

      {/* Add/Edit Expense Form */}
      {showAddForm && isCurrentMonth && (
        <div className="expense-form-card">
          <h3>{editingExpense ? 'Edit Expense' : 'Add New Expense'}</h3>
          <form onSubmit={handleSubmit} className="expense-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="date">Date</label>
                <input
                  type="date"
                  id="date"
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
                <label htmlFor="amount">Amount</label>
                <input
                  type="number"
                  id="amount"
                  name="amount"
                  value={formData.amount}
                  onChange={handleFormChange}
                  required
                  step="0.01"
                  min="0"
                  placeholder="0.00"
                  className="form-input"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="category_id">Category</label>
                <select
                  id="category_id"
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
                <label htmlFor="subcategory_id">Subcategory (Optional)</label>
                <select
                  id="subcategory_id"
                  name="subcategory_id"
                  value={formData.subcategory_id}
                  onChange={handleFormChange}
                  className="form-input"
                  disabled={!formData.category_id || subcategories.length === 0}
                >
                  <option value="">Select a subcategory</option>
                  {subcategories.map((sub) => (
                    <option key={sub.id} value={sub.id}>
                      {sub.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="account_id">Payment Account</label>
              <select
                id="account_id"
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

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="status"
                  checked={formData.status}
                  onChange={handleFormChange}
                />
                <span>Active</span>
              </label>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-primary">
                {editingExpense ? 'Update Expense' : 'Save Expense'}
              </button>
              <button type="button" onClick={handleCancelForm} className="btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Expenses List */}
      <div className="expenses-list">
        <h3>Expenses ({expenses.length})</h3>
        {expenses.length === 0 ? (
          <p className="empty-state">No expenses for this month</p>
        ) : (
          <div className="expenses-table">
            <div className="table-header">
              <div className="col-date">Date</div>
              <div className="col-category">Category</div>
              <div className="col-subcategory">Subcategory</div>
              <div className="col-amount">Amount</div>
              <div className="col-account">Payment Account</div>
              <div className="col-status">Status</div>
              {isCurrentMonth && <div className="col-actions">Actions</div>}
            </div>
            {expenses.map((expense) => (
              <div key={expense.id} className="table-row">
                <div className="col-date">{expense.date}</div>
                <div className="col-category">{expense.category_name || expense.category || '-'}</div>
                <div className="col-subcategory">{expense.subcategory_name || expense.subcategory || '-'}</div>
                <div className="col-amount">{formatAmount(expense.amount)}</div>
                <div className="col-account">{expense.account_name || '-'}</div>
                <div className="col-status">
                  <span className={`status-badge ${expense.status ? 'active' : 'inactive'}`}>
                    {expense.status ? 'Active' : 'Inactive'}
                  </span>
                </div>
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
    </div>
  )
}

export default MonthlyExpenses
