import './TransactionList.css'

function TransactionList({ transactions, onDelete }) {
  if (transactions.length === 0) {
    return <div className="empty-state">No transactions found. Add your first transaction!</div>
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  return (
    <div className="transaction-list">
      {transactions.map(transaction => (
        <div key={transaction.id} className={`transaction-item ${transaction.transaction_type}`}>
          <div className="transaction-info">
            <div className="transaction-header">
              <span className="transaction-description">{transaction.description}</span>
              <span className={`transaction-amount ${transaction.transaction_type}`}>
                {transaction.transaction_type === 'income' ? '+' : '-'}
                ${transaction.amount.toFixed(2)}
              </span>
            </div>
            <div className="transaction-meta">
              <span className="transaction-category">
                {transaction.category?.name || 'Uncategorized'}
              </span>
              <span className="transaction-date">{formatDate(transaction.date)}</span>
            </div>
          </div>
          <button
            className="btn-delete"
            onClick={() => onDelete(transaction.id)}
            title="Delete transaction"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  )
}

export default TransactionList
