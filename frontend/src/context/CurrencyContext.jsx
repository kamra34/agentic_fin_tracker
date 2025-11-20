import { createContext, useContext, useState, useEffect } from 'react'
import { getCurrentUser } from '../services/api'

const CurrencyContext = createContext()

export const CURRENCY_SYMBOLS = {
  'SEK': 'kr',
  'USD': '$',
  'EUR': '€',
  'GBP': '£',
  'JPY': '¥',
  'CNY': '¥',
  'CHF': 'Fr',
  'CAD': '$',
  'AUD': '$'
}

export function CurrencyProvider({ children }) {
  const [currency, setCurrency] = useState('SEK')
  const [symbol, setSymbol] = useState('kr')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadUserCurrency()
  }, [])

  const loadUserCurrency = async () => {
    try {
      const user = await getCurrentUser()
      if (user && user.currency) {
        setCurrency(user.currency)
        setSymbol(CURRENCY_SYMBOLS[user.currency] || user.currency)
      }
    } catch (error) {
      console.error('Error loading currency:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatAmount = (amount) => {
    if (amount === null || amount === undefined) return `0 ${symbol}`

    const numAmount = parseFloat(amount)

    // Use Intl.NumberFormat for proper locale-aware formatting
    const formatter = new Intl.NumberFormat('sv-SE', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
      useGrouping: true
    })

    const formattedNumber = formatter.format(numAmount)

    // For Swedish Krona, put symbol after the number
    if (currency === 'SEK') {
      return `${formattedNumber} ${symbol}`
    }

    // For other currencies, put symbol before
    return `${symbol}${formattedNumber}`
  }

  const value = {
    currency,
    symbol,
    formatAmount,
    loading
  }

  return (
    <CurrencyContext.Provider value={value}>
      {children}
    </CurrencyContext.Provider>
  )
}

export function useCurrency() {
  const context = useContext(CurrencyContext)
  if (context === undefined) {
    throw new Error('useCurrency must be used within a CurrencyProvider')
  }
  return context
}
