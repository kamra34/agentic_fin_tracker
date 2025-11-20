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

function Profile() {
  const [user, setUser] = useState(null)
  const [formData, setFormData] = useState({
    full_name: '',
    currency: 'SEK'
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
        full_name: data.full_name,
        currency: data.currency
      })
    } catch (error) {
      console.error('Error fetching profile:', error)
      setMessage({ type: 'error', text: 'Failed to load profile' })
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      setSaving(true)
      setMessage({ type: '', text: '' })

      const updated = await updateProfile(formData)
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

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <div className="profile">
      <h2 className="page-title">Profile Settings</h2>

      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="profile-container">
        <div className="profile-section">
          <h3>Account Information</h3>
          <div className="info-field">
            <label>Email</label>
            <p>{user?.email}</p>
          </div>
          <div className="info-field">
            <label>Member Since</label>
            <p>{new Date(user?.created_at).toLocaleDateString()}</p>
          </div>
        </div>

        <div className="profile-section">
          <h3>Settings</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="full_name">Full Name</label>
              <input
                type="text"
                id="full_name"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                required
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="currency">Currency</label>
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
                This currency will be used throughout the application
              </p>
            </div>

            <button type="submit" disabled={saving} className="btn-primary">
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default Profile
