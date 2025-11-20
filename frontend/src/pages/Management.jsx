import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  getCategories,
  getCategoriesWithStats,
  getAccounts,
  getAccountsWithStats,
  createCategory,
  createAccount,
  updateCategory,
  deleteCategory,
  deleteAccount,
  createSubcategory,
  updateSubcategory,
  deleteSubcategory,
  getIncomeTemplates,
  createIncomeTemplate,
  updateIncomeTemplate,
  deleteIncomeTemplate,
  getExpenseTemplates,
  createExpenseTemplate,
  updateExpenseTemplate,
  deleteExpenseTemplate
} from '../services/api'
import { useCurrency } from '../context/CurrencyContext'
import './Management.css'

function Management() {
  const navigate = useNavigate()
  const location = useLocation()
  const { formatAmount } = useCurrency()

  // Determine which section to show based on URL
  const currentPath = location.pathname
  const showCategories = currentPath.includes('/categories')
  const showIncome = currentPath.includes('/income')
  const showRecurring = currentPath.includes('/recurring')
  const showAccounts = currentPath.includes('/accounts')
  const [categories, setCategories] = useState([])
  const [accounts, setAccounts] = useState([])
  const [incomeTemplates, setIncomeTemplates] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCategoryForm, setShowCategoryForm] = useState(false)
  const [showAccountForm, setShowAccountForm] = useState(false)
  const [showIncomeForm, setShowIncomeForm] = useState(false)
  const [categoryFormData, setCategoryFormData] = useState({
    name: '',
    category_type: 'expense'
  })
  const [accountFormData, setAccountFormData] = useState({
    name: '',
    owner_name: ''
  })
  const [incomeFormData, setIncomeFormData] = useState({
    source_name: '',
    current_amount: ''
  })
  const [editingIncome, setEditingIncome] = useState(null)

  // Expense template state
  const [expenseTemplates, setExpenseTemplates] = useState([])
  const [showExpenseTemplateForm, setShowExpenseTemplateForm] = useState(false)
  const [expenseTemplateFormData, setExpenseTemplateFormData] = useState({
    name: '',
    amount: '',
    category_id: '',
    subcategory_id: '',
    account_id: ''
  })
  const [editingExpenseTemplate, setEditingExpenseTemplate] = useState(null)

  // Modal state
  const [showModal, setShowModal] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [editingCategory, setEditingCategory] = useState(false)
  const [editingSubcategory, setEditingSubcategory] = useState(null)
  const [newSubcategoryName, setNewSubcategoryName] = useState('')
  const [categoryEditData, setCategoryEditData] = useState({ name: '' })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [categoriesData, accountsData, incomesData, expenseTemplatesData] = await Promise.all([
        getCategoriesWithStats(),
        getAccountsWithStats(),
        getIncomeTemplates(),
        getExpenseTemplates()
      ])
      setCategories(categoriesData)
      setAccounts(accountsData)
      setIncomeTemplates(incomesData)
      setExpenseTemplates(expenseTemplatesData)
    } catch (error) {
      console.error('Error loading management data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCategorySubmit = async (e) => {
    e.preventDefault()
    try {
      await createCategory(categoryFormData)
      setShowCategoryForm(false)
      setCategoryFormData({ name: '', category_type: 'expense' })
      await loadData()
    } catch (error) {
      console.error('Error creating category:', error)
      alert('Failed to create category: ' + (error.message || 'Unknown error'))
    }
  }

  const handleAccountSubmit = async (e) => {
    e.preventDefault()
    try {
      await createAccount(accountFormData)
      setShowAccountForm(false)
      setAccountFormData({ name: '', owner_name: '' })
      await loadData()
    } catch (error) {
      console.error('Error creating payment account:', error)
      alert('Failed to create payment account: ' + (error.message || 'Unknown error'))
    }
  }

  const handleDeleteCategory = async (categoryId) => {
    if (window.confirm('Are you sure you want to delete this category? This cannot be undone.')) {
      try {
        await deleteCategory(categoryId)
        await loadData()
      } catch (error) {
        console.error('Error deleting category:', error)
        alert('Failed to delete category: ' + (error.message || 'Unknown error'))
      }
    }
  }

  const handleDeleteAccount = async (accountId) => {
    if (window.confirm('Are you sure you want to delete this payment account? This cannot be undone.')) {
      try {
        await deleteAccount(accountId)
        await loadData()
      } catch (error) {
        console.error('Error deleting payment account:', error)
        alert('Failed to delete payment account: ' + (error.message || 'Unknown error'))
      }
    }
  }

  const handleIncomeSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingIncome) {
        await updateIncomeTemplate(editingIncome.id, {
          source_name: incomeFormData.source_name,
          current_amount: parseFloat(incomeFormData.current_amount)
        })
        setEditingIncome(null)
      } else {
        await createIncomeTemplate({
          source_name: incomeFormData.source_name,
          current_amount: parseFloat(incomeFormData.current_amount)
        })
      }
      setShowIncomeForm(false)
      setIncomeFormData({ source_name: '', current_amount: '' })
      await loadData()
    } catch (error) {
      console.error('Error saving income source:', error)
      alert('Failed to save income source: ' + (error.message || 'Unknown error'))
    }
  }

  const handleEditIncome = (income) => {
    setIncomeFormData({
      source_name: income.source_name,
      current_amount: income.current_amount.toString()
    })
    setEditingIncome(income)
    setShowIncomeForm(true)
  }

  const handleDeleteIncome = async (incomeId) => {
    if (window.confirm('Are you sure you want to delete this income source? This will deactivate it.')) {
      try {
        await deleteIncomeTemplate(incomeId)
        await loadData()
      } catch (error) {
        console.error('Error deleting income source:', error)
        alert('Failed to delete income source: ' + (error.message || 'Unknown error'))
      }
    }
  }

  const handleCancelIncomeEdit = () => {
    setEditingIncome(null)
    setShowIncomeForm(false)
    setIncomeFormData({ source_name: '', current_amount: '' })
  }

  // Expense template handlers
  const handleExpenseTemplateSubmit = async (e) => {
    e.preventDefault()
    try {
      const data = {
        name: expenseTemplateFormData.name,
        amount: parseFloat(expenseTemplateFormData.amount),
        category_id: parseInt(expenseTemplateFormData.category_id),
        subcategory_id: expenseTemplateFormData.subcategory_id ? parseInt(expenseTemplateFormData.subcategory_id) : null,
        account_id: expenseTemplateFormData.account_id ? parseInt(expenseTemplateFormData.account_id) : null
      }

      if (editingExpenseTemplate) {
        await updateExpenseTemplate(editingExpenseTemplate.id, data)
        setEditingExpenseTemplate(null)
      } else {
        await createExpenseTemplate(data)
      }

      setShowExpenseTemplateForm(false)
      setExpenseTemplateFormData({
        name: '',
        amount: '',
        category_id: '',
        subcategory_id: '',
        account_id: ''
      })
      await loadData()
    } catch (error) {
      console.error('Error saving expense template:', error)
      alert('Failed to save expense template: ' + (error.message || 'Unknown error'))
    }
  }

  const handleEditExpenseTemplate = (template) => {
    setExpenseTemplateFormData({
      name: template.name,
      amount: template.amount.toString(),
      category_id: template.category_id.toString(),
      subcategory_id: template.subcategory_id ? template.subcategory_id.toString() : '',
      account_id: template.account_id ? template.account_id.toString() : ''
    })
    setEditingExpenseTemplate(template)
    setShowExpenseTemplateForm(true)
  }

  const handleDeleteExpenseTemplate = async (templateId) => {
    if (window.confirm('Are you sure you want to delete this recurring expense? This will deactivate it.')) {
      try {
        await deleteExpenseTemplate(templateId)
        await loadData()
      } catch (error) {
        console.error('Error deleting expense template:', error)
        alert('Failed to delete expense template: ' + (error.message || 'Unknown error'))
      }
    }
  }

  const handleCancelExpenseTemplateEdit = () => {
    setEditingExpenseTemplate(null)
    setShowExpenseTemplateForm(false)
    setExpenseTemplateFormData({
      name: '',
      amount: '',
      category_id: '',
      subcategory_id: '',
      account_id: ''
    })
  }

  // Get subcategories for selected category
  const getSubcategoriesForCategory = (categoryId) => {
    const category = categories.find(c => c.id === parseInt(categoryId))
    return category ? category.subcategories : []
  }

  // Modal functions
  const handleCategoryClick = (category) => {
    setSelectedCategory(category)
    setCategoryEditData({ name: category.name })
    setShowModal(true)
    setEditingCategory(false)
    setEditingSubcategory(null)
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setSelectedCategory(null)
    setEditingCategory(false)
    setEditingSubcategory(null)
    setNewSubcategoryName('')
  }

  const handleEditCategoryName = async () => {
    if (!categoryEditData.name.trim()) {
      alert('Category name cannot be empty')
      return
    }
    try {
      await updateCategory(selectedCategory.id, { name: categoryEditData.name })
      // Reload all data
      const [categoriesData, accountsData] = await Promise.all([
        getCategoriesWithStats(),
        getAccountsWithStats()
      ])
      setCategories(categoriesData)
      setAccounts(accountsData)
      // Find and update the selected category with fresh data
      const updated = categoriesData.find(c => c.id === selectedCategory.id)
      setSelectedCategory(updated)
      setEditingCategory(false)
    } catch (error) {
      console.error('Error updating category:', error)
      alert('Failed to update category: ' + (error.message || 'Unknown error'))
    }
  }

  const handleAddSubcategory = async () => {
    if (!newSubcategoryName.trim()) {
      alert('Subcategory name cannot be empty')
      return
    }
    try {
      await createSubcategory({
        name: newSubcategoryName,
        category_id: selectedCategory.id,
        is_active: true
      })
      setNewSubcategoryName('')
      // Reload all data
      const [categoriesData, accountsData] = await Promise.all([
        getCategoriesWithStats(),
        getAccountsWithStats()
      ])
      setCategories(categoriesData)
      setAccounts(accountsData)
      // Find and update the selected category with fresh data
      const updated = categoriesData.find(c => c.id === selectedCategory.id)
      setSelectedCategory(updated)
    } catch (error) {
      console.error('Error creating subcategory:', error)
      alert('Failed to create subcategory: ' + (error.message || 'Unknown error'))
    }
  }

  const handleEditSubcategory = async (subcategoryId, newName) => {
    if (!newName.trim()) {
      alert('Subcategory name cannot be empty')
      return
    }
    try {
      await updateSubcategory(subcategoryId, { name: newName })
      // Reload all data
      const [categoriesData, accountsData] = await Promise.all([
        getCategoriesWithStats(),
        getAccountsWithStats()
      ])
      setCategories(categoriesData)
      setAccounts(accountsData)
      // Find and update the selected category with fresh data
      const updated = categoriesData.find(c => c.id === selectedCategory.id)
      setSelectedCategory(updated)
      setEditingSubcategory(null)
    } catch (error) {
      console.error('Error updating subcategory:', error)
      alert('Failed to update subcategory: ' + (error.message || 'Unknown error'))
    }
  }

  const handleDeleteSubcategory = async (subcategoryId) => {
    if (window.confirm('Are you sure you want to delete this subcategory?')) {
      try {
        await deleteSubcategory(subcategoryId)
        // Reload all data
        const [categoriesData, accountsData] = await Promise.all([
          getCategoriesWithStats(),
          getAccountsWithStats()
        ])
        setCategories(categoriesData)
        setAccounts(accountsData)
        // Find and update the selected category with fresh data
        const updated = categoriesData.find(c => c.id === selectedCategory.id)
        setSelectedCategory(updated)
      } catch (error) {
        console.error('Error deleting subcategory:', error)
        alert('Failed to delete subcategory: ' + (error.message || 'Unknown error'))
      }
    }
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <div className="management">
      {/* Categories Section */}
      {showCategories && (
      <div className="management-section">
        <div className="section-header">
          <h3>Categories</h3>
          <button
            onClick={() => setShowCategoryForm(!showCategoryForm)}
            className="btn-add"
          >
            {showCategoryForm ? 'Cancel' : '+ Add Category'}
          </button>
        </div>

        {showCategoryForm && (
          <div className="form-card">
            <form onSubmit={handleCategorySubmit} className="management-form">
              <div className="form-group">
                <label htmlFor="category-name">Category Name</label>
                <input
                  type="text"
                  id="category-name"
                  value={categoryFormData.name}
                  onChange={(e) => setCategoryFormData({ ...categoryFormData, name: e.target.value })}
                  required
                  className="form-input"
                  placeholder="e.g., Groceries, Entertainment"
                />
              </div>
              <div className="form-group">
                <label htmlFor="category-type">Type</label>
                <select
                  id="category-type"
                  value={categoryFormData.category_type}
                  onChange={(e) => setCategoryFormData({ ...categoryFormData, category_type: e.target.value })}
                  className="form-input"
                >
                  <option value="expense">Expense</option>
                  <option value="income">Income</option>
                  <option value="saving">Saving</option>
                </select>
              </div>
              <button type="submit" className="btn-primary">Create Category</button>
            </form>
          </div>
        )}

        <div className="items-grid">
          {categories.length === 0 ? (
            <p className="empty-state">No categories yet. Create one to get started!</p>
          ) : (
            categories.map((category) => (
              <div key={category.id} className="item-card" onClick={() => handleCategoryClick(category)} style={{ cursor: 'pointer' }}>
                <div className="item-header">
                  <h4>{category.name}</h4>
                  <span className={`type-badge ${category.category_type}`}>
                    {category.category_type}
                  </span>
                </div>
                <div className="item-stats">
                  <div className="stat">
                    <span className="stat-value">{category.expense_count || 0}</span>
                    <span className="stat-label">expenses</span>
                  </div>
                  <div className="stat">
                    <span className="stat-value">{formatAmount(category.total_amount || 0)}</span>
                    <span className="stat-label">total</span>
                  </div>
                </div>
                <div className="item-actions" onClick={(e) => e.stopPropagation()}>
                  <button
                    onClick={() => handleDeleteCategory(category.id)}
                    className="btn-delete-small"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      )}

      {/* Income Sources Section */}
      {showIncome && (
      <div className="management-section">
        <div className="section-header">
          <h3>Income Sources</h3>
          <button
            onClick={() => {
              if (showIncomeForm && editingIncome) {
                handleCancelIncomeEdit()
              } else {
                setShowIncomeForm(!showIncomeForm)
              }
            }}
            className="btn-add"
          >
            {showIncomeForm ? 'Cancel' : '+ Add Income Source'}
          </button>
        </div>

        {showIncomeForm && (
          <div className="form-card">
            <form onSubmit={handleIncomeSubmit} className="management-form">
              <div className="form-group">
                <label htmlFor="income-source-name">Income Source Name</label>
                <input
                  type="text"
                  id="income-source-name"
                  value={incomeFormData.source_name}
                  onChange={(e) => setIncomeFormData({ ...incomeFormData, source_name: e.target.value })}
                  required
                  className="form-input"
                  placeholder="e.g., Your Salary, Wife's Salary, Freelance"
                />
              </div>
              <div className="form-group">
                <label htmlFor="income-amount">Current Monthly Amount</label>
                <input
                  type="number"
                  id="income-amount"
                  step="0.01"
                  min="0"
                  value={incomeFormData.current_amount}
                  onChange={(e) => setIncomeFormData({ ...incomeFormData, current_amount: e.target.value })}
                  className="form-input"
                  placeholder="e.g., 50000"
                />
              </div>
              <button type="submit" className="btn-primary">
                {editingIncome ? 'Update Income Source' : 'Create Income Source'}
              </button>
            </form>
          </div>
        )}

        <div className="items-grid">
          {incomeTemplates.length === 0 ? (
            <p className="empty-state">No income sources yet. Create one to get started!</p>
          ) : (
            incomeTemplates.map((income) => (
              <div key={income.id} className="item-card">
                <div className="item-header">
                  <h4>{income.source_name}</h4>
                  <span className="type-badge income">recurring</span>
                </div>
                <div className="item-stats">
                  <div className="stat">
                    <span className="stat-value">{formatAmount(income.current_amount)}</span>
                    <span className="stat-label">monthly</span>
                  </div>
                </div>
                <div className="item-actions">
                  <button
                    onClick={() => handleEditIncome(income)}
                    className="btn-edit-small"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteIncome(income.id)}
                    className="btn-delete-small"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      )}

      {/* Recurring Expenses Section */}
      {showRecurring && (
      <div className="management-section">
        <div className="section-header">
          <h3>Recurring Expenses</h3>
          <button
            onClick={() => {
              if (showExpenseTemplateForm && editingExpenseTemplate) {
                handleCancelExpenseTemplateEdit()
              } else {
                setShowExpenseTemplateForm(!showExpenseTemplateForm)
              }
            }}
            className="btn-add"
          >
            {showExpenseTemplateForm ? 'Cancel' : '+ Add Recurring Expense'}
          </button>
        </div>

        {showExpenseTemplateForm && (
          <div className="form-card">
            <form onSubmit={handleExpenseTemplateSubmit} className="management-form">
              <div className="form-group">
                <label htmlFor="expense-template-name">Expense Name</label>
                <input
                  type="text"
                  id="expense-template-name"
                  value={expenseTemplateFormData.name}
                  onChange={(e) => setExpenseTemplateFormData({ ...expenseTemplateFormData, name: e.target.value })}
                  required
                  className="form-input"
                  placeholder="e.g., Rent, Internet, Gym Membership"
                />
              </div>
              <div className="form-group">
                <label htmlFor="expense-template-amount">Amount</label>
                <input
                  type="number"
                  id="expense-template-amount"
                  step="0.01"
                  min="0"
                  value={expenseTemplateFormData.amount}
                  onChange={(e) => setExpenseTemplateFormData({ ...expenseTemplateFormData, amount: e.target.value })}
                  className="form-input"
                  placeholder="e.g., 15000"
                />
              </div>
              <div className="form-group">
                <label htmlFor="expense-template-category">Category</label>
                <select
                  id="expense-template-category"
                  value={expenseTemplateFormData.category_id}
                  onChange={(e) => {
                    setExpenseTemplateFormData({
                      ...expenseTemplateFormData,
                      category_id: e.target.value,
                      subcategory_id: '' // Reset subcategory when category changes
                    })
                  }}
                  required
                  className="form-input"
                >
                  <option value="">Select Category</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>
              {expenseTemplateFormData.category_id && (
                <div className="form-group">
                  <label htmlFor="expense-template-subcategory">Subcategory (Optional)</label>
                  <select
                    id="expense-template-subcategory"
                    value={expenseTemplateFormData.subcategory_id}
                    onChange={(e) => setExpenseTemplateFormData({ ...expenseTemplateFormData, subcategory_id: e.target.value })}
                    className="form-input"
                  >
                    <option value="">None</option>
                    {getSubcategoriesForCategory(expenseTemplateFormData.category_id).map((subcat) => (
                      <option key={subcat.id} value={subcat.id}>{subcat.name}</option>
                    ))}
                  </select>
                </div>
              )}
              <div className="form-group">
                <label htmlFor="expense-template-account">Payment Account (Optional)</label>
                <select
                  id="expense-template-account"
                  value={expenseTemplateFormData.account_id}
                  onChange={(e) => setExpenseTemplateFormData({ ...expenseTemplateFormData, account_id: e.target.value })}
                  className="form-input"
                >
                  <option value="">None</option>
                  {accounts.map((acc) => (
                    <option key={acc.id} value={acc.id}>{acc.name} - {acc.owner_name}</option>
                  ))}
                </select>
              </div>
              <button type="submit" className="btn-primary">
                {editingExpenseTemplate ? 'Update Recurring Expense' : 'Create Recurring Expense'}
              </button>
            </form>
          </div>
        )}

        <div className="items-grid">
          {expenseTemplates.length === 0 ? (
            <p className="empty-state">No recurring expenses yet. Create one to get started!</p>
          ) : (
            expenseTemplates.map((template) => (
              <div key={template.id} className="item-card">
                <div className="item-header">
                  <h4>{template.name}</h4>
                  <span className="type-badge expense">recurring</span>
                </div>
                <div className="item-stats">
                  <div className="stat">
                    <span className="stat-value">{formatAmount(template.amount)}</span>
                    <span className="stat-label">monthly</span>
                  </div>
                  <div className="stat">
                    <span className="stat-value">{template.category_name}</span>
                    <span className="stat-label">
                      {template.subcategory_name ? `${template.subcategory_name}` : 'category'}
                    </span>
                  </div>
                  {template.account_name && (
                    <div className="stat">
                      <span className="stat-value">{template.account_name}</span>
                      <span className="stat-label">account</span>
                    </div>
                  )}
                </div>
                <div className="item-actions">
                  <button
                    onClick={() => handleEditExpenseTemplate(template)}
                    className="btn-edit-small"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteExpenseTemplate(template.id)}
                    className="btn-delete-small"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      )}

      {/* Payment Accounts Section */}
      {showAccounts && (
      <div className="management-section">
        <div className="section-header">
          <h3>Payment Accounts</h3>
          <button
            onClick={() => setShowAccountForm(!showAccountForm)}
            className="btn-add"
          >
            {showAccountForm ? 'Cancel' : '+ Add Payment Account'}
          </button>
        </div>

        {showAccountForm && (
          <div className="form-card">
            <form onSubmit={handleAccountSubmit} className="management-form">
              <div className="form-group">
                <label htmlFor="account-name">Account Name</label>
                <input
                  type="text"
                  id="account-name"
                  value={accountFormData.name}
                  onChange={(e) => setAccountFormData({ ...accountFormData, name: e.target.value })}
                  required
                  className="form-input"
                  placeholder="e.g., Main Bank Account, Credit Card"
                />
              </div>
              <div className="form-group">
                <label htmlFor="owner-name">Owner Name</label>
                <input
                  type="text"
                  id="owner-name"
                  value={accountFormData.owner_name}
                  onChange={(e) => setAccountFormData({ ...accountFormData, owner_name: e.target.value })}
                  required
                  className="form-input"
                  placeholder="e.g., John Doe"
                />
              </div>
              <button type="submit" className="btn-primary">Create Payment Account</button>
            </form>
          </div>
        )}

        <div className="items-grid">
          {accounts.length === 0 ? (
            <p className="empty-state">No payment accounts yet. Create one to get started!</p>
          ) : (
            accounts.map((account) => (
              <div key={account.id} className="item-card">
                <div className="item-header">
                  <h4>{account.name}</h4>
                  <span className="owner-badge">{account.owner_name}</span>
                </div>
                <div className="item-stats">
                  <div className="stat">
                    <span className="stat-value">{account.expense_count || 0}</span>
                    <span className="stat-label">expenses</span>
                  </div>
                  <div className="stat">
                    <span className="stat-value">{formatAmount(account.total_amount || 0)}</span>
                    <span className="stat-label">total</span>
                  </div>
                </div>
                <div className="item-actions">
                  <button
                    onClick={() => handleDeleteAccount(account.id)}
                    className="btn-delete-small"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      )}

      {/* Category Details Modal */}
      {showCategories && showModal && selectedCategory && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Category Details</h2>
              <button className="modal-close" onClick={handleCloseModal}>&times;</button>
            </div>

            <div className="modal-body">
              {/* Category Name Section */}
              <div className="modal-section">
                <h3>Category Name</h3>
                {editingCategory ? (
                  <div className="edit-form">
                    <input
                      type="text"
                      value={categoryEditData.name}
                      onChange={(e) => setCategoryEditData({ name: e.target.value })}
                      className="form-input"
                    />
                    <div className="edit-actions">
                      <button onClick={handleEditCategoryName} className="btn-save">Save</button>
                      <button onClick={() => {
                        setEditingCategory(false)
                        setCategoryEditData({ name: selectedCategory.name })
                      }} className="btn-cancel">Cancel</button>
                    </div>
                  </div>
                ) : (
                  <div className="display-with-edit">
                    <span className="display-value">{selectedCategory.name}</span>
                    <button onClick={() => setEditingCategory(true)} className="btn-edit-inline">Edit</button>
                  </div>
                )}
              </div>

              {/* Statistics */}
              <div className="modal-section">
                <h3>Statistics</h3>
                <div className="modal-stats">
                  <div className="modal-stat">
                    <span className="stat-label">Total Expenses:</span>
                    <span className="stat-value">{selectedCategory.expense_count || 0}</span>
                  </div>
                  <div className="modal-stat">
                    <span className="stat-label">Total Amount:</span>
                    <span className="stat-value">{formatAmount(selectedCategory.total_amount || 0)}</span>
                  </div>
                </div>
              </div>

              {/* Subcategories Section */}
              <div className="modal-section">
                <h3>Subcategories</h3>
                <div className="subcategories-list">
                  {selectedCategory.subcategories && selectedCategory.subcategories.length > 0 ? (
                    selectedCategory.subcategories.map((sub) => (
                      <div key={sub.id} className="subcategory-item">
                        {editingSubcategory === sub.id ? (
                          <div className="edit-form">
                            <input
                              type="text"
                              defaultValue={sub.name}
                              id={`subcategory-edit-${sub.id}`}
                              className="form-input"
                            />
                            <div className="edit-actions">
                              <button onClick={() => {
                                const newName = document.getElementById(`subcategory-edit-${sub.id}`).value
                                handleEditSubcategory(sub.id, newName)
                              }} className="btn-save">Save</button>
                              <button onClick={() => setEditingSubcategory(null)} className="btn-cancel">Cancel</button>
                            </div>
                          </div>
                        ) : (
                          <div className="subcategory-display">
                            <div className="subcategory-info">
                              <span className="subcategory-name">{sub.name}</span>
                              <div className="subcategory-stats">
                                <span className="subcategory-stat">{sub.expense_count || 0} expenses</span>
                                <span className="subcategory-stat-separator">•</span>
                                <span className="subcategory-stat">{formatAmount(sub.total_amount || 0)}</span>
                              </div>
                            </div>
                            <div className="subcategory-actions">
                              <button onClick={() => setEditingSubcategory(sub.id)} className="btn-edit-small">Edit</button>
                              <button onClick={() => handleDeleteSubcategory(sub.id)} className="btn-delete-small">Delete</button>
                            </div>
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    <p className="empty-state-small">No subcategories yet</p>
                  )}
                </div>

                {/* Add Subcategory */}
                <div className="add-subcategory">
                  <input
                    type="text"
                    placeholder="New subcategory name"
                    value={newSubcategoryName}
                    onChange={(e) => setNewSubcategoryName(e.target.value)}
                    className="form-input"
                    onKeyPress={(e) => e.key === 'Enter' && handleAddSubcategory()}
                  />
                  <button onClick={handleAddSubcategory} className="btn-add-small">Add Subcategory</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Management
