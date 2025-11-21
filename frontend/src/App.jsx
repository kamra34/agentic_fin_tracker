import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile'
import MonthlyExpenses from './pages/MonthlyExpenses'
import ControlCenter from './pages/ControlCenter'
import Management from './pages/Management'
import Savings from './pages/Savings'
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
        <Route path="/register" element={<Register />} />
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
                      <Route path="/control-center" element={<ControlCenter />} />
                      <Route path="/management/*" element={<Management />} />
                      <Route path="/savings" element={<Savings />} />
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
