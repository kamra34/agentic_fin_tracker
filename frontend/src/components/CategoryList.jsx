import './CategoryList.css'

function CategoryList({ categories, onDelete }) {
  if (categories.length === 0) {
    return <div className="empty-state">No categories found. Add your first category!</div>
  }

  const incomeCategories = categories.filter(cat => cat.type === 'income')
  const expenseCategories = categories.filter(cat => cat.type === 'expense')

  const CategoryItem = ({ category }) => (
    <div className="category-item" style={{ borderLeftColor: category.color }}>
      <div className="category-info">
        {category.icon && <span className="category-icon">{category.icon}</span>}
        <div className="category-details">
          <span className="category-name">{category.name}</span>
          <span className="category-type">{category.type}</span>
        </div>
      </div>
      <button
        className="btn-delete"
        onClick={() => onDelete(category.id)}
        title="Delete category"
      >
        ×
      </button>
    </div>
  )

  return (
    <div className="category-list">
      {expenseCategories.length > 0 && (
        <div className="category-section">
          <h3 className="section-title">Expense Categories</h3>
          <div className="category-grid">
            {expenseCategories.map(category => (
              <CategoryItem key={category.id} category={category} />
            ))}
          </div>
        </div>
      )}

      {incomeCategories.length > 0 && (
        <div className="category-section">
          <h3 className="section-title">Income Categories</h3>
          <div className="category-grid">
            {incomeCategories.map(category => (
              <CategoryItem key={category.id} category={category} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default CategoryList
