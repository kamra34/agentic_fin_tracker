import { Link, useLocation } from 'react-router-dom'
import { logout } from '../services/api'
import './Navigation.css'

function Navigation() {
  const location = useLocation()

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      logout()
    }
  }

  return (
    <nav className="navigation">
      <div className="nav-container">
        <h1 className="nav-logo">Financial Tracker</h1>
        <ul className="nav-links">
          <li>
            <Link
              to="/"
              className={location.pathname === '/' ? 'active' : ''}
            >
              Dashboard
            </Link>
          </li>
          <li>
            <Link
              to="/monthly"
              className={location.pathname === '/monthly' ? 'active' : ''}
            >
              Monthly
            </Link>
          </li>
          <li>
            <Link
              to="/categories"
              className={location.pathname === '/categories' ? 'active' : ''}
            >
              Categories
            </Link>
          </li>
          <li>
            <Link
              to="/profile"
              className={location.pathname === '/profile' ? 'active' : ''}
            >
              Profile
            </Link>
          </li>
          <li>
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </li>
        </ul>
      </div>
    </nav>
  )
}

export default Navigation
