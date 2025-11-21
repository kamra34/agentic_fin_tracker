"""
Database migration script to create savings tables
Run this script to add savings_accounts and savings_transactions tables
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from app.core.database import engine


def run_migration():
    """Create savings tables"""

    print("Starting migration: Creating savings tables...")

    migration_sql = """
    -- Create savings_accounts table
    CREATE TABLE IF NOT EXISTS savings_accounts (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        name VARCHAR(100) NOT NULL,
        account_type VARCHAR(50) NOT NULL,
        description VARCHAR(255),
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create index on user_id for faster queries
    CREATE INDEX IF NOT EXISTS idx_savings_accounts_user_id ON savings_accounts(user_id);

    -- Create savings_transactions table
    CREATE TABLE IF NOT EXISTS savings_transactions (
        id SERIAL PRIMARY KEY,
        account_id INTEGER NOT NULL REFERENCES savings_accounts(id) ON DELETE CASCADE,
        transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('deposit', 'withdrawal', 'value_update')),
        amount FLOAT NOT NULL CHECK (amount >= 0),
        transaction_date TIMESTAMP NOT NULL,
        notes VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create indexes for faster queries
    CREATE INDEX IF NOT EXISTS idx_savings_transactions_account_id ON savings_transactions(account_id);
    CREATE INDEX IF NOT EXISTS idx_savings_transactions_date ON savings_transactions(transaction_date);
    CREATE INDEX IF NOT EXISTS idx_savings_transactions_type ON savings_transactions(transaction_type);
    """

    try:
        with engine.connect() as conn:
            # Execute migration
            conn.execute(text(migration_sql))
            conn.commit()
            print("[SUCCESS] Successfully created savings tables")

            # Verify tables were created
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('savings_accounts', 'savings_transactions')
                ORDER BY table_name
            """))

            created_tables = [row[0] for row in result]
            print(f"[SUCCESS] Verified tables created: {', '.join(created_tables)}")

    except Exception as e:
        print(f"[ERROR] Migration failed: {str(e)}")
        return False

    print("Migration completed successfully!")
    return True


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
