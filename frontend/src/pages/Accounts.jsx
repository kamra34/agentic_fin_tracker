import { useState, useEffect } from 'react'
import { getAccountsWithStats, createAccount, updateAccount, deleteAccount } from '../services/api'
import { useCurrency } from '../context/CurrencyContext'
import './Accounts.css'

function Accounts() {
  const { formatAmount } = useCurrency()
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingAccount, setEditingAccount] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    owner_name: ''
  })
  const [error, setError] = useState('')
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  useEffect(() => {
    fetchAccounts()
  }, [])

  const fetchAccounts = async () => {
    try {
      setLoading(true)
      const data = await getAccountsWithStats()
      setAccounts(data)
    } catch (error) {
      console.error('Error fetching accounts:', error)
      setError('Failed to load accounts')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenModal = (account = null) => {
    if (account) {
      setEditingAccount(account)
      setFormData({
        name: account.name,
        owner_name: account.owner_name
      })
    } else {
      setEditingAccount(null)
      setFormData({
        name: '',
        owner_name: ''
      })
    }
    setError('')
    setShowModal(true)
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setEditingAccount(null)
    setFormData({ name: '', owner_name: '' })
    setError('')
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!formData.name.trim() || !formData.owner_name.trim()) {
      setError('Both account name and owner name are required')
      return
    }

    try {
      if (editingAccount) {
        await updateAccount(editingAccount.id, formData)
      } else {
        await createAccount(formData)
      }
      await fetchAccounts()
      handleCloseModal()
    } catch (error) {
      setError(error.message || 'Failed to save account')
    }
  }

  const handleDelete = async (accountId) => {
    try {
      await deleteAccount(accountId)
      await fetchAccounts()
      setDeleteConfirm(null)
    } catch (error) {
      setError(error.message || 'Failed to delete account')
      setDeleteConfirm(null)
    }
  }

  if (loading) {
    return <div className="loading">Loading accounts...</div>
  }

  return (
    <div className="accounts">
      <div className="page-header">
        <h2 className="page-title">Accounts Management</h2>
        <button className="btn-primary" onClick={() => handleOpenModal()}>
          + Add Account
        </button>
      </div>

      {error && !showModal && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError('')}>&times;</button>
        </div>
      )}

      {accounts.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🏦</div>
          <h3>No Accounts Yet</h3>
          <p>Create your first account to start tracking expenses by account</p>
          <button className="btn-primary" onClick={() => handleOpenModal()}>
            Create Account
          </button>
        </div>
      ) : (
        <div className="accounts-grid">
          {accounts.map((account, index) => (
            <div
              key={account.id}
              className="account-card"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="account-header">
                <div className="account-icon">
                  {account.name.charAt(0).toUpperCase()}
                </div>
                <div className="account-info">
                  <h3 className="account-name">{account.name}</h3>
                  <p className="account-owner">{account.owner_name}</p>
                </div>
              </div>

              <div className="account-stats">
                <div className="stat-item">
                  <span className="stat-label">Total Expenses</span>
                  <span className="stat-value">{formatAmount(account.total_amount)}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Expense Count</span>
                  <span className="stat-value">{account.expense_count}</span>
                </div>
              </div>

              <div className="account-actions">
                <button
                  className="btn-edit"
                  onClick={() => handleOpenModal(account)}
                  title="Edit account"
                >
                  Edit
                </button>
                <button
                  className="btn-delete"
                  onClick={() => setDeleteConfirm(account.id)}
                  title="Delete account"
                >
                  Delete
                </button>
              </div>

              {deleteConfirm === account.id && (
                <div className="delete-confirm">
                  <p>Delete this account?</p>
                  {account.expense_count > 0 && (
                    <p className="warning">
                      This account has {account.expense_count} associated expenses.
                      You cannot delete it until those are removed or reassigned.
                    </p>
                  )}
                  <div className="confirm-actions">
                    <button
                      className="btn-confirm"
                      onClick={() => handleDelete(account.id)}
                      disabled={account.expense_count > 0}
                    >
                      Confirm
                    </button>
                    <button
                      className="btn-cancel"
                      onClick={() => setDeleteConfirm(null)}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingAccount ? 'Edit Account' : 'Create New Account'}</h3>
              <button className="modal-close" onClick={handleCloseModal}>
                &times;
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              {error && (
                <div className="error-message">{error}</div>
              )}

              <div className="form-group">
                <label htmlFor="name">Account Name *</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="e.g., Main Credit Card, Savings Account"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="owner_name">Owner Name *</label>
                <input
                  type="text"
                  id="owner_name"
                  name="owner_name"
                  value={formData.owner_name}
                  onChange={handleInputChange}
                  placeholder="e.g., John Doe"
                  required
                />
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={handleCloseModal}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  {editingAccount ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Accounts
