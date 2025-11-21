import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './Landing.css'

function Landing() {
  const navigate = useNavigate()
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authMode, setAuthMode] = useState('login') // 'login' or 'register'

  const features = [
    {
      icon: '💰',
      title: 'Smart Expense Tracking',
      description: 'Automatically categorize and track your expenses with intelligent insights. Monitor spending patterns across categories and time periods.',
      gradient: 'linear-gradient(135deg, #ef4444 0%, #f87171 100%)'
    },
    {
      icon: '📊',
      title: 'Investment & Savings',
      description: 'Track your investment portfolios, stocks, crypto, and savings accounts. Monitor real-time returns and performance metrics.',
      gradient: 'linear-gradient(135deg, #9c27b0 0%, #ba68c8 100%)'
    },
    {
      icon: '💵',
      title: 'Income Management',
      description: 'Manage multiple income sources, recurring payments, and one-time earnings. Visualize your cash flow effortlessly.',
      gradient: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)'
    },
    {
      icon: '🤖',
      title: 'AI-Powered Insights',
      description: 'Get intelligent financial recommendations and predictions powered by advanced AI. Chat with your financial assistant anytime.',
      gradient: 'linear-gradient(135deg, #0066cc 0%, #3b82f6 100%)'
    },
    {
      icon: '📈',
      title: 'Advanced Analytics',
      description: 'Comprehensive dashboards with trends, forecasts, and detailed breakdowns. Make data-driven financial decisions.',
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)'
    },
    {
      icon: '🔒',
      title: 'Secure & Private',
      description: 'Bank-level encryption and security. Your financial data is protected with industry-standard security protocols.',
      gradient: 'linear-gradient(135deg, #06b6d4 0%, #22d3ee 100%)'
    }
  ]

  const handleGetStarted = () => {
    setAuthMode('register')
    setShowAuthModal(true)
  }

  const handleLogin = () => {
    setAuthMode('login')
    setShowAuthModal(true)
  }

  const handleAuthSubmit = () => {
    if (authMode === 'login') {
      navigate('/login')
    } else {
      navigate('/register')
    }
  }

  return (
    <div className="landing">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-background">
          <div className="hero-gradient"></div>
          <div className="hero-pattern"></div>
        </div>

        <nav className="landing-nav">
          <div className="nav-brand">
            <div className="brand-icon">
              <svg viewBox="0 0 64 64" fill="none">
                <circle cx="32" cy="32" r="30" fill="#0066CC"/>
                <path d="M32 20 L32 44 M26 26 C26 23 28 22 32 22 C36 22 38 23 38 26 C38 29 36 30 32 30 L32 30 C28 30 26 31 26 34 C26 37 28 38 32 38 C36 38 38 37 38 34"
                      stroke="#FFFFFF" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
              </svg>
            </div>
            <span className="brand-name">FinTrack AI</span>
          </div>
          <button className="nav-login-btn" onClick={handleLogin}>Login</button>
        </nav>

        <div className="hero-content">
          <div className="hero-badge">
            <span className="badge-icon">✨</span>
            <span>AI-Powered Personal Finance Manager</span>
          </div>

          <h1 className="hero-title">
            Take Control of Your
            <span className="hero-title-highlight"> Financial Future</span>
          </h1>

          <p className="hero-description">
            Smart expense tracking, investment monitoring, and AI-powered insights—all in one beautiful platform.
            Make informed financial decisions with real-time analytics and intelligent recommendations.
          </p>

          <div className="hero-cta">
            <button className="cta-primary" onClick={handleGetStarted}>
              Get Started Free
              <span className="cta-arrow">→</span>
            </button>
            <button className="cta-secondary" onClick={() => document.getElementById('features').scrollIntoView({ behavior: 'smooth' })}>
              Explore Features
            </button>
          </div>

          <div className="hero-stats">
            <div className="stat-item">
              <div className="stat-value">100%</div>
              <div className="stat-label">Secure</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <div className="stat-value">AI</div>
              <div className="stat-label">Powered</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <div className="stat-value">24/7</div>
              <div className="stat-label">Tracking</div>
            </div>
          </div>
        </div>

        <div className="hero-visual">
          <div className="dashboard-preview">
            <div className="preview-window">
              <div className="window-header">
                <div className="window-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <div className="window-title">Dashboard</div>
              </div>
              <div className="window-content">
                <div className="preview-kpis">
                  <div className="preview-kpi kpi-success">
                    <div className="kpi-label">Monthly Income</div>
                    <div className="kpi-value">$8,500</div>
                  </div>
                  <div className="preview-kpi kpi-danger">
                    <div className="kpi-label">Expenses</div>
                    <div className="kpi-value">$4,200</div>
                  </div>
                  <div className="preview-kpi kpi-primary">
                    <div className="kpi-label">Net Savings</div>
                    <div className="kpi-value">$4,300</div>
                  </div>
                </div>
                <div className="preview-chart">
                  <div className="chart-bars">
                    <div className="chart-bar" style={{ height: '40%' }}></div>
                    <div className="chart-bar" style={{ height: '65%' }}></div>
                    <div className="chart-bar" style={{ height: '45%' }}></div>
                    <div className="chart-bar" style={{ height: '80%' }}></div>
                    <div className="chart-bar" style={{ height: '60%' }}></div>
                    <div className="chart-bar" style={{ height: '90%' }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section" id="features">
        <div className="section-header">
          <h2 className="section-title">Everything You Need to Succeed</h2>
          <p className="section-subtitle">
            Powerful features designed to give you complete control over your finances
          </p>
        </div>

        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card" style={{ '--delay': `${index * 0.1}s` }}>
              <div className="feature-icon" style={{ background: feature.gradient }}>
                {feature.icon}
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2 className="cta-title">Ready to Transform Your Financial Life?</h2>
          <p className="cta-description">
            Join thousands of users who are already taking control of their finances with FinTrack AI
          </p>
          <button className="cta-button" onClick={handleGetStarted}>
            Start Your Journey Today
            <span className="button-glow"></span>
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <div className="brand-icon">
              <svg viewBox="0 0 64 64" fill="none">
                <circle cx="32" cy="32" r="30" fill="#0066CC"/>
                <path d="M32 20 L32 44 M26 26 C26 23 28 22 32 22 C36 22 38 23 38 26 C38 29 36 30 32 30 L32 30 C28 30 26 31 26 34 C26 37 28 38 32 38 C36 38 38 37 38 34"
                      stroke="#FFFFFF" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
              </svg>
            </div>
            <span className="brand-name">FinTrack AI</span>
          </div>
          <p className="footer-text">
            Smart Personal Finance Manager with AI-Powered Insights
          </p>
          <p className="footer-copyright">
            © 2025 FinTrack AI. All rights reserved.
          </p>
        </div>
      </footer>

      {/* Auth Modal */}
      {showAuthModal && (
        <div className="auth-modal-overlay" onClick={() => setShowAuthModal(false)}>
          <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowAuthModal(false)}>×</button>
            <div className="modal-content">
              <h2 className="modal-title">
                {authMode === 'login' ? 'Welcome Back' : 'Get Started Free'}
              </h2>
              <p className="modal-subtitle">
                {authMode === 'login'
                  ? 'Sign in to access your financial dashboard'
                  : 'Create your account and start managing your finances'}
              </p>
              <button className="modal-cta" onClick={handleAuthSubmit}>
                {authMode === 'login' ? 'Go to Login' : 'Go to Sign Up'}
              </button>
              <p className="modal-switch">
                {authMode === 'login' ? "Don't have an account? " : "Already have an account? "}
                <button onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}>
                  {authMode === 'login' ? 'Sign up' : 'Log in'}
                </button>
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Landing
