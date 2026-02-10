import { useState, useEffect, useMemo } from 'react'
import { useCurrency } from '../context/CurrencyContext'
import './ExpenseKPICard.css'

const MONTHLY_TIME_WINDOWS = [
  { key: 'three_months', label: '3M', fullLabel: '3 Months' },
  { key: 'six_months', label: '6M', fullLabel: '6 Months' },
  { key: 'one_year', label: '1Y', fullLabel: '1 Year' },
  { key: 'three_years', label: '3Y', fullLabel: '3 Years' }
]

const YEARLY_TIME_WINDOWS = [
  { key: 'one_year', label: '1Y', fullLabel: '1 Year' },
  { key: 'three_years', label: '3Y', fullLabel: '3 Years' },
  { key: 'all_time', label: 'All', fullLabel: 'All Time' }
]

const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

const getTrendMax = (analyticsData, trendKey) => {
  if (!analyticsData) return 0

  return Object.values(analyticsData).reduce((maxValue, windowData) => {
    if (!windowData || !Array.isArray(windowData[trendKey])) return maxValue

    for (const item of windowData[trendKey]) {
      if (typeof item?.total === 'number' && item.total > maxValue) {
        maxValue = item.total
      }
    }

    return maxValue
  }, 0)
}

function ExpenseKPICard({ analytics }) {
  const { formatAmount } = useCurrency()
  const [selectedWindow, setSelectedWindow] = useState('three_months')
  const [trendView, setTrendView] = useState('monthly') // 'monthly' or 'yearly'
  const [hoveredBar, setHoveredBar] = useState(null)

  // Get current time windows based on trend view
  const timeWindows = trendView === 'monthly' ? MONTHLY_TIME_WINDOWS : YEARLY_TIME_WINDOWS
  const monthlyTrendMax = useMemo(() => getTrendMax(analytics, 'monthly_trend'), [analytics])
  const yearlyTrendMax = useMemo(() => getTrendMax(analytics, 'yearly_trend'), [analytics])

  // When switching trend view, adjust selected window if needed
  useEffect(() => {
    if (trendView === 'yearly') {
      // If current window is 3M or 6M, switch to 1Y as default for yearly view
      if (selectedWindow === 'three_months' || selectedWindow === 'six_months') {
        setSelectedWindow('one_year')
      }
    }
  }, [trendView, selectedWindow])

  if (!analytics || !analytics[selectedWindow]) {
    return (
      <div className="expense-kpi-card">
        <div className="kpi-card-content">
          <p>Loading analytics...</p>
        </div>
      </div>
    )
  }

  const data = analytics[selectedWindow]
  const growthRate = trendView === 'monthly' ? (data.growth_rate || 0) : (data.yearly_growth_rate || 0)
  const isPositiveGrowth = growthRate >= 0
  const trendData = trendView === 'monthly' ? data.monthly_trend : data.yearly_trend
  const allTimeData = analytics.all_time

  const formatDateRange = () => {
    if (!allTimeData?.first_expense_date || !allTimeData?.last_expense_date) return 'No data'
    const first = new Date(allTimeData.first_expense_date)
    const last = new Date(allTimeData.last_expense_date)
    return `${first.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })} - ${last.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}`
  }

  const formatMonthLabel = (item) => {
    const monthIndex = typeof item?.month === 'number' ? item.month - 1 : -1
    const month = MONTH_LABELS[monthIndex] || item?.month
    const year = typeof item?.year === 'number' ? String(item.year).slice(-2) : ''
    return year ? `${month} '${year}` : `${month}`
  }

  return (
    <div className="expense-kpi-card">
      {/* All-Time Summary Header */}
      {allTimeData && (
        <div className="expense-summary-header">
          <div className="summary-main">
            <div className="summary-label">ALL-TIME EXPENSES</div>
            <div className="summary-value">{formatAmount(allTimeData.total_amount)}</div>
          </div>
          <div className="summary-stats">
            <div className="summary-stat">
              <span className="summary-stat-value">{allTimeData.expense_count.toLocaleString()}</span>
              <span className="summary-stat-label">Transactions</span>
            </div>
            <div className="summary-divider"></div>
            <div className="summary-stat">
              <span className="summary-stat-value">{formatDateRange()}</span>
              <span className="summary-stat-label">Date Range</span>
            </div>
            <div className="summary-divider"></div>
            <div className="summary-stat">
              <span className="summary-stat-value">{formatAmount(allTimeData.avg_monthly)}</span>
              <span className="summary-stat-label">Avg Monthly</span>
            </div>
          </div>
        </div>
      )}

      {/* Time Window Selector */}
      <div className="kpi-time-selector">
        {timeWindows.map((window, index) => (
          <button
            key={`${window.key}-${index}`}
            className={`time-btn ${selectedWindow === window.key ? 'active' : ''}`}
            onClick={() => setSelectedWindow(window.key)}
            title={window.fullLabel}
          >
            {window.label}
          </button>
        ))}
      </div>

      {/* Main KPI Header */}
      <div className="kpi-header">
        <div className="kpi-label">TOTAL EXPENSES</div>
        <div className="kpi-timeframe">{timeWindows.find(w => w.key === selectedWindow)?.fullLabel}</div>
      </div>

      {/* Main Value */}
      <div className="kpi-main-value">
        {formatAmount(data.total_amount)}
      </div>

      {/* Sub Stats Row */}
      <div className="kpi-sub-stats">
        <div className="sub-stat">
          <span className="sub-stat-value">{data.expense_count}</span>
          <span className="sub-stat-label">Transactions</span>
        </div>
        <div className="sub-stat-divider"></div>
        <div className="sub-stat">
          <span className="sub-stat-value">{formatAmount(data.avg_monthly)}</span>
          <span className="sub-stat-label">Avg/Month</span>
        </div>
        <div className="sub-stat-divider"></div>
        <div className={`sub-stat ${isPositiveGrowth ? 'negative' : 'positive'}`}>
          <span className="sub-stat-value">
            {isPositiveGrowth ? '+' : ''}{growthRate}%
          </span>
          <span className="sub-stat-label">{trendView === 'monthly' ? 'MoM' : 'YoY'} Change</span>
        </div>
      </div>

      {/* Mini Trend Chart */}
      {trendData && trendData.length > 0 && (
        <div className="kpi-mini-chart">
          <div className="chart-header">
            <div className="chart-title">Spending Trend</div>
            <div className="chart-toggle">
              <button
                className={`toggle-btn ${trendView === 'monthly' ? 'active' : ''}`}
                onClick={() => setTrendView('monthly')}
              >
                Monthly
              </button>
              <button
                className={`toggle-btn ${trendView === 'yearly' ? 'active' : ''}`}
                onClick={() => setTrendView('yearly')}
              >
                Yearly
              </button>
            </div>
          </div>
          <div className="chart-bars">
            {trendData.map((item, index) => {
              const maxAmount = trendView === 'monthly' ? monthlyTrendMax : yearlyTrendMax
              const heightPercent = maxAmount > 0 ? (item.total / maxAmount) * 100 : 0
              const label = trendView === 'monthly' ? formatMonthLabel(item) : `${item.year}`

              return (
                <div
                  key={index}
                  className="chart-bar-wrapper"
                  onMouseEnter={() => setHoveredBar(index)}
                  onMouseLeave={() => setHoveredBar(null)}
                >
                  <div className="chart-bar" style={{ height: `${heightPercent}%` }}></div>
                  <div className="chart-bar-label">{label}</div>

                  {/* Rich Tooltip */}
                  {hoveredBar === index && (
                    <div className="chart-tooltip">
                      {trendView === 'monthly' ? (
                        <>
                          <div className="tooltip-header">
                            {item.month}/{item.year}
                          </div>
                          <div className="tooltip-amount">{formatAmount(item.total)}</div>
                        </>
                      ) : (
                        <>
                          <div className="tooltip-header">{item.year}</div>
                          <div className="tooltip-amount">{formatAmount(item.total)}</div>
                          {item.months_count && (
                            <div className="tooltip-months">{item.months_count} months reported</div>
                          )}
                          {item.top_categories && item.top_categories.length > 0 && (
                            <div className="tooltip-categories">
                              <div className="tooltip-section-title">Top Categories:</div>
                              {item.top_categories.map((cat, idx) => (
                                <div key={idx} className="tooltip-category">
                                  <span className="tooltip-cat-name">{cat.name}</span>
                                  <span className="tooltip-cat-value">
                                    {formatAmount(cat.total)} ({cat.percentage.toFixed(1)}%)
                                  </span>
                                </div>
                              ))}
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Top Categories */}
      {data.top_categories && data.top_categories.length > 0 && (
        <div className="kpi-top-categories">
          <div className="categories-title">Top Spending Categories</div>
          <div className="categories-list">
            {data.top_categories.slice(0, 5).map((category, index) => (
              <div key={index} className="category-row">
                <div className="category-info">
                  <span className="category-rank">{index + 1}</span>
                  <span className="category-name">{category.name}</span>
                  <span className="category-count">{category.count} items</span>
                </div>
                <div className="category-amount-section">
                  <span className="category-amount">{formatAmount(category.total)}</span>
                  <span className="category-percentage">{category.percentage.toFixed(1)}%</span>
                </div>
                <div className="category-bar">
                  <div
                    className="category-bar-fill"
                    style={{ width: `${category.percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ExpenseKPICard
