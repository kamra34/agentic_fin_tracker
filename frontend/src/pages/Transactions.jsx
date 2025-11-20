import { useState, useEffect } from 'react'
import { getTransactions, createTransaction, deleteTransaction } from '../services/api'
import TransactionForm from '../components/TransactionForm'
import TransactionList from '../components/TransactionList'
import './Transactions.css'

function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)

  useEffect(() => {
    fetchTransactions()
  }, [])

  const fetchTransactions = async () => {
    try {
      setLoading(true)
      const data = await getTransactions()
      setTransactions(data)
    } catch (error) {
      console.error('Error fetching transactions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTransaction = async (transactionData) => {
    try {
      await createTransaction(transactionData)
      await fetchTransactions()
      setShowForm(false)
    } catch (error) {
      console.error('Error creating transaction:', error)
    }
  }

  const handleDeleteTransaction = async (id) => {
    if (window.confirm('Are you sure you want to delete this transaction?')) {
      try {
        await deleteTransaction(id)
        await fetchTransactions()
      } catch (error) {
        console.error('Error deleting transaction:', error)
      }
    }
  }

  return (
    <div className="transactions">
      <div className="page-header">
        <h2 className="page-title">Transactions</h2>
        <button
          className="btn btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : 'Add Transaction'}
        </button>
      </div>

      {showForm && (
        <TransactionForm onSubmit={handleCreateTransaction} onCancel={() => setShowForm(false)} />
      )}

      {loading ? (
        <div className="loading">Loading...</div>
      ) : (
        <TransactionList
          transactions={transactions}
          onDelete={handleDeleteTransaction}
        />
      )}
    </div>
  )
}

export default Transactions
