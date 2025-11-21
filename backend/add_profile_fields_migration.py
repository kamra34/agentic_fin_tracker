"""
Database migration script to add profile fields to users table
Run this script to add new personal finance profile fields
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from app.core.database import engine, SessionLocal


def run_migration():
    """Add new profile fields to users table"""

    print("Starting migration: Adding profile fields to users table...")

    migration_sql = """
    -- Add new columns to users table
    ALTER TABLE users ADD COLUMN IF NOT EXISTS household_members INTEGER;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS num_vehicles INTEGER;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS housing_type VARCHAR(50);
    ALTER TABLE users ADD COLUMN IF NOT EXISTS house_size_sqm INTEGER;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS monthly_income_goal FLOAT;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS monthly_savings_goal FLOAT;
    """

    try:
        with engine.connect() as conn:
            # Execute migration
            conn.execute(text(migration_sql))
            conn.commit()
            print("[SUCCESS] Successfully added profile fields to users table")

            # Verify columns were added
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'users'
                AND column_name IN (
                    'household_members',
                    'num_vehicles',
                    'housing_type',
                    'house_size_sqm',
                    'monthly_income_goal',
                    'monthly_savings_goal'
                )
            """))

            added_columns = [row[0] for row in result]
            print(f"[SUCCESS] Verified columns added: {', '.join(added_columns)}")

    except Exception as e:
        print(f"[ERROR] Migration failed: {str(e)}")
        return False

    print("Migration completed successfully!")
    return True


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
