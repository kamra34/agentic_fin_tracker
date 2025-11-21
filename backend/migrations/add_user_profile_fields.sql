-- Migration: Add personal finance profile fields to users table
-- Date: 2025-11-21
-- Description: Adds household, housing, vehicle, and financial goal fields to support enhanced user profiles

-- Add new columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS household_members INTEGER;
ALTER TABLE users ADD COLUMN IF NOT EXISTS num_vehicles INTEGER;
ALTER TABLE users ADD COLUMN IF NOT EXISTS housing_type VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS house_size_sqm INTEGER;
ALTER TABLE users ADD COLUMN IF NOT EXISTS monthly_income_goal FLOAT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS monthly_savings_goal FLOAT;

-- Optional: Add comments to document the columns (PostgreSQL)
COMMENT ON COLUMN users.household_members IS 'Number of people in the household including user';
COMMENT ON COLUMN users.num_vehicles IS 'Total number of vehicles owned or leased';
COMMENT ON COLUMN users.housing_type IS 'Type of housing: own_house, own_apartment, rent_house, rent_apartment, other';
COMMENT ON COLUMN users.house_size_sqm IS 'Living area in square meters';
COMMENT ON COLUMN users.monthly_income_goal IS 'Target monthly income amount in user currency';
COMMENT ON COLUMN users.monthly_savings_goal IS 'Target monthly savings amount in user currency';
