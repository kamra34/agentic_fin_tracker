import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Transactions from './pages/Transactions'
import Categories from './pages/Categories'
import Profile from './pages/Profile'
import MonthlyExpenses from './pages/MonthlyExpenses'
import Navigation from './components/Navigation'
import { CurrencyProvider } from './context/CurrencyContext'
import './App.css'

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token')

  if (!token) {
    return <Navigate to="/login" replace />
  }

  return children
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <CurrencyProvider>
                <div className="app">
                  <Navigation />
                  <main className="main-content">
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/monthly" element={<MonthlyExpenses />} />
                      <Route path="/transactions" element={<Transactions />} />
                      <Route path="/categories" element={<Categories />} />
                      <Route path="/profile" element={<Profile />} />
                    </Routes>
                  </main>
                </div>
              </CurrencyProvider>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  )
}

export default App
