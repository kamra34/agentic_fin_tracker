const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

function getAuthHeaders() {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  }
}

// Performance monitoring helper
const logPerformance = (endpoint, startTime, response) => {
  const endTime = performance.now()
  const duration = (endTime - startTime).toFixed(2)
  const serverTime = response.headers.get('X-Process-Time')

  if (duration > 1000) {
    console.warn(`🐌 SLOW API: ${endpoint}`)
    console.warn(`   Total: ${duration}ms | Server: ${serverTime || 'N/A'}`)
  } else if (duration > 500) {
    console.log(`⚡ API: ${endpoint} - ${duration}ms (Server: ${serverTime || 'N/A'})`)
  } else {
    console.log(`✅ API: ${endpoint} - ${duration}ms (Server: ${serverTime || 'N/A'})`)
  }
}

// Wrapper for fetch with timing
async function timedFetch(url, options = {}) {
  const startTime = performance.now()
  const endpoint = url.replace(API_BASE_URL, '')

  console.log(`🚀 API Request: ${options.method || 'GET'} ${endpoint}`)

  const response = await fetch(url, options)

  logPerformance(endpoint, startTime, response)

  return response
}

async function handleResponse(response) {
  if (response.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    throw new Error('Unauthorized. Please login again.')
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }))
    throw new Error(error.detail || 'An error occurred')
  }

  if (response.status === 204) {
    return null
  }

  return response.json()
}

