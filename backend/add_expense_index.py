"""
Script to add index on expenses table for better performance
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

def add_expense_index():
    """Add index on (user_id, date) for expenses table"""
    print("=" * 60)
    print("Adding index to expenses table")
    print("=" * 60)

    try:
        # Connect to database
        print(f"\nConnecting to database: {DATABASE_URL.split('@')[1]}")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Check if index already exists
        cursor.execute("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename='expenses' AND indexname='idx_expenses_user_date';
        """)

        if cursor.fetchone():
            print("✓ Index already exists")
        else:
            # Add index
            print("Creating index on (user_id, date)...")
            cursor.execute("""
                CREATE INDEX idx_expenses_user_date ON expenses(user_id, date);
            """)

            conn.commit()
            print("✓ Index created successfully")

        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("✓ Index optimization completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_expense_index()
