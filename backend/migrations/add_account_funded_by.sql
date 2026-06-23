-- Migration: Add funded_by_account_id to accounts (per-account funding source)
-- Date: 2026-06-23
-- Description: Lets a payment account declare which OTHER account funds it. In the Monthly
--   per-person budget-left view, a funded account's income+expenses count toward the OWNER
--   of its funding account instead of its own owner (e.g. a SHARED account topped up from
--   Kamiar's salary counts against Kamiar's budget). Nullable; NULL = counts under own owner.
--
-- IMPORTANT: Run on the Railway production DB BEFORE deploying the new backend — the Account
--   model now SELECTs funded_by_account_id on every account query, so the column must exist.

ALTER TABLE accounts ADD COLUMN IF NOT EXISTS funded_by_account_id INTEGER REFERENCES accounts(id);

COMMENT ON COLUMN accounts.funded_by_account_id IS 'Account that funds this one; its owner is used for per-person budget-left. NULL = use own owner.';

-- Idempotent (IF NOT EXISTS); existing rows untouched (NULL). Reversible by dropping the column.
