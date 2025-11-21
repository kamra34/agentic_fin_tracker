import { useState, useEffect } from 'react'
import {
  getSavingsAccounts,
  createSavingsAccount,
  updateSavingsAccount,
  deleteSavingsAccount,
  createSavingsTransaction,
  updateSavingsTransaction,
  deleteSavingsTransaction
} from '../services/api'
import { useCurrency } from '../context/CurrencyContext'
import './Savings.css'

const ACCOUNT_TYPES = [
  { value: 'investment', label: '📈 Investment Account', icon: '📈' },
  { value: 'crypto', label: '₿ Cryptocurrency', icon: '₿' },
  { value: 'bank_savings', label: '🏦 Bank Savings', icon: '🏦' },
  { value: 'retirement', label: '🎯 Retirement Fund', icon: '🎯' },
  { value: 'other', label: '💼 Other', icon: '💼' }
]

const TRANSACTION_TYPES = [
  { value: 'deposit', label: 'Deposit', color: '#00c853' },
  { value: 'withdrawal', label: 'Withdrawal', color: '#ef4444' },
  { value: 'value_update', label: 'Value Update', color: '#00b8d4' }
]

function Savings() {
  const { formatAmount } = useCurrency()
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedAccount, setSelectedAccount] = useState(null)
  const [showAccountModal, setShowAccountModal] = useState(false)
  const [showTransactionModal, setShowTransactionModal] = useState(false)
  const [editingAccount, setEditingAccount] = useState(null)
  const [editingTransaction, setEditingTransaction] = useState(null)
  const [error, setError] = useState('')
  const [deleteConfirm, setDeleteConfirm] = useState(null)
  const [deleteTransactionConfirm, setDeleteTransactionConfirm] = useState(null)

  const [accountForm, setAccountForm] = useState({
    name: '',
    account_type: '',
    description: ''
  })

  const [transactionForm, setTransactionForm] = useState({
    transaction_type: 'deposit',
    amount: '',
    transaction_date: new Date().toISOString().slice(0, 16),
    notes: ''
  })

  useEffect(() => {
    fetchAccounts()
  }, [])

  const fetchAccounts = async () => {
    try {
      setLoading(true)
      const data = await getSavingsAccounts()
      setAccounts(data)
      setError('')
    } catch (error) {
      console.error('Error fetching savings accounts:', error)
      setError('Failed to load savings accounts')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenAccountModal = (account = null) => {
    if (account) {
      setEditingAccount(account)
      setAccountForm({
        name: account.name,
        account_type: account.account_type,
        description: account.description || ''
      })
    } else {
      setEditingAccount(null)
      setAccountForm({
        name: '',
        account_type: '',
        description: ''
      })
    }
    setError('')
    setShowAccountModal(true)
  }

  const handleCloseAccountModal = () => {
    setShowAccountModal(false)
    setEditingAccount(null)
    setAccountForm({ name: '', account_type: '', description: '' })
    setError('')
  }

  const handleAccountSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!accountForm.name.trim() || !accountForm.account_type) {
      setError('Account name and type are required')
      return
    }

    try {
      if (editingAccount) {
        await updateSavingsAccount(editingAccount.id, accountForm)
      } else {
        await createSavingsAccount(accountForm)
      }
      await fetchAccounts()
      handleCloseAccountModal()
    } catch (error) {
      setError(error.message || 'Failed to save account')
    }
  }

  const handleDeleteAccount = async (accountId) => {
    try {
      await deleteSavingsAccount(accountId)
      await fetchAccounts()
      setDeleteConfirm(null)
      if (selectedAccount?.id === accountId) {
        setSelectedAccount(null)
      }
    } catch (error) {
      setError(error.message || 'Failed to delete account')
      setDeleteConfirm(null)
    }
  }

  const handleOpenTransactionModal = (account, transaction = null) => {
    setSelectedAccount(account)
    if (transaction) {
      setEditingTransaction(transaction)
      setTransactionForm({
        transaction_type: transaction.transaction_type,
        amount: transaction.amount.toString(),
        transaction_date: new Date(transaction.transaction_date).toISOString().slice(0, 16),
        notes: transaction.notes || ''
      })
    } else {
      setEditingTransaction(null)
      setTransactionForm({
        transaction_type: 'deposit',
        amount: '',
        transaction_date: new Date().toISOString().slice(0, 16),
        notes: ''
      })
    }
    setError('')
    setShowTransactionModal(true)
  }

  const handleTransactionSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!transactionForm.amount || parseFloat(transactionForm.amount) <= 0) {
      setError('Please enter a valid amount')
      return
    }

    try {
      if (editingTransaction) {
        await updateSavingsTransaction(editingTransaction.id, {
          transaction_type: transactionForm.transaction_type,
          amount: parseFloat(transactionForm.amount),
          transaction_date: new Date(transactionForm.transaction_date).toISOString(),
          notes: transactionForm.notes
        })
      } else {
        await createSavingsTransaction({
          account_id: selectedAccount.id,
          transaction_type: transactionForm.transaction_type,
          amount: parseFloat(transactionForm.amount),
          transaction_date: new Date(transactionForm.transaction_date).toISOString(),
          notes: transactionForm.notes
        })
      }
      await fetchAccounts()
      setShowTransactionModal(false)
      setSelectedAccount(null)
      setEditingTransaction(null)
    } catch (error) {
      setError(error.message || 'Failed to save transaction')
    }
  }

  const handleDeleteTransaction = async (transactionId) => {
    try {
      await deleteSavingsTransaction(transactionId)
      await fetchAccounts()
      setDeleteTransactionConfirm(null)
    } catch (error) {
      setError(error.message || 'Failed to delete transaction')
      setDeleteTransactionConfirm(null)
    }
  }

  const getAccountTypeIcon = (type) => {
    const accountType = ACCOUNT_TYPES.find(t => t.value === type)
    return accountType?.icon || '💼'
  }

  const getTotalPortfolioValue = () => {
    return accounts.reduce((sum, acc) => sum + (acc.current_value || 0), 0)
  }

  const getTotalProfitLoss = () => {
    return accounts.reduce((sum, acc) => sum + (acc.profit_loss || 0), 0)
  }

  const getTotalInvested = () => {
    return accounts.reduce((sum, acc) => sum + (acc.total_deposits || 0) - (acc.total_withdrawals || 0), 0)
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading savings...</p>
      </div>
    )
  }

  return (
    <div className="savings">
      {/* Header with Portfolio Summary */}
      <div className="savings-header">
        <div className="savings-header-content">
          <h1 className="savings-title">Savings & Investments</h1>
          <p className="savings-subtitle">Track your wealth across all accounts</p>

          <div className="portfolio-summary">
            <div className="summary-card summary-card-value">
              <div className="summary-label">Total Portfolio Value</div>
              <div className="summary-value">{formatAmount(getTotalPortfolioValue())}</div>
            </div>
            <div className="summary-card summary-card-invested">
              <div className="summary-label">Total Invested</div>
              <div className="summary-value">{formatAmount(getTotalInvested())}</div>
            </div>
            <div className={`summary-card summary-card-profit ${getTotalProfitLoss() >= 0 ? 'positive' : 'negative'}`}>
              <div className="summary-label">Total Profit/Loss</div>
              <div className="summary-value">
                {getTotalProfitLoss() >= 0 ? '+' : ''}{formatAmount(getTotalProfitLoss())}
                {getTotalInvested() > 0 && (
                  <span className="summary-percentage">
                    ({((getTotalProfitLoss() / getTotalInvested()) * 100).toFixed(2)}%)
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        <button className="btn-primary" onClick={() => handleOpenAccountModal()}>
          + Add Savings Account
        </button>
      </div>

      {error && !showAccountModal && !showTransactionModal && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError('')}>&times;</button>
        </div>
      )}

      {/* Accounts Grid */}
      {accounts.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">💰</div>
          <h3>No Savings Accounts Yet</h3>
          <p>Create your first savings account to start tracking your wealth</p>
          <button className="btn-primary" onClick={() => handleOpenAccountModal()}>
            Create Savings Account
          </button>
        </div>
      ) : (
        <div className="accounts-grid">
          {accounts.map((account, index) => {
            const profitLoss = account.profit_loss || 0
            const profitLossPercentage = account.profit_loss_percentage || 0

            return (
              <div
                key={account.id}
                className="savings-account-card"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="account-card-header">
                  <div className="account-icon-wrapper">
                    <span className="account-type-icon">{getAccountTypeIcon(account.account_type)}</span>
                  </div>
                  <div className="account-info">
                    <h3 className="account-name">{account.name}</h3>
                    <p className="account-type">
                      {ACCOUNT_TYPES.find(t => t.value === account.account_type)?.label || account.account_type}
                    </p>
                  </div>
                </div>

                {account.description && (
                  <p className="account-description">{account.description}</p>
                )}

                <div className="account-stats">
                  <div className="stat-row stat-row-main">
                    <span className="stat-label">Current Value</span>
                    <span className="stat-value stat-value-large">{formatAmount(account.current_value)}</span>
                  </div>

                  <div className="stat-row">
                    <span className="stat-label">Total Deposits</span>
                    <span className="stat-value">{formatAmount(account.total_deposits)}</span>
                  </div>

                  <div className="stat-row">
                    <span className="stat-label">Total Withdrawals</span>
                    <span className="stat-value">{formatAmount(account.total_withdrawals)}</span>
                  </div>

                  <div className="stat-row stat-row-highlight">
                    <span className="stat-label">Profit/Loss</span>
                    <span className={`stat-value stat-value-profit ${profitLoss >= 0 ? 'positive' : 'negative'}`}>
                      {profitLoss >= 0 ? '+' : ''}{formatAmount(profitLoss)}
                      <span className="profit-percentage">({profitLossPercentage >= 0 ? '+' : ''}{profitLossPercentage.toFixed(2)}%)</span>
                    </span>
                  </div>
                </div>

                <div className="account-actions">
                  <button
                    className="btn-action btn-add-transaction"
                    onClick={() => handleOpenTransactionModal(account)}
                  >
                    + Transaction
                  </button>
                  <button
                    className="btn-action btn-edit"
                    onClick={() => handleOpenAccountModal(account)}
                  >
                    Edit
                  </button>
                  <button
                    className="btn-action btn-delete"
                    onClick={() => setDeleteConfirm(account.id)}
                  >
                    Delete
                  </button>
                </div>

                {/* Recent Transactions */}
                {account.transactions && account.transactions.length > 0 && (
                  <div className="recent-transactions">
                    <h4>Recent Transactions</h4>
                    <div className="transactions-list">
                      {account.transactions.slice(0, 10).map((trans) => (
                        <div key={trans.id} className="transaction-item">
                          <div className="transaction-info">
                            <span className={`transaction-type transaction-type-${trans.transaction_type}`}>
                              {TRANSACTION_TYPES.find(t => t.value === trans.transaction_type)?.label}
                            </span>
                            <span className="transaction-date">
                              {new Date(trans.transaction_date).toLocaleDateString()}
                            </span>
                            {trans.notes && (
                              <span className="transaction-note-indicator" title={trans.notes}>
                                📝
                              </span>
                            )}
                          </div>
                          <div className="transaction-right">
                            <span className="transaction-amount">{formatAmount(trans.amount)}</span>
                            <div className="transaction-actions">
                              <button
                                className="btn-transaction-edit"
                                onClick={() => handleOpenTransactionModal(account, trans)}
                                title="Edit transaction"
                              >
                                ✏️
                              </button>
                              <button
                                className="btn-transaction-delete"
                                onClick={() => setDeleteTransactionConfirm(trans.id)}
                                title="Delete transaction"
                              >
                                🗑️
                              </button>
                            </div>
                          </div>

                          {deleteTransactionConfirm === trans.id && (
                            <div className="transaction-delete-confirm">
                              <p>Delete this transaction?</p>
                              <div className="confirm-actions-inline">
                                <button
                                  className="btn-confirm-small"
                                  onClick={() => handleDeleteTransaction(trans.id)}
                                >
                                  Yes
                                </button>
                                <button
                                  className="btn-cancel-small"
                                  onClick={() => setDeleteTransactionConfirm(null)}
                                >
                                  No
                                </button>
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {deleteConfirm === account.id && (
                  <div className="delete-confirm">
                    <p>Delete this savings account?</p>
                    <p className="warning">All transactions will be permanently deleted!</p>
                    <div className="confirm-actions">
                      <button
                        className="btn-confirm"
                        onClick={() => handleDeleteAccount(account.id)}
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
            )
          })}
        </div>
      )}

      {/* Account Modal */}
      {showAccountModal && (
        <div className="modal-overlay" onClick={handleCloseAccountModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingAccount ? 'Edit Savings Account' : 'Create New Savings Account'}</h3>
              <button className="modal-close" onClick={handleCloseAccountModal}>
                &times;
              </button>
            </div>

            <form onSubmit={handleAccountSubmit}>
              {error && <div className="error-message">{error}</div>}

              <div className="form-group">
                <label htmlFor="name">Account Name *</label>
                <input
                  type="text"
                  id="name"
                  value={accountForm.name}
                  onChange={(e) => setAccountForm({ ...accountForm, name: e.target.value })}
                  placeholder="e.g., Avanza ISK, Binance, Nordea Savings"
                  required
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="account_type">Account Type *</label>
                <select
                  id="account_type"
                  value={accountForm.account_type}
                  onChange={(e) => setAccountForm({ ...accountForm, account_type: e.target.value })}
                  required
                  className="form-select"
                >
                  <option value="">Select type...</option>
                  {ACCOUNT_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="description">Description (Optional)</label>
                <textarea
                  id="description"
                  value={accountForm.description}
                  onChange={(e) => setAccountForm({ ...accountForm, description: e.target.value })}
                  placeholder="Additional notes about this account..."
                  rows="3"
                  className="form-textarea"
                />
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={handleCloseAccountModal}>
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

      {/* Transaction Modal */}
      {showTransactionModal && (
        <div className="modal-overlay" onClick={() => setShowTransactionModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingTransaction ? 'Edit' : 'Add'} Transaction - {selectedAccount?.name}</h3>
              <button className="modal-close" onClick={() => setShowTransactionModal(false)}>
                &times;
              </button>
            </div>

            <form onSubmit={handleTransactionSubmit}>
              {error && <div className="error-message">{error}</div>}

              <div className="form-group">
                <label htmlFor="transaction_type">Transaction Type *</label>
                <select
                  id="transaction_type"
                  value={transactionForm.transaction_type}
                  onChange={(e) => setTransactionForm({ ...transactionForm, transaction_type: e.target.value })}
                  required
                  className="form-select"
                >
                  {TRANSACTION_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
                <p className="field-hint">
                  {transactionForm.transaction_type === 'deposit' && 'Money you add to the account'}
                  {transactionForm.transaction_type === 'withdrawal' && 'Money you take out from the account'}
                  {transactionForm.transaction_type === 'value_update' && 'Current market value of the account'}
                </p>
              </div>

              <div className="form-group">
                <label htmlFor="amount">Amount *</label>
                <input
                  type="number"
                  id="amount"
                  value={transactionForm.amount}
                  onChange={(e) => setTransactionForm({ ...transactionForm, amount: e.target.value })}
                  step="0.01"
                  min="0"
                  placeholder="0.00"
                  required
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="transaction_date">Transaction Date *</label>
                <input
                  type="datetime-local"
                  id="transaction_date"
                  value={transactionForm.transaction_date}
                  onChange={(e) => setTransactionForm({ ...transactionForm, transaction_date: e.target.value })}
                  required
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="notes">Notes (Optional)</label>
                <textarea
                  id="notes"
                  value={transactionForm.notes}
                  onChange={(e) => setTransactionForm({ ...transactionForm, notes: e.target.value })}
                  placeholder="Additional details..."
                  rows="3"
                  className="form-textarea"
                />
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowTransactionModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  {editingTransaction ? 'Update Transaction' : 'Add Transaction'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Savings
