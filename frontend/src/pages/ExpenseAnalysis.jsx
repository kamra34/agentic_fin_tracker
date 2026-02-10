import { useEffect, useMemo, useState } from 'react'
import { useCurrency } from '../context/CurrencyContext'
import { getExpenseAnalyticsDetail } from '../services/api'
import './ExpenseAnalysis.css'

const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

const formatMonthLabel = (year, month) => {
  const monthLabel = MONTH_LABELS[month - 1] || month
  const shortYear = typeof year === 'number' ? String(year).slice(-2) : ''
  return shortYear ? `${monthLabel} '${shortYear}` : `${monthLabel}`
}

const formatMonthYear = (item) => {
  if (!item) return 'N/A'
  return formatMonthLabel(item.year, item.month)
}

function ExpenseAnalysis() {
  const { formatAmount } = useCurrency()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedCategoryId, setSelectedCategoryId] = useState(null)

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        const detail = await getExpenseAnalyticsDetail()
        setData(detail)
      } catch (error) {
        console.error('Error fetching expense analysis detail:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchDetail()
  }, [])

  const categories = data?.categories || []
  const sortedCategories = useMemo(() => {
    return [...categories].sort((a, b) => b.total_amount - a.total_amount)
  }, [categories])

  const filteredCategories = useMemo(() => {
    const term = search.trim().toLowerCase()
    if (!term) return sortedCategories
    return sortedCategories.filter(category => category.name.toLowerCase().includes(term))
  }, [search, sortedCategories])

  useEffect(() => {
    if (!selectedCategoryId && sortedCategories.length > 0) {
      setSelectedCategoryId(sortedCategories[0].id)
    }
  }, [sortedCategories, selectedCategoryId])

  const selectedCategory = categories.find(category => category.id === selectedCategoryId) || sortedCategories[0]
  const selectedCategoryKey = selectedCategory ? String(selectedCategory.id) : null
  const categoryYearly = selectedCategoryKey ? (data?.category_yearly?.[selectedCategoryKey] || []) : []
  const categoryMonthly = selectedCategoryKey ? (data?.category_monthly?.[selectedCategoryKey] || []) : []

  const yearlyTotals = data?.yearly_totals || []
  const monthlyTotals = data?.monthly_totals || []

  const yearlyMax = yearlyTotals.length > 0 ? Math.max(...yearlyTotals.map(item => item.total)) : 0
  const monthlyMax = monthlyTotals.length > 0 ? Math.max(...monthlyTotals.map(item => item.total)) : 0
  const categoryYearlyMax = categoryYearly.length > 0 ? Math.max(...categoryYearly.map(item => item.total)) : 0
  const categoryMonthlyMax = categoryMonthly.length > 0 ? Math.max(...categoryMonthly.map(item => item.total)) : 0

  const summary = data?.summary

  const [topIncrease, topDecrease, moverThresholds] = useMemo(() => {
    const withYoy = categories.filter(category => category.yoy_change !== null)
    if (withYoy.length === 0) return [null, null]

    const total12 = summary?.last_12_total || 0
    const minBase = Math.max(500, total12 * 0.01)
    const minCurrent = Math.max(200, total12 * 0.003)

    const meaningful = withYoy.filter(category => (
      category.prev_12_total >= minBase && category.last_12_total >= minCurrent
    ))

    if (meaningful.length === 0) return [null, null, { minBase, minCurrent }]

    const sorted = [...meaningful].sort((a, b) => b.yoy_change - a.yoy_change)
    return [sorted[0], sorted[sorted.length - 1], { minBase, minCurrent }]
  }, [categories, summary])

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  if (!data) {
    return (
      <div className="expense-analysis">
        <div className="analysis-empty">No analysis data available.</div>
      </div>
    )
  }

  return (
    <div className="expense-analysis">
      <div className="analysis-header">
        <div>
          <h1>Expense Deep Dive</h1>
          <p>See every category, every trend, and the biggest movers in one place.</p>
        </div>
      </div>

      <div className="analysis-kpi-grid">
        <div className="analysis-kpi-card">
          <div className="analysis-kpi-label">Total Spend</div>
          <div className="analysis-kpi-value">{formatAmount(summary.total_amount)}</div>
          <div className="analysis-kpi-meta">{summary.expense_count} transactions</div>
        </div>
        <div className="analysis-kpi-card">
          <div className="analysis-kpi-label">Avg Monthly</div>
          <div className="analysis-kpi-value">{formatAmount(summary.avg_monthly)}</div>
          <div className="analysis-kpi-meta">{summary.months_of_data} months tracked</div>
        </div>
        <div className="analysis-kpi-card">
          <div className="analysis-kpi-label">Avg Transaction</div>
          <div className="analysis-kpi-value">{formatAmount(summary.avg_transaction)}</div>
          <div className="analysis-kpi-meta">Across all expenses</div>
        </div>
        <div className="analysis-kpi-card">
          <div className="analysis-kpi-label">YoY (Last 12M)</div>
          <div className={`analysis-kpi-value ${summary.yoy_change_pct >= 0 ? 'positive' : 'negative'}`}>
            {summary.yoy_change_pct === null ? 'New' : `${summary.yoy_change_pct}%`}
          </div>
          <div className="analysis-kpi-meta">
            {formatAmount(summary.last_12_total)} vs {formatAmount(summary.prev_12_total)}
          </div>
        </div>
        <div className="analysis-kpi-card">
          <div className="analysis-kpi-label">Peak Month</div>
          <div className="analysis-kpi-value">{formatMonthYear(summary.peak_month)}</div>
          <div className="analysis-kpi-meta">
            {summary.peak_month ? formatAmount(summary.peak_month.total) : 'N/A'}
          </div>
        </div>
        <div className="analysis-kpi-card">
          <div className="analysis-kpi-label">Peak Year</div>
          <div className="analysis-kpi-value">{summary.peak_year?.year || 'N/A'}</div>
          <div className="analysis-kpi-meta">
            {summary.peak_year ? formatAmount(summary.peak_year.total) : 'N/A'}
          </div>
        </div>
      </div>

      <div className="analysis-insights">
        <div className="insight-card">
          <div className="insight-label">Biggest Jump</div>
          {topIncrease ? (
            <>
              <div className="insight-title">{topIncrease.name}</div>
              <div className="insight-value positive">+{topIncrease.yoy_change}%</div>
              <div className="insight-meta">{formatAmount(topIncrease.last_12_total)} last 12M</div>
            </>
          ) : (
            <div className="insight-meta">Not enough meaningful history yet.</div>
          )}
        </div>
        <div className="insight-card">
          <div className="insight-label">Biggest Drop</div>
          {topDecrease ? (
            <>
              <div className="insight-title">{topDecrease.name}</div>
              <div className="insight-value negative">{topDecrease.yoy_change}%</div>
              <div className="insight-meta">{formatAmount(topDecrease.last_12_total)} last 12M</div>
            </>
          ) : (
            <div className="insight-meta">Not enough meaningful history yet.</div>
          )}
        </div>
        <div className="insight-card insight-note">
          <div className="insight-label">Meaningful Movers</div>
          <div className="insight-meta">
            Requires at least {formatAmount(moverThresholds?.minBase || 0)} in the prior 12 months and
            {` ${formatAmount(moverThresholds?.minCurrent || 0)}`} in the last 12 months.
          </div>
        </div>
      </div>

      <div className="analysis-section">
        <div className="analysis-section-header">
          <h2>Yearly Comparison</h2>
          <span>How your spend stacks up year over year.</span>
        </div>
        <div className="yearly-bars">
          {yearlyTotals.map(item => {
            const widthPercent = yearlyMax > 0 ? (item.total / yearlyMax) * 100 : 0
            return (
              <div className="yearly-row" key={item.year}>
                <span className="year-label">{item.year}</span>
                <div className="year-bar">
                  <div className="year-bar-fill" style={{ width: `${widthPercent}%` }}></div>
                </div>
                <span className="year-amount">{formatAmount(item.total)}</span>
              </div>
            )
          })}
        </div>
      </div>

      <div className="analysis-section">
        <div className="analysis-section-header">
          <h2>Monthly Trend (Last 24 Months)</h2>
          <span>Spot seasonality and momentum at a glance.</span>
        </div>
        <div className="monthly-bars">
          {monthlyTotals.map((item, index) => {
            const heightPercent = monthlyMax > 0 ? (item.total / monthlyMax) * 100 : 0
            const label = formatMonthLabel(item.year, item.month)
            return (
              <div key={`${item.year}-${item.month}-${index}`} className="monthly-bar-wrapper">
                <div className="monthly-bar" style={{ height: `${heightPercent}%` }} title={`${label}: ${formatAmount(item.total)}`}></div>
                <div className="monthly-label">{label}</div>
              </div>
            )
          })}
        </div>
      </div>

      <div className="analysis-section analysis-split">
        <div className="analysis-panel">
          <div className="analysis-section-header">
            <h2>Category Explorer</h2>
            <span>All categories ranked by total spend.</span>
          </div>
          <div className="category-search">
            <input
              type="text"
              placeholder="Search categories..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </div>
          <div className="category-table">
            <div className="category-table-header">
              <span>Category</span>
              <span>Total</span>
              <span>% of Total</span>
              <span>Last 12M</span>
              <span>YoY</span>
            </div>
            <div className="category-table-body">
              {filteredCategories.map(category => (
                <div
                  key={category.id}
                  className={`category-row ${category.id === selectedCategoryId ? 'active' : ''}`}
                  onClick={() => setSelectedCategoryId(category.id)}
                >
                  <span className="category-name">{category.name}</span>
                  <span>{formatAmount(category.total_amount)}</span>
                  <span>{category.percentage.toFixed(1)}%</span>
                  <span>{formatAmount(category.last_12_total)}</span>
                  <span className={category.yoy_change >= 0 ? 'positive' : 'negative'}>
                    {category.yoy_change === null ? 'New' : `${category.yoy_change}%`}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="analysis-panel">
          <div className="analysis-section-header">
            <h2>Category Spotlight</h2>
            <span>{selectedCategory ? selectedCategory.name : 'Select a category'}</span>
          </div>

          {selectedCategory ? (
            <>
              <div className="category-spotlight">
                <div className="spotlight-card">
                  <div className="spotlight-label">Total Spend</div>
                  <div className="spotlight-value">{formatAmount(selectedCategory.total_amount)}</div>
                </div>
                <div className="spotlight-card">
                  <div className="spotlight-label">Last 12M</div>
                  <div className="spotlight-value">{formatAmount(selectedCategory.last_12_total)}</div>
                </div>
                <div className="spotlight-card">
                  <div className="spotlight-label">YoY Change</div>
                  <div className={`spotlight-value ${selectedCategory.yoy_change >= 0 ? 'positive' : 'negative'}`}>
                    {selectedCategory.yoy_change === null ? 'New' : `${selectedCategory.yoy_change}%`}
                  </div>
                </div>
              </div>

              <div className="spotlight-section">
                <div className="spotlight-title">Yearly Breakdown</div>
                <div className="yearly-bars compact">
                  {categoryYearly.map(item => {
                    const widthPercent = categoryYearlyMax > 0 ? (item.total / categoryYearlyMax) * 100 : 0
                    return (
                      <div className="yearly-row" key={`${selectedCategory.id}-${item.year}`}>
                        <span className="year-label">{item.year}</span>
                        <div className="year-bar">
                          <div className="year-bar-fill" style={{ width: `${widthPercent}%` }}></div>
                        </div>
                        <span className="year-amount">{formatAmount(item.total)}</span>
                      </div>
                    )
                  })}
                </div>
              </div>

              <div className="spotlight-section">
                <div className="spotlight-title">Monthly Pulse (Last 12M)</div>
                <div className="monthly-bars compact">
                  {categoryMonthly.map((item, index) => {
                    const heightPercent = categoryMonthlyMax > 0 ? (item.total / categoryMonthlyMax) * 100 : 0
                    const label = formatMonthLabel(item.year, item.month)
                    return (
                      <div key={`${item.year}-${item.month}-${index}`} className="monthly-bar-wrapper">
                        <div className="monthly-bar" style={{ height: `${heightPercent}%` }} title={`${label}: ${formatAmount(item.total)}`}></div>
                        <div className="monthly-label">{label}</div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </>
          ) : (
            <div className="analysis-empty">Select a category to explore the details.</div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ExpenseAnalysis
