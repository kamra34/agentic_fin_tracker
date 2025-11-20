import { useState, useEffect } from 'react'
import {
  getCategoriesWithStats,
  createCategory,
  updateCategory,
  deleteCategory,
  mergeCategories,
  createSubcategory,
  deleteSubcategory
} from '../services/api'
import { useCurrency } from '../context/CurrencyContext'
import './CategoryManagement.css'

function CategoryManagement() {
  const { formatAmount } = useCurrency()
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddCategoryForm, setShowAddCategoryForm] = useState(false)
  const [showAddSubcategoryForm, setShowAddSubcategoryForm] = useState(null)
  const [editingCategory, setEditingCategory] = useState(null)
  const [mergingCategory, setMergingCategory] = useState(null)
  const [newCategoryName, setNewCategoryName] = useState('')
  const [newCategoryType, setNewCategoryType] = useState('expense')
  const [newSubcategoryName, setNewSubcategoryName] = useState('')
  const [filterType, setFilterType] = useState('all')

  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    try {
      setLoading(true)
      const data = await getCategoriesWithStats()
      setCategories(data)
    } catch (error) {
      console.error('Error loading categories:', error)
      alert('Failed to load categories')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateCategory = async (e) => {
    e.preventDefault()
    if (!newCategoryName.trim()) return

    try {
      await createCategory({
        name: newCategoryName.trim(),
        category_type: newCategoryType,
        is_active: true
      })
      await loadCategories()
      setNewCategoryName('')
      setNewCategoryType('expense')
      setShowAddCategoryForm(false)
    } catch (error) {
      console.error('Error creating category:', error)
      alert('Failed to create category: ' + (error.message || 'Unknown error'))
    }
  }

  const handleUpdateCategory = async (categoryId, newName) => {
    if (!newName.trim()) return

    try {
      await updateCategory(categoryId, { name: newName.trim() })
      await loadCategories()
      setEditingCategory(null)
    } catch (error) {
      console.error('Error updating category:', error)
      alert('Failed to update category: ' + (error.message || 'Unknown error'))
    }
  }

  const handleDeleteCategory = async (categoryId, categoryName) => {
    if (!window.confirm(`Are you sure you want to deactivate "${categoryName}"? It will be hidden but expenses will remain.`)) {
      return
    }

    try {
      await deleteCategory(categoryId)
      await loadCategories()
    } catch (error) {
      console.error('Error deleting category:', error)
      alert('Failed to delete category')
    }
  }

  const handleMergeCategories = async (sourceId, targetId) => {
    const source = categories.find(c => c.id === sourceId)
    const target = categories.find(c => c.id === targetId)

    if (!window.confirm(`Merge "${source.name}" into "${target.name}"? All expenses from "${source.name}" will be moved to "${target.name}" and "${source.name}" will be deleted.`)) {
      return
    }

    try {
      await mergeCategories(sourceId, targetId)
      await loadCategories()
      setMergingCategory(null)
    } catch (error) {
      console.error('Error merging categories:', error)
      alert('Failed to merge categories: ' + (error.message || 'Unknown error'))
    }
  }

  const handleCreateSubcategory = async (e, categoryId) => {
    e.preventDefault()
    if (!newSubcategoryName.trim()) return

    try {
      await createSubcategory({
        name: newSubcategoryName.trim(),
        category_id: categoryId,
        is_active: true
      })
      await loadCategories()
      setNewSubcategoryName('')
      setShowAddSubcategoryForm(null)
    } catch (error) {
      console.error('Error creating subcategory:', error)
      alert('Failed to create subcategory: ' + (error.message || 'Unknown error'))
    }
  }

  const handleDeleteSubcategory = async (subcategoryId, subcategoryName) => {
    if (!window.confirm(`Are you sure you want to deactivate "${subcategoryName}"?`)) {
      return
    }

    try {
      await deleteSubcategory(subcategoryId)
      await loadCategories()
    } catch (error) {
      console.error('Error deleting subcategory:', error)
      alert('Failed to delete subcategory')
    }
  }

  if (loading) {
    return <div className="loading">Loading categories...</div>
  }

  const filteredCategories = filterType === 'all'
    ? categories
    : categories.filter(cat => cat.category_type === filterType)

  const getCategoryTypeLabel = (type) => {
    const labels = {
      'expense': 'Expense',
      'income': 'Income',
      'saving': 'Saving & Investment'
    }
    return labels[type] || type
  }

  return (
    <div className="category-management">
      <div className="page-header">
        <h2 className="page-title">Category Management</h2>
        <div className="header-actions">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="type-filter"
          >
            <option value="all">All Types</option>
            <option value="expense">Expenses</option>
            <option value="income">Income</option>
            <option value="saving">Savings & Investments</option>
          </select>
          <button
            className="btn-primary"
            onClick={() => setShowAddCategoryForm(true)}
          >
            + Add Category
          </button>
        </div>
      </div>

      {/* Add Category Form */}
      {showAddCategoryForm && (
        <div className="form-card">
          <h3>Add New Category</h3>
          <form onSubmit={handleCreateCategory} className="inline-form">
            <input
              type="text"
              value={newCategoryName}
              onChange={(e) => setNewCategoryName(e.target.value)}
              placeholder="Category name"
              className="form-input"
              autoFocus
              required
            />
            <select
              value={newCategoryType}
              onChange={(e) => setNewCategoryType(e.target.value)}
              className="form-input"
              style={{ flex: '0 0 200px' }}
            >
              <option value="expense">Expense</option>
              <option value="income">Income</option>
              <option value="saving">Saving & Investment</option>
            </select>
            <button type="submit" className="btn-primary">Save</button>
            <button
              type="button"
              className="btn-secondary"
              onClick={() => {
                setShowAddCategoryForm(false)
                setNewCategoryName('')
                setNewCategoryType('expense')
              }}
            >
              Cancel
            </button>
          </form>
        </div>
      )}

      {/* Categories List */}
      <div className="categories-list">
        {filteredCategories.length === 0 ? (
          <div className="empty-state">
            <p>{filterType === 'all' ? 'No categories yet. Add your first category above!' : `No ${getCategoryTypeLabel(filterType).toLowerCase()} categories yet.`}</p>
          </div>
        ) : (
          filteredCategories.map((category) => (
            <div key={category.id} className="category-item">
              <div className="category-main">
                <div className="category-info">
                  {editingCategory === category.id ? (
                    <form
                      onSubmit={(e) => {
                        e.preventDefault()
                        const input = e.target.querySelector('input')
                        handleUpdateCategory(category.id, input.value)
                      }}
                      className="inline-form"
                    >
                      <input
                        type="text"
                        defaultValue={category.name}
                        className="form-input"
                        autoFocus
                        required
                      />
                      <button type="submit" className="btn-small btn-primary">Save</button>
                      <button
                        type="button"
                        className="btn-small btn-secondary"
                        onClick={() => setEditingCategory(null)}
                      >
                        Cancel
                      </button>
                    </form>
                  ) : (
                    <>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <h3 className="category-name">{category.name}</h3>
                        <span className={`type-badge type-${category.category_type}`}>
                          {getCategoryTypeLabel(category.category_type)}
                        </span>
                      </div>
                      <div className="category-stats">
                        <span className="stat">{category.expense_count} items</span>
                        <span className="stat-separator">•</span>
                        <span className="stat">{formatAmount(category.total_amount)}</span>
                        <span className="stat-separator">•</span>
                        <span className="stat">{category.subcategories?.length || 0} subcategories</span>
                      </div>
                    </>
                  )}
                </div>

                {editingCategory !== category.id && (
                  <div className="category-actions">
                    <button
                      className="btn-icon"
                      onClick={() => setEditingCategory(category.id)}
                      title="Rename"
                    >
                      Edit
                    </button>
                    <button
                      className="btn-icon"
                      onClick={() => setMergingCategory(mergingCategory === category.id ? null : category.id)}
                      title="Merge"
                    >
                      Merge
                    </button>
                    <button
                      className="btn-icon"
                      onClick={() => setShowAddSubcategoryForm(showAddSubcategoryForm === category.id ? null : category.id)}
                      title="Add Subcategory"
                    >
                      + Sub
                    </button>
                    <button
                      className="btn-icon btn-danger"
                      onClick={() => handleDeleteCategory(category.id, category.name)}
                      title="Deactivate"
                    >
                      Delete
                    </button>
                  </div>
                )}
              </div>

              {/* Merge Target Selection */}
              {mergingCategory === category.id && (
                <div className="merge-panel">
                  <p>Merge "{category.name}" into:</p>
                  <div className="merge-options">
                    {categories
                      .filter(c => c.id !== category.id)
                      .map(targetCat => (
                        <button
                          key={targetCat.id}
                          className="merge-option"
                          onClick={() => handleMergeCategories(category.id, targetCat.id)}
                        >
                          {targetCat.name}
                        </button>
                      ))}
                  </div>
                  <button
                    className="btn-secondary btn-small"
                    onClick={() => setMergingCategory(null)}
                  >
                    Cancel
                  </button>
                </div>
              )}

              {/* Add Subcategory Form */}
              {showAddSubcategoryForm === category.id && (
                <div className="subcategory-form">
                  <form onSubmit={(e) => handleCreateSubcategory(e, category.id)} className="inline-form">
                    <input
                      type="text"
                      value={newSubcategoryName}
                      onChange={(e) => setNewSubcategoryName(e.target.value)}
                      placeholder="Subcategory name"
                      className="form-input"
                      autoFocus
                      required
                    />
                    <button type="submit" className="btn-primary btn-small">Save</button>
                    <button
                      type="button"
                      className="btn-secondary btn-small"
                      onClick={() => {
                        setShowAddSubcategoryForm(null)
                        setNewSubcategoryName('')
                      }}
                    >
                      Cancel
                    </button>
                  </form>
                </div>
              )}

              {/* Subcategories List */}
              {category.subcategories && category.subcategories.length > 0 && (
                <div className="subcategories-list">
                  {category.subcategories.map(sub => (
                    <div key={sub.id} className="subcategory-item">
                      <span className="subcategory-name">{sub.name}</span>
                      <button
                        className="btn-icon btn-small"
                        onClick={() => handleDeleteSubcategory(sub.id, sub.name)}
                        title="Deactivate"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Info Box */}
      <div className="info-box">
        <div className="info-icon">i</div>
        <div>
          <p><strong>Tips:</strong></p>
          <ul>
            <li>Rename categories to fix capitalization or typos</li>
            <li>Merge duplicate categories (e.g., "car" and "Car") to combine their expenses</li>
            <li>Add subcategories to organize expenses within a category</li>
            <li>Deactivating a category hides it but preserves expense history</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default CategoryManagement