// Auth API
export async function register(email, password, fullName = '') {
  const response = await timedFetch(`${API_BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password,
      full_name: fullName
    })
  })
  return handleResponse(response)
}

export async function login(username, password) {
  const formData = new URLSearchParams()
  formData.append('username', username)
  formData.append('password', password)

  const response = await timedFetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData
  })
  return handleResponse(response)
}

export async function getCurrentUser() {
  const response = await timedFetch(`${API_BASE_URL}/api/auth/me`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export function logout() {
  localStorage.removeItem('token')
  window.location.href = '/login'
}

export async function updateProfile(data) {
  const response = await timedFetch(`${API_BASE_URL}/api/auth/profile`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

// Dashboard API
export async function getDashboardStats() {
  const response = await timedFetch(`${API_BASE_URL}/api/dashboard/stats`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

// Expenses API
export async function getExpenses(skip = 0, limit = 100, filters = {}) {
  const params = new URLSearchParams({ skip, limit, ...filters })
  const response = await timedFetch(`${API_BASE_URL}/api/expenses?${params}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getExpense(id) {
  const response = await timedFetch(`${API_BASE_URL}/api/expenses/${id}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function createExpense(data) {
  const response = await timedFetch(`${API_BASE_URL}/api/expenses`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

export async function updateExpense(id, data) {
  const response = await timedFetch(`${API_BASE_URL}/api/expenses/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

export async function deleteExpense(id) {
  const response = await timedFetch(`${API_BASE_URL}/api/expenses/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getExpenseCategories() {
  const response = await timedFetch(`${API_BASE_URL}/api/expenses/categories`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getExpenseSubcategories(category = null) {
  const params = category ? `?category=${category}` : ''
  const response = await timedFetch(`${API_BASE_URL}/api/expenses/subcategories${params}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

// Monthly Expenses API
export async function getMonthlyExpenses(year, month) {
  const response = await timedFetch(`${API_BASE_URL}/api/expenses/monthly/list?year=${year}&month=${month}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getMonthlySummary(year, month) {
  const response = await timedFetch(`${API_BASE_URL}/api/expenses/monthly/summary?year=${year}&month=${month}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getAvailableMonths() {
  const response = await timedFetch(`${API_BASE_URL}/api/expenses/monthly/available`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getCategoriesStructured() {
  const response = await timedFetch(`${API_BASE_URL}/api/expenses/categories/structured`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getMonthlyAccountAllocation(year, month) {
  const response = await timedFetch(`${API_BASE_URL}/api/expenses/monthly/account-allocation?year=${year}&month=${month}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

// New Category Management API
export async function getCategories(includeInactive = false) {
  const params = includeInactive ? '?include_inactive=true' : ''
  const response = await timedFetch(`${API_BASE_URL}/api/categories/${params}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getCategoriesWithStats() {
  const response = await timedFetch(`${API_BASE_URL}/api/categories/with-stats`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getCategory(categoryId) {
  const response = await timedFetch(`${API_BASE_URL}/api/categories/${categoryId}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function createCategory(data) {
  const response = await timedFetch(`${API_BASE_URL}/api/categories/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

export async function updateCategory(categoryId, data) {
  const response = await timedFetch(`${API_BASE_URL}/api/categories/${categoryId}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

export async function deleteCategory(categoryId) {
  const response = await timedFetch(`${API_BASE_URL}/api/categories/${categoryId}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function mergeCategories(sourceId, targetId) {
  const response = await timedFetch(`${API_BASE_URL}/api/categories/merge?source_id=${sourceId}&target_id=${targetId}`, {
    method: 'POST',
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getSubcategories(categoryId) {
  const response = await timedFetch(`${API_BASE_URL}/api/categories/${categoryId}/subcategories`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function createSubcategory(data) {
  const response = await timedFetch(`${API_BASE_URL}/api/categories/subcategories`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

export async function updateSubcategory(subcategoryId, data) {
  const response = await timedFetch(`${API_BASE_URL}/api/categories/subcategories/${subcategoryId}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

export async function deleteSubcategory(subcategoryId) {
  const response = await timedFetch(`${API_BASE_URL}/api/categories/subcategories/${subcategoryId}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

// Accounts API
export async function getAccounts() {
  const response = await timedFetch(`${API_BASE_URL}/api/accounts/`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getAccountsWithStats() {
  const response = await timedFetch(`${API_BASE_URL}/api/accounts/with-stats`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getAccount(accountId) {
  const response = await timedFetch(`${API_BASE_URL}/api/accounts/${accountId}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function createAccount(data) {
  const response = await timedFetch(`${API_BASE_URL}/api/accounts/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

export async function updateAccount(accountId, data) {
  const response = await timedFetch(`${API_BASE_URL}/api/accounts/${accountId}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

export async function deleteAccount(accountId) {
  const response = await timedFetch(`${API_BASE_URL}/api/accounts/${accountId}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

// Income Templates API
export async function getIncomeTemplates(includeInactive = false) {
  const params = includeInactive ? '?include_inactive=true' : ''
  const response = await timedFetch(`${API_BASE_URL}/api/incomes/templates${params}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getIncomeTemplate(templateId) {
  const response = await timedFetch(`${API_BASE_URL}/api/incomes/templates/${templateId}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function createIncomeTemplate(data) {
  const response = await timedFetch(`${API_BASE_URL}/api/incomes/templates`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

export async function updateIncomeTemplate(templateId, data) {
  const response = await timedFetch(`${API_BASE_URL}/api/incomes/templates/${templateId}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

export async function deleteIncomeTemplate(templateId) {
  const response = await timedFetch(`${API_BASE_URL}/api/incomes/templates/${templateId}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

// Monthly Incomes API
export async function getMonthlyIncomes(month = null) {
  const params = month ? `?month=${month}` : ''
  const response = await timedFetch(`${API_BASE_URL}/api/incomes/monthly${params}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function generateMonthlyIncomes(month) {
  const response = await timedFetch(`${API_BASE_URL}/api/incomes/generate/${month}`, {
    method: 'POST',
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getMonthlyIncomeTotal(month) {
  const response = await timedFetch(`${API_BASE_URL}/api/incomes/total/${month}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function createMonthlyIncome(data) {
  const response = await timedFetch(`${API_BASE_URL}/api/incomes/monthly`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

export async function updateMonthlyIncome(incomeId, data) {
  const response = await timedFetch(`${API_BASE_URL}/api/incomes/monthly/${incomeId}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

export async function deleteMonthlyIncome(incomeId) {
  const response = await timedFetch(`${API_BASE_URL}/api/incomes/monthly/${incomeId}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

// Expense Templates API
export async function getExpenseTemplates(includeInactive = false) {
  const params = includeInactive ? '?include_inactive=true' : ''
  const response = await timedFetch(`${API_BASE_URL}/api/expenses/templates${params}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getExpenseTemplate(templateId) {
  const response = await timedFetch(`${API_BASE_URL}/api/expenses/templates/${templateId}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function createExpenseTemplate(data) {
  const response = await timedFetch(`${API_BASE_URL}/api/expenses/templates`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

export async function updateExpenseTemplate(templateId, data) {
  const response = await timedFetch(`${API_BASE_URL}/api/expenses/templates/${templateId}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

export async function deleteExpenseTemplate(templateId) {
  const response = await timedFetch(`${API_BASE_URL}/api/expenses/templates/${templateId}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function generateExpensesFromTemplates(year, month) {
  const response = await timedFetch(`${API_BASE_URL}/api/expenses/generate/${year}/${month}`, {
    method: 'POST',
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

// Legacy aliases for compatibility
export const getTransactions = getExpenses
export const getTransaction = getExpense
export const createTransaction = createExpense
export const updateTransaction = updateExpense
export const deleteTransaction = deleteExpense
