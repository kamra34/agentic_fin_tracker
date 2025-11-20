const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

function getAuthHeaders() {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  }
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
export async function login(username, password) {
  const formData = new URLSearchParams()
  formData.append('username', username)
  formData.append('password', password)

  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData
  })
  return handleResponse(response)
}

export async function getCurrentUser() {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export function logout() {
  localStorage.removeItem('token')
  window.location.href = '/login'
}

export async function updateProfile(data) {
  const response = await fetch(`${API_BASE_URL}/api/auth/profile`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

// Dashboard API
export async function getDashboardStats() {
  const response = await fetch(`${API_BASE_URL}/api/dashboard/stats`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

// Expenses API
export async function getExpenses(skip = 0, limit = 100, filters = {}) {
  const params = new URLSearchParams({ skip, limit, ...filters })
  const response = await fetch(`${API_BASE_URL}/api/expenses?${params}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getExpense(id) {
  const response = await fetch(`${API_BASE_URL}/api/expenses/${id}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function createExpense(data) {
  const response = await fetch(`${API_BASE_URL}/api/expenses`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

export async function updateExpense(id, data) {
  const response = await fetch(`${API_BASE_URL}/api/expenses/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })
  return handleResponse(response)
}

export async function deleteExpense(id) {
  const response = await fetch(`${API_BASE_URL}/api/expenses/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getExpenseCategories() {
  const response = await fetch(`${API_BASE_URL}/api/expenses/categories`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getExpenseSubcategories(category = null) {
  const params = category ? `?category=${category}` : ''
  const response = await fetch(`${API_BASE_URL}/api/expenses/subcategories${params}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

// Monthly Expenses API
export async function getMonthlyExpenses(year, month) {
  const response = await fetch(`${API_BASE_URL}/api/expenses/monthly/list?year=${year}&month=${month}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getMonthlySummary(year, month) {
  const response = await fetch(`${API_BASE_URL}/api/expenses/monthly/summary?year=${year}&month=${month}`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getAvailableMonths() {
  const response = await fetch(`${API_BASE_URL}/api/expenses/monthly/available`, {
    headers: getAuthHeaders()
  })
  return handleResponse(response)
}

export async function getCategoriesStructured() {
  const response = await fetch(`${API_BASE_URL}/api/expenses/categories/structured`, {
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
export const getCategories = getExpenseCategories
