import { useState, useEffect } from 'react'
import { getCategoriesStructured } from '../services/api'
import { useCurrency } from '../context/CurrencyContext'
import './Categories.css'

function Categories() {
  const { formatAmount } = useCurrency()
  const [categories, setCategories] = useState([])
  const [expandedCategory, setExpandedCategory] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCategories()
  }, [])

  const fetchCategories = async () => {
    try {
      setLoading(true)
      const data = await getCategoriesStructured()
      setCategories(data)
    } catch (error) {
      console.error('Error fetching categories:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleCategory = (categoryName) => {
    setExpandedCategory(expandedCategory === categoryName ? null : categoryName)
  }

  const getCategoryColor = (index) => {
    const colors = [
      '#667eea', // indigo
      '#f093fb', // pink
      '#4facfe', // blue
      '#43e97b', // green
      '#fa709a', // rose
      '#feca57', // yellow
      '#ee5a6f', // red
      '#c471ed', // purple
      '#12c2e9', // cyan
      '#f6d365'  // orange
    ]
    return colors[index % colors.length]
  }

  if (loading) {
    return <div className="loading">Loading categories...</div>
  }

  if (categories.length === 0) {
    return (
      <div className="categories">
        <div className="page-header">
          <h2 className="page-title">Expense Categories</h2>
        </div>
        <div className="empty-categories">
          <div className="empty-icon">📊</div>
          <h3>No Categories Yet</h3>
          <p>Start adding expenses to see your categories here</p>
        </div>
      </div>
    )
  }

  return (
    <div className="categories">
      <div className="page-header">
        <h2 className="page-title">Expense Categories</h2>
        <div className="categories-stats">
          <span className="stat-badge">{categories.length} Categories</span>
          <span className="stat-badge">
            {categories.reduce((sum, cat) => sum + cat.total_count, 0)} Total Expenses
          </span>
        </div>
      </div>

      <div className="categories-grid">
        {categories.map((category, index) => (
          <div
            key={category.name}
            className={`category-card ${expandedCategory === category.name ? 'expanded' : ''}`}
            style={{
              '--category-color': getCategoryColor(index),
              animationDelay: `${index * 0.1}s`
            }}
          >
            <div
              className="category-header"
              onClick={() => toggleCategory(category.name)}
            >
              <div className="category-info">
                <div className="category-icon" style={{ backgroundColor: getCategoryColor(index) }}>
                  {category.name.charAt(0).toUpperCase()}
                </div>
                <div className="category-details">
                  <h3 className="category-name">{category.name}</h3>
                  <div className="category-meta">
                    <span className="expense-count">{category.total_count} expenses</span>
                    <span className="category-separator">•</span>
                    <span className="expense-total">{formatAmount(category.total_amount)}</span>
                  </div>
                </div>
              </div>
              <div className="category-expand-icon">
                {category.subcategories.length > 0 && (
                  <>
                    <span className="subcategory-count">{category.subcategories.length}</span>
                    <svg
                      className="expand-arrow"
                      width="20"
                      height="20"
                      viewBox="0 0 20 20"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M5 7.5L10 12.5L15 7.5"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </>
                )}
              </div>
            </div>

            {category.subcategories.length > 0 && (
              <div className="subcategories-container">
                <div className="subcategories-scroll">
                  {category.subcategories.map((subcategory, subIndex) => (
                    <div
                      key={subcategory.name}
                      className="subcategory-pill"
                      style={{
                        animationDelay: `${subIndex * 0.05}s`,
                        borderColor: getCategoryColor(index)
                      }}
                    >
                      <div className="subcategory-content">
                        <span className="subcategory-name">{subcategory.name}</span>
                        <div className="subcategory-stats">
                          <span className="subcategory-count">{subcategory.count}×</span>
                          <span className="subcategory-amount">{formatAmount(subcategory.total_amount)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="info-box">
        <div className="info-icon">💡</div>
        <p>
          Click on a category to view its subcategories. Categories are automatically
          created from your expenses.
        </p>
      </div>
    </div>
  )
}

export default Categories
