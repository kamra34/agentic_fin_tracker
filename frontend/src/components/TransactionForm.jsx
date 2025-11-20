import { useState, useEffect } from 'react'
import { getCategories } from '../services/api'
import './TransactionForm.css'

function TransactionForm({ onSubmit, onCancel }) {
  const [categories, setCategories] = useState([])
  const [formData, setFormData] = useState({
    amount: '',
    description: '',
    transaction_type: 'expense',
    category_id: '',
    date: new Date().toISOString().split('T')[0]
  })

  useEffect(() => {
    fetchCategories()
  }, [])

  const fetchCategories = async () => {
    try {
      const data = await getCategories()
      setCategories(data)
    } catch (error) {
      console.error('Error fetching categories:', error)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({
      ...formData,
      amount: parseFloat(formData.amount),
      category_id: parseInt(formData.category_id)
    })
    setFormData({
      amount: '',
      description: '',
      transaction_type: 'expense',
      category_id: '',
      date: new Date().toISOString().split('T')[0]
    })
  }

  const filteredCategories = categories.filter(
    cat => cat.type === formData.transaction_type
  )

  return (
    <form className="transaction-form" onSubmit={handleSubmit}>
      <div className="form-row">
        <div className="form-group">
          <label>Type</label>
          <select
            name="transaction_type"
            value={formData.transaction_type}
            onChange={handleChange}
            required
          >
            <option value="expense">Expense</option>
            <option value="income">Income</option>
          </select>
        </div>

        <div className="form-group">
          <label>Amount</label>
          <input
            type="number"
            name="amount"
            value={formData.amount}
            onChange={handleChange}
            step="0.01"
            min="0.01"
            required
          />
        </div>

        <div className="form-group">
          <label>Date</label>
          <input
            type="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
            required
          />
        </div>
      </div>

      <div className="form-group">
        <label>Category</label>
        <select
          name="category_id"
          value={formData.category_id}
          onChange={handleChange}
          required
        >
          <option value="">Select a category</option>
          {filteredCategories.map(cat => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Description</label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows="3"
          required
        />
      </div>

      <div className="form-actions">
        <button type="submit" className="btn btn-primary">
          Add Transaction
        </button>
        <button type="button" className="btn btn-secondary" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  )
}

export default TransactionForm
