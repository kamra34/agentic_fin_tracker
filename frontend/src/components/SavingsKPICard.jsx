import { useCurrency } from '../context/CurrencyContext'
import './SavingsKPICard.css'

const ACCOUNT_TYPE_INFO = {
  investment: { icon: '📈', label: 'Investments', color: '#00b8d4' },
  crypto: { icon: '₿', label: 'Crypto', color: '#f7931a' },
  bank_savings: { icon: '🏦', label: 'Bank Savings', color: '#4caf50' }
}

function SavingsKPICard({ savingsSummary }) {
  const { formatAmount } = useCurrency()

  if (!savingsSummary || savingsSummary.account_count === 0) {
    return (
      <div className="savings-kpi-card">
        <div className="kpi-card-content">
          <div className="kpi-header">
            <div className="kpi-label">SAVINGS & INVESTMENTS</div>
          </div>
          <div className="no-data-message">
            <p>No savings accounts yet</p>
            <span className="no-data-hint">Start tracking your investments and savings</span>
          </div>
        </div>
      </div>
    )
  }

  const {
    total_value,
    total_invested,
    total_profit_loss,
    profit_loss_percentage,
    account_count,
    accounts_by_type
  } = savingsSummary

  const isProfit = total_profit_loss >= 0

  return (
    <div className="savings-kpi-card">
      {/* Main KPI Header */}
      <div className="kpi-header">
        <div className="kpi-label">TOTAL PORTFOLIO VALUE</div>
        <div className="kpi-accounts-count">{account_count} {account_count === 1 ? 'Account' : 'Accounts'}</div>
      </div>

      {/* Main Value */}
      <div className="kpi-main-value">
        {formatAmount(total_value)}
      </div>

      {/* Sub Stats Row */}
      <div className="kpi-sub-stats">
        <div className="sub-stat">
          <span className="sub-stat-value">{formatAmount(total_invested)}</span>
          <span className="sub-stat-label">Total Invested</span>
        </div>
        <div className="sub-stat-divider"></div>
        <div className={`sub-stat ${isProfit ? 'profit' : 'loss'}`}>
          <span className="sub-stat-value">
            {isProfit ? '+' : ''}{formatAmount(total_profit_loss)}
          </span>
          <span className="sub-stat-label">{isProfit ? 'Profit' : 'Loss'}</span>
        </div>
        <div className="sub-stat-divider"></div>
        <div className={`sub-stat ${isProfit ? 'profit' : 'loss'}`}>
          <span className="sub-stat-value">
            {isProfit ? '+' : ''}{profit_loss_percentage}%
          </span>
          <span className="sub-stat-label">Return</span>
        </div>
      </div>

      {/* Account Type Breakdown */}
      {Object.keys(accounts_by_type).length > 0 && (
        <div className="kpi-breakdown">
          <div className="breakdown-title">Portfolio Breakdown</div>
          <div className="breakdown-list">
            {Object.entries(accounts_by_type).map(([type, data]) => {
              const typeInfo = ACCOUNT_TYPE_INFO[type] || { icon: '💼', label: type, color: '#999' }
              const valuePercent = total_value > 0 ? (data.value / total_value * 100) : 0
              const typeProfit = data.profit_loss >= 0

              return (
                <div key={type} className="breakdown-row">
                  <div className="breakdown-info">
                    <span className="breakdown-icon">{typeInfo.icon}</span>
                    <div className="breakdown-details">
                      <span className="breakdown-name">{typeInfo.label}</span>
                      <span className="breakdown-count">{data.count} {data.count === 1 ? 'account' : 'accounts'}</span>
                    </div>
                  </div>
                  <div className="breakdown-amounts">
                    <div className="breakdown-value">
                      <span className="breakdown-amount">{formatAmount(data.value)}</span>
                      <span className="breakdown-percentage">{valuePercent.toFixed(1)}%</span>
                    </div>
                    <div className={`breakdown-pl ${typeProfit ? 'profit' : 'loss'}`}>
                      {typeProfit ? '+' : ''}{formatAmount(data.profit_loss)}
                    </div>
                  </div>
                  <div className="breakdown-bar">
                    <div
                      className="breakdown-bar-fill"
                      style={{
                        width: `${valuePercent}%`,
                        backgroundColor: typeInfo.color
                      }}
                    ></div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Performance Summary */}
      <div className="kpi-performance">
        <div className="performance-metric">
          <span className="performance-label">Invested Capital</span>
          <span className="performance-value">{formatAmount(total_invested)}</span>
        </div>
        <div className="performance-metric">
          <span className="performance-label">Current Value</span>
          <span className="performance-value">{formatAmount(total_value)}</span>
        </div>
        <div className="performance-metric">
          <span className="performance-label">Total Return</span>
          <span className={`performance-value ${isProfit ? 'profit' : 'loss'}`}>
            {isProfit ? '+' : ''}{formatAmount(total_profit_loss)} ({isProfit ? '+' : ''}{profit_loss_percentage}%)
          </span>
        </div>
      </div>
    </div>
  )
}

export default SavingsKPICard
