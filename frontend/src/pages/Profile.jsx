import { useState, useEffect } from 'react'
import { getCurrentUser, updateProfile } from '../services/api'
import './Profile.css'

const CURRENCIES = [
  { code: 'SEK', name: 'Swedish Krona (SEK)', symbol: 'kr' },
  { code: 'USD', name: 'US Dollar (USD)', symbol: '$' },
  { code: 'EUR', name: 'Euro (EUR)', symbol: '€' },
  { code: 'GBP', name: 'British Pound (GBP)', symbol: '£' },
  { code: 'JPY', name: 'Japanese Yen (JPY)', symbol: '¥' },
  { code: 'CNY', name: 'Chinese Yuan (CNY)', symbol: '¥' },
  { code: 'CHF', name: 'Swiss Franc (CHF)', symbol: 'Fr' },
  { code: 'CAD', name: 'Canadian Dollar (CAD)', symbol: '$' },
  { code: 'AUD', name: 'Australian Dollar (AUD)', symbol: '$' }
]

const TIMEZONES = [
  { value: 'UTC', label: 'UTC (Coordinated Universal Time)' },
  { value: 'Europe/Stockholm', label: 'Europe/Stockholm (CET/CEST)' },
  { value: 'Europe/London', label: 'Europe/London (GMT/BST)' },
  { value: 'Europe/Paris', label: 'Europe/Paris (CET/CEST)' },
  { value: 'Europe/Berlin', label: 'Europe/Berlin (CET/CEST)' },
  { value: 'America/New_York', label: 'America/New York (EST/EDT)' },
  { value: 'America/Chicago', label: 'America/Chicago (CST/CDT)' },
  { value: 'America/Denver', label: 'America/Denver (MST/MDT)' },
  { value: 'America/Los_Angeles', label: 'America/Los Angeles (PST/PDT)' },
  { value: 'America/Toronto', label: 'America/Toronto (EST/EDT)' },
  { value: 'Asia/Tokyo', label: 'Asia/Tokyo (JST)' },
  { value: 'Asia/Shanghai', label: 'Asia/Shanghai (CST)' },
  { value: 'Asia/Dubai', label: 'Asia/Dubai (GST)' },
  { value: 'Asia/Kolkata', label: 'Asia/Kolkata (IST)' },
  { value: 'Australia/Sydney', label: 'Australia/Sydney (AEDT/AEST)' },
  { value: 'Pacific/Auckland', label: 'Pacific/Auckland (NZDT/NZST)' }
]

const HOUSING_TYPES = [
  { value: 'own_house', label: 'Own House' },
  { value: 'own_apartment', label: 'Own Apartment' },
  { value: 'rent_house', label: 'Rent House' },
  { value: 'rent_apartment', label: 'Rent Apartment' },
  { value: 'other', label: 'Other' }
]

