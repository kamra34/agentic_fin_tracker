-- Migration: Add is_investment flag to savings_accounts
-- Date: 2026-06-23
-- Description: Distinguishes performance-tracked investment accounts from cash savings buffers.
--   When is_investment = 0, the account's value still counts toward Total Portfolio Value,
--   but is EXCLUDED from Total Invested and Total Profit/Loss (so a savings buffer no longer
--   dilutes your real investment return).
--
-- IMPORTANT: Run this against the production (Railway) database BEFORE deploying the new
-- backend code. The SQLAlchemy model now selects this column on every savings query, so the
-- column must exist first or the savings endpoints will error.

-- Add the column. Default 1 so any row not covered by the backfill below is treated as an investment.
ALTER TABLE savings_accounts ADD COLUMN IF NOT EXISTS is_investment INTEGER NOT NULL DEFAULT 1;

-- Backfill existing accounts from their account_type:
--   bank_savings / other -> cash buffer (0)
--   investment / crypto / retirement -> investment (1)
UPDATE savings_accounts SET is_investment = 0 WHERE account_type IN ('bank_savings', 'other');
UPDATE savings_accounts SET is_investment = 1 WHERE account_type IN ('investment', 'crypto', 'retirement');

COMMENT ON COLUMN savings_accounts.is_investment IS '1 = counts toward Total Invested and Total Profit/Loss; 0 = cash buffer (value still counts toward Total Portfolio Value only)';
