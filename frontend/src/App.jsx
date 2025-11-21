import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile'
import MonthlyExpenses from './pages/MonthlyExpenses'
import ControlCenter from './pages/ControlCenter'
import Management from './pages/Management'
import Savings from './pages/Savings'
import Chat from './pages/Chat'
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
  const token = localStorage.getItem('token')

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={token ? <Navigate to="/dashboard" replace /> : <Landing />} />
        <Route path="/login" element={token ? <Navigate to="/dashboard" replace /> : <Login />} />
        <Route path="/register" element={token ? <Navigate to="/dashboard" replace /> : <Register />} />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <CurrencyProvider>
                <div className="app">
                  <Navigation />
                  <main className="main-content">
                    <Dashboard />
                  </main>
                </div>
              </CurrencyProvider>
            </ProtectedRoute>
          }
        />
        <Route
          path="/monthly"
          element={
            <ProtectedRoute>
              <CurrencyProvider>
                <div className="app">
                  <Navigation />
                  <main className="main-content">
                    <MonthlyExpenses />
                  </main>
                </div>
              </CurrencyProvider>
            </ProtectedRoute>
          }
        />
        <Route
          path="/control-center"
          element={
            <ProtectedRoute>
              <CurrencyProvider>
                <div className="app">
                  <Navigation />
                  <main className="main-content">
                    <ControlCenter />
                  </main>
                </div>
              </CurrencyProvider>
            </ProtectedRoute>
          }
        />
        <Route
          path="/management/*"
          element={
            <ProtectedRoute>
              <CurrencyProvider>
                <div className="app">
                  <Navigation />
                  <main className="main-content">
                    <Management />
                  </main>
                </div>
              </CurrencyProvider>
            </ProtectedRoute>
          }
        />
        <Route
          path="/savings"
          element={
            <ProtectedRoute>
              <CurrencyProvider>
                <div className="app">
                  <Navigation />
                  <main className="main-content">
                    <Savings />
                  </main>
                </div>
              </CurrencyProvider>
            </ProtectedRoute>
          }
        />
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <CurrencyProvider>
                <div className="app">
                  <Navigation />
                  <main className="main-content">
                    <Chat />
                  </main>
                </div>
              </CurrencyProvider>
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <CurrencyProvider>
                <div className="app">
                  <Navigation />
                  <main className="main-content">
                    <Profile />
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
