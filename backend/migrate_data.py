"""
Script to migrate data from old database to new database.
This script will:
1. Copy the expenses table structure and data from old db to new db
2. Create a users table
3. Insert initial user
"""

import sys
import io
import psycopg2
from psycopg2.extras import RealDictCursor
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

OLD_DB_URL = os.getenv("OLD_DATABASE_URL")
NEW_DB_URL = os.getenv("DATABASE_URL")

# Password hashing context - must match the one in backend/app/core/security.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_connection(db_url):
    """Create database connection from URL"""
    return psycopg2.connect(db_url)


def create_users_table(new_conn):
    """Create users table in new database"""
    print("Creating users table...")

    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        hashed_password VARCHAR(255) NOT NULL,
        full_name VARCHAR(255) NOT NULL,
        currency VARCHAR(10) DEFAULT 'SEK',
        is_active BOOLEAN DEFAULT TRUE,
        is_superuser BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    """

    with new_conn.cursor() as cursor:
        cursor.execute(create_table_query)
        new_conn.commit()

    print("✓ Users table created successfully")


def insert_initial_user(new_conn):
    """Insert initial user into users table"""
    print("Inserting initial user...")

    email = "kr.nosrati@gmail.com"
    password = "4444"
    full_name = "Kamiar Radnosrati"

    # Hash the password using passlib (same as authentication service)
    hashed_password = pwd_context.hash(password)

    insert_query = """
    INSERT INTO users (email, hashed_password, full_name, is_active, is_superuser)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (email) DO UPDATE
    SET hashed_password = EXCLUDED.hashed_password,
        full_name = EXCLUDED.full_name,
        updated_at = CURRENT_TIMESTAMP
    RETURNING id;
    """

    with new_conn.cursor() as cursor:
        cursor.execute(insert_query, (email, hashed_password, full_name, True, True))
        user_id = cursor.fetchone()[0]
        new_conn.commit()

    print(f"✓ User created successfully with ID: {user_id}")
    print(f"  Email: {email}")
    print(f"  Name: {full_name}")


def copy_expenses_table(old_conn, new_conn):
    """Copy expenses table from old database to new database"""
    print("Copying expenses table structure...")

    with old_conn.cursor() as old_cursor:
        # Get table structure
        old_cursor.execute("""
            SELECT column_name, data_type, character_maximum_length,
                   column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'expenses'
            ORDER BY ordinal_position;
        """)

        columns = old_cursor.fetchall()

        if not columns:
            print("⚠ Warning: 'expenses' table not found in old database")
            return

        # Get primary key and constraints
        old_cursor.execute("""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = 'expenses'::regclass AND i.indisprimary;
        """)

        primary_keys = [row[0] for row in old_cursor.fetchall()]

    # Create table in new database
    with new_conn.cursor() as new_cursor:
        # Drop table if exists
        new_cursor.execute("DROP TABLE IF EXISTS expenses CASCADE;")

        # Build CREATE TABLE statement
        col_definitions = []
        for col in columns:
            col_name, data_type, max_length, default, nullable = col

            col_def = f"{col_name} {data_type}"

            if max_length:
                col_def += f"({max_length})"

            if nullable == 'NO':
                col_def += " NOT NULL"

            if default and 'nextval' not in default:
                col_def += f" DEFAULT {default}"

            col_definitions.append(col_def)

        # Add primary key if exists
        if primary_keys:
            pk_constraint = f"PRIMARY KEY ({', '.join(primary_keys)})"
            col_definitions.append(pk_constraint)

        create_table = f"CREATE TABLE expenses ({', '.join(col_definitions)});"
        new_cursor.execute(create_table)
        new_conn.commit()

    print("✓ Expenses table structure created")

    # Copy data
    print("Copying expenses data...")

    with old_conn.cursor(cursor_factory=RealDictCursor) as old_cursor:
        old_cursor.execute("SELECT * FROM expenses;")
        rows = old_cursor.fetchall()

        if rows:
            # Get column names from first row
            column_names = list(rows[0].keys())

            with new_conn.cursor() as new_cursor:
                # Build INSERT statement
                placeholders = ', '.join(['%s'] * len(column_names))
                insert_query = f"""
                    INSERT INTO expenses ({', '.join(column_names)})
                    VALUES ({placeholders});
                """

                # Insert all rows
                for row in rows:
                    values = [row[col] for col in column_names]
                    new_cursor.execute(insert_query, values)

                new_conn.commit()

            print(f"✓ Copied {len(rows)} records from expenses table")
        else:
            print("⚠ No data found in expenses table")


def main():
    """Main migration function"""
    print("=" * 60)
    print("Database Migration Script")
    print("=" * 60)
    print(f"\nOld Database: {OLD_DB_URL.split('@')[1] if OLD_DB_URL else 'Not set'}")
    print(f"New Database: {NEW_DB_URL.split('@')[1] if NEW_DB_URL else 'Not set'}")
    print()

    if not OLD_DB_URL or not NEW_DB_URL:
        print("❌ Error: Database URLs not configured in .env file")
        return

    try:
        # Connect to databases
        print("Connecting to databases...")
        old_conn = get_connection(OLD_DB_URL)
        new_conn = get_connection(NEW_DB_URL)
        print("✓ Connected to both databases\n")

        # Perform migrations
        create_users_table(new_conn)
        print()

        insert_initial_user(new_conn)
        print()

        copy_expenses_table(old_conn, new_conn)
        print()

        # Close connections
        old_conn.close()
        new_conn.close()

        print("=" * 60)
        print("✓ Migration completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