function Profile() {
  const [user, setUser] = useState(null)
  const [formData, setFormData] = useState({
    full_name: '',
    currency: 'SEK',
    timezone: 'UTC',
    household_members: '',
    num_vehicles: '',
    housing_type: '',
    house_size_sqm: '',
    monthly_income_goal: '',
    monthly_savings_goal: ''
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    fetchUserProfile()
  }, [])

  const fetchUserProfile = async () => {
    try {
      setLoading(true)
      const data = await getCurrentUser()
      setUser(data)
      setFormData({
        full_name: data.full_name || '',
        currency: data.currency || 'SEK',
        timezone: data.timezone || 'UTC',
        household_members: data.household_members || '',
        num_vehicles: data.num_vehicles || '',
        housing_type: data.housing_type || '',
        house_size_sqm: data.house_size_sqm || '',
        monthly_income_goal: data.monthly_income_goal || '',
        monthly_savings_goal: data.monthly_savings_goal || ''
      })
    } catch (error) {
      console.error('Error fetching profile:', error)
      setMessage({ type: 'error', text: 'Failed to load profile' })
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      setSaving(true)
      setMessage({ type: '', text: '' })

      // Prepare data - convert empty strings to null for numeric fields
      const dataToSubmit = {
        ...formData,
        household_members: formData.household_members === '' ? null : parseInt(formData.household_members),
        num_vehicles: formData.num_vehicles === '' ? null : parseInt(formData.num_vehicles),
        house_size_sqm: formData.house_size_sqm === '' ? null : parseInt(formData.house_size_sqm),
        monthly_income_goal: formData.monthly_income_goal === '' ? null : parseFloat(formData.monthly_income_goal),
        monthly_savings_goal: formData.monthly_savings_goal === '' ? null : parseFloat(formData.monthly_savings_goal)
      }

      const updated = await updateProfile(dataToSubmit)
      setUser(updated)
      setMessage({ type: 'success', text: 'Profile updated successfully!' })

      // Reload page after 1 second to apply currency changes
      setTimeout(() => {
        window.location.reload()
      }, 1000)
    } catch (error) {
      console.error('Error updating profile:', error)
      setMessage({ type: 'error', text: error.message || 'Failed to update profile' })
    } finally {
      setSaving(false)
    }
  }

  const getInitials = () => {
    if (!user?.full_name) return user?.email?.charAt(0).toUpperCase() || 'U'
    const names = user.full_name.split(' ')
    if (names.length >= 2) {
      return names[0].charAt(0).toUpperCase() + names[names.length - 1].charAt(0).toUpperCase()
    }
    return user.full_name.charAt(0).toUpperCase()
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading profile...</p>
      </div>
    )
  }

  return (
    <div className="profile">
      {/* Profile Header */}
      <div className="profile-header">
        <div className="profile-header-content">
          <div className="profile-avatar">{getInitials()}</div>
          <div className="profile-header-info">
            <h1 className="profile-name">{user?.full_name || 'User Profile'}</h1>
            <p className="profile-email">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path d="M3 4a2 2 0 00-2 2v1.161l8.441 4.221a1.5 1.5 0 001.418 0L19 7.162V6a2 2 0 00-2-2H3z" />
                <path d="M19 8.839l-7.77 3.885a2.5 2.5 0 01-2.46 0L1 8.839V14a2 2 0 002 2h14a2 2 0 002-2V8.839z" />
              </svg>
              {user?.email}
            </p>
            <div className="profile-meta">
              <div className="profile-meta-item">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                </svg>
                <span>Member since {new Date(user?.created_at).toLocaleDateString()}</span>
              </div>
              <div className="profile-meta-item">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
                </svg>
                <span>Currency: {user?.currency || 'SEK'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      {message.text && (
        <div className={`message ${message.type}`}>
          {message.type === 'success' ? (
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          )}
          {message.text}
        </div>
      )}

      {/* Profile Sections */}
      <div className="profile-sections">
        {/* Basic Information Section */}
        <div className="profile-section">
          <div className="profile-section-header">
            <div className="profile-section-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
              </svg>
            </div>
            <h3>Basic Information</h3>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="full_name">Full Name <span className="required">*</span></label>
              <input
                type="text"
                id="full_name"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                required
                className="form-input"
                placeholder="Enter your full name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="currency">Preferred Currency <span className="required">*</span></label>
              <select
                id="currency"
                name="currency"
                value={formData.currency}
                onChange={handleChange}
                className="form-select"
              >
                {CURRENCIES.map((curr) => (
                  <option key={curr.code} value={curr.code}>
                    {curr.name}
                  </option>
                ))}
              </select>
              <p className="field-hint">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                This currency will be used throughout the application
              </p>
            </div>

            <div className="form-group">
              <label htmlFor="timezone">Timezone</label>
              <select
                id="timezone"
                name="timezone"
                value={formData.timezone}
                onChange={handleChange}
                className="form-select"
              >
                {TIMEZONES.map((tz) => (
                  <option key={tz.value} value={tz.value}>
                    {tz.label}
                  </option>
                ))}
              </select>
              <p className="field-hint">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                Your timezone helps the AI assistant understand your local time
              </p>
            </div>

            <button type="submit" disabled={saving} className="btn-primary">
              {saving ? 'Saving Changes...' : 'Save Changes'}
            </button>
          </form>
        </div>

        {/* Household Information Section */}
        <div className="profile-section">
          <div className="profile-section-header">
            <div className="profile-section-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
              </svg>
            </div>
            <h3>Household Details</h3>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="household_members">Household Members</label>
              <input
                type="number"
                id="household_members"
                name="household_members"
                value={formData.household_members}
                onChange={handleChange}
                min="1"
                className="form-input"
                placeholder="Number of people in your household"
              />
              <p className="field-hint">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                Include yourself and all dependents
              </p>
            </div>

            <div className="form-group">
              <label htmlFor="housing_type">Housing Type</label>
              <select
                id="housing_type"
                name="housing_type"
                value={formData.housing_type}
                onChange={handleChange}
                className="form-select"
              >
                <option value="">Select housing type</option>
                {HOUSING_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="house_size_sqm">House Size (m²)</label>
              <input
                type="number"
                id="house_size_sqm"
                name="house_size_sqm"
                value={formData.house_size_sqm}
                onChange={handleChange}
                min="0"
                className="form-input"
                placeholder="Living area in square meters"
              />
            </div>

            <button type="submit" disabled={saving} className="btn-primary">
              {saving ? 'Saving Changes...' : 'Save Changes'}
            </button>
          </form>
        </div>

        {/* Assets Section */}
        <div className="profile-section">
          <div className="profile-section-header">
            <div className="profile-section-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
                <path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1V5a1 1 0 00-1-1H3zM14 7a1 1 0 00-1 1v6.05A2.5 2.5 0 0115.95 16H17a1 1 0 001-1v-5a1 1 0 00-.293-.707l-2-2A1 1 0 0015 7h-1z" />
              </svg>
            </div>
            <h3>Assets</h3>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="num_vehicles">Number of Vehicles</label>
              <input
                type="number"
                id="num_vehicles"
                name="num_vehicles"
                value={formData.num_vehicles}
                onChange={handleChange}
                min="0"
                className="form-input"
                placeholder="Cars, motorcycles, etc."
              />
              <p className="field-hint">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                Total vehicles owned or leased
              </p>
            </div>

            <button type="submit" disabled={saving} className="btn-primary">
              {saving ? 'Saving Changes...' : 'Save Changes'}
            </button>
          </form>
        </div>

        {/* Financial Goals Section */}
        <div className="profile-section">
          <div className="profile-section-header">
            <div className="profile-section-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
              </svg>
            </div>
            <h3>Financial Goals</h3>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="monthly_income_goal">Monthly Income Goal</label>
              <input
                type="number"
                id="monthly_income_goal"
                name="monthly_income_goal"
                value={formData.monthly_income_goal}
                onChange={handleChange}
                min="0"
                step="0.01"
                className="form-input"
                placeholder="Target monthly income"
              />
              <p className="field-hint">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                Your target monthly income amount
              </p>
            </div>

            <div className="form-group">
              <label htmlFor="monthly_savings_goal">Monthly Savings Goal</label>
              <input
                type="number"
                id="monthly_savings_goal"
                name="monthly_savings_goal"
                value={formData.monthly_savings_goal}
                onChange={handleChange}
                min="0"
                step="0.01"
                className="form-input"
                placeholder="Target monthly savings"
              />
              <p className="field-hint">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                How much you aim to save each month
              </p>
            </div>

            <button type="submit" disabled={saving} className="btn-primary">
              {saving ? 'Saving Changes...' : 'Save Changes'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default Profile
