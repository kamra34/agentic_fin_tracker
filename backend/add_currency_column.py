"""
Script to add currency column to existing users table
"""

import sys
import io
import psycopg2
import os
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def add_currency_column():
    """Add currency column to users table"""
    print("=" * 60)
    print("Adding currency column to users table")
    print("=" * 60)

    try:
        # Connect to database
        print(f"\nConnecting to database: {DATABASE_URL.split('@')[1]}")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Check if column already exists
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='users' AND column_name='currency';
        """)

        if cursor.fetchone():
            print("✓ Currency column already exists")
        else:
            # Add currency column
            print("Adding currency column...")
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN currency VARCHAR(10) DEFAULT 'SEK';
            """)

            # Update existing users to have SEK as default
            cursor.execute("""
                UPDATE users
                SET currency = 'SEK'
                WHERE currency IS NULL;
            """)

            conn.commit()
            print("✓ Currency column added successfully")
            print("✓ All existing users set to SEK currency")

        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("✓ Migration completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_currency_column()
