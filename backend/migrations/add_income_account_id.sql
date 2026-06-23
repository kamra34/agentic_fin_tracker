-- Migration: Add account_id to income tables (account-linked income)
-- Date: 2026-06-23
-- Description: Links monthly income and income templates to a payment Account so per-account /
--   per-owner NET (income - expense) can be computed, mirroring how expenses are attributed.
--   Nullable for backward compat: existing income rows stay NULL and roll up under "Unassigned",
--   exactly like NULL-account expenses already do.
--
-- IMPORTANT: Run this on the Railway production DB BEFORE deploying the new backend — the income
--   models now SELECT account_id on every income query, so the column must exist first.
--
-- Deploy order: (1) run this SQL on Railway, (2) merge to main -> Railway backend deploy, (3) Vercel.

ALTER TABLE monthly_incomes  ADD COLUMN IF NOT EXISTS account_id INTEGER REFERENCES accounts(id);
ALTER TABLE income_templates ADD COLUMN IF NOT EXISTS account_id INTEGER REFERENCES accounts(id);

CREATE INDEX IF NOT EXISTS ix_monthly_incomes_account_id ON monthly_incomes (account_id);

COMMENT ON COLUMN monthly_incomes.account_id  IS 'Account the income lands in; NULL = unassigned (legacy rows). Used for per-account/per-owner net.';
COMMENT ON COLUMN income_templates.account_id IS 'Default account for income generated from this template; copied onto monthly_incomes at generate time.';

-- Existing income rows intentionally left NULL (-> "Unassigned"); assign going forward via the UI.
-- Idempotent (IF NOT EXISTS); reversible by dropping the two columns. No down-migration required.
