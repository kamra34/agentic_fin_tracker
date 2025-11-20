import { useState, useEffect } from 'react'
import {
  getMonthlyExpenses,
  getMonthlySummary,
  getAvailableMonths,
  createExpense,
  updateExpense,
  deleteExpense,
  getExpenseCategories,
  getExpenseSubcategories
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
  const [loading, setLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [editingExpense, setEditingExpense] = useState(null)
  const [formData, setFormData] = useState({
    date: '',
    category: '',
    subcategory: '',
    amount: '',
    status: true
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
      const [months, cats] = await Promise.all([
        getAvailableMonths(),
        getExpenseCategories()
      ])
      setAvailableMonths(months)
      setCategories(cats)
    } catch (error) {
      console.error('Error loading initial data:', error)
    }
  }

  const loadMonthlyData = async () => {
    try {
      setLoading(true)
      const [expensesData, summaryData] = await Promise.all([
        getMonthlyExpenses(selectedYear, selectedMonth),
        getMonthlySummary(selectedYear, selectedMonth)
      ])
      setExpenses(expensesData)
      setSummary(summaryData)
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
    if (name === 'category' && value) {
      try {
        const subs = await getExpenseSubcategories(value)
        setSubcategories(subs)
      } catch (error) {
        console.error('Error loading subcategories:', error)
      }
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const expenseData = {
        ...formData,
        date: formData.date || getDefaultDate(),
        amount: parseFloat(formData.amount),
        subcategory: formData.subcategory || null
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
      category: expense.category,
      subcategory: expense.subcategory || '',
      amount: expense.amount.toString(),
      status: expense.status
    })
    setShowAddForm(true)
    // Load subcategories for the category
    if (expense.category) {
      getExpenseSubcategories(expense.category).then(setSubcategories)
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
      category: '',
      subcategory: '',
      amount: '',
      status: true
    })
    setSubcategories([])
  }

  const getDefaultDate = () => {
    const year = selectedYear
    const month = String(selectedMonth).padStart(2, '0')
    const day = String(currentDate.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
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
          <h4>Total Expenses</h4>
          <p className="summary-value">{formatAmount(summary.total)}</p>
        </div>
        <div className="summary-card">
          <h4>Count</h4>
          <p className="summary-value">{summary.count}</p>
        </div>
        <div className="summary-card">
          <h4>Categories</h4>
          <p className="summary-value">{Object.keys(summary.by_category || {}).length}</p>
        </div>
      </div>

      {/* Add Expense Button (only for current month) */}
      {isCurrentMonth && !showAddForm && (
        <button onClick={() => setShowAddForm(true)} className="btn-add-expense">
          + Add Expense
        </button>
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
                <label htmlFor="category">Category</label>
                <input
                  type="text"
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleFormChange}
                  required
                  list="categories-list"
                  placeholder="Enter or select category"
                  className="form-input"
                />
                <datalist id="categories-list">
                  {categories.map((cat) => (
                    <option key={cat} value={cat} />
                  ))}
                </datalist>
              </div>

              <div className="form-group">
                <label htmlFor="subcategory">Subcategory (Optional)</label>
                <input
                  type="text"
                  id="subcategory"
                  name="subcategory"
                  value={formData.subcategory}
                  onChange={handleFormChange}
                  list="subcategories-list"
                  placeholder="Enter or select subcategory"
                  className="form-input"
                />
                <datalist id="subcategories-list">
                  {subcategories.map((sub) => (
                    <option key={sub} value={sub} />
                  ))}
                </datalist>
              </div>
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
              <div className="col-status">Status</div>
              {isCurrentMonth && <div className="col-actions">Actions</div>}
            </div>
            {expenses.map((expense) => (
              <div key={expense.id} className="table-row">
                <div className="col-date">{expense.date}</div>
                <div className="col-category">{expense.category}</div>
                <div className="col-subcategory">{expense.subcategory || '-'}</div>
                <div className="col-amount">{formatAmount(expense.amount)}</div>
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
