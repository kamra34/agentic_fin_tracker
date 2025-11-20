"""
Script to migrate ALL tables from old database to new database.
"""

import sys
import io
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

OLD_DB_URL = os.getenv("OLD_DATABASE_URL")
NEW_DB_URL = os.getenv("DATABASE_URL")


def get_connection(db_url):
    """Create database connection from URL"""
    return psycopg2.connect(db_url)


def get_all_tables(conn):
    """Get all tables from database"""
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        return [row[0] for row in cursor.fetchall()]


def copy_table_structure_and_data(table_name, old_conn, new_conn):
    """Copy table structure and data from old to new database"""
    print(f"\n{'='*60}")
    print(f"Migrating table: {table_name}")
    print('='*60)

    with old_conn.cursor() as old_cursor:
        # Get table structure
        old_cursor.execute("""
            SELECT column_name, data_type, character_maximum_length,
                   column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))

        columns = old_cursor.fetchall()

        if not columns:
            print(f"Warning: '{table_name}' table has no columns")
            return

        # Get primary key
        old_cursor.execute("""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass AND i.indisprimary;
        """, (table_name,))

        primary_keys = [row[0] for row in old_cursor.fetchall()]

        # Get foreign keys
        old_cursor.execute("""
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = %s;
        """, (table_name,))

        foreign_keys = old_cursor.fetchall()

    # Create table in new database
    with new_conn.cursor() as new_cursor:
        # Drop table if exists
        new_cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")

        # Build CREATE TABLE statement
        col_definitions = []
        serial_columns = []

        for col in columns:
            col_name, data_type, max_length, default, nullable = col

            # Check if this is an auto-increment column (SERIAL)
            if default and 'nextval' in default:
                # Use SERIAL instead of integer with sequence
                col_def = f"{col_name} SERIAL"
                serial_columns.append(col_name)
            else:
                col_def = f"{col_name} {data_type}"

                if max_length:
                    col_def += f"({max_length})"

                if nullable == 'NO':
                    col_def += " NOT NULL"

                # Handle other defaults
                if default and default != 'NULL' and 'nextval' not in default:
                    col_def += f" DEFAULT {default}"

            col_definitions.append(col_def)

        # Add primary key if exists
        if primary_keys:
            pk_constraint = f"PRIMARY KEY ({', '.join(primary_keys)})"
            col_definitions.append(pk_constraint)

        # Add foreign keys
        for fk in foreign_keys:
            col_name, foreign_table, foreign_col = fk
            fk_constraint = f"FOREIGN KEY ({col_name}) REFERENCES {foreign_table}({foreign_col})"
            col_definitions.append(fk_constraint)

        create_table = f"CREATE TABLE {table_name} ({', '.join(col_definitions)});"
        print(f"\nCreating table structure...")
        print(f"SQL: {create_table[:200]}...")
        new_cursor.execute(create_table)
        new_conn.commit()

    print(f"Table structure created")

    # Copy data
    print(f"Copying data...")

    with old_conn.cursor(cursor_factory=RealDictCursor) as old_cursor:
        old_cursor.execute(f"SELECT * FROM {table_name};")
        rows = old_cursor.fetchall()

        if rows:
            # Get column names from first row
            column_names = list(rows[0].keys())

            with new_conn.cursor() as new_cursor:
                # Build INSERT statement
                placeholders = ', '.join(['%s'] * len(column_names))
                insert_query = f"""
                    INSERT INTO {table_name} ({', '.join(column_names)})
                    VALUES ({placeholders});
                """

                # Insert all rows
                for i, row in enumerate(rows):
                    values = [row[col] for col in column_names]
                    try:
                        new_cursor.execute(insert_query, values)
                    except Exception as e:
                        print(f"Error inserting row {i+1}: {e}")
                        print(f"Row data: {row}")
                        raise

                new_conn.commit()

            print(f"Copied {len(rows)} records")
        else:
            print("No data to copy")


def main():
    """Main migration function"""
    print("="*60)
    print("COMPLETE DATABASE MIGRATION")
    print("="*60)
    print(f"\nOld Database: {OLD_DB_URL.split('@')[1] if OLD_DB_URL else 'Not set'}")
    print(f"New Database: {NEW_DB_URL.split('@')[1] if NEW_DB_URL else 'Not set'}")
    print()

    if not OLD_DB_URL or not NEW_DB_URL:
        print("Error: Database URLs not configured in .env file")
        return

    try:
        # Connect to databases
        print("Connecting to databases...")
        old_conn = get_connection(OLD_DB_URL)
        new_conn = get_connection(NEW_DB_URL)
        print("Connected to both databases\n")

        # Get all tables from old database
        tables = get_all_tables(old_conn)
        print(f"Found {len(tables)} tables in old database:")
        for table in tables:
            print(f"  - {table}")

        if not tables:
            print("\nNo tables found in old database!")
            return

        print(f"\nStarting migration of {len(tables)} tables...")

        # Migrate each table
        for table in tables:
            try:
                copy_table_structure_and_data(table, old_conn, new_conn)
            except Exception as e:
                print(f"\nError migrating table {table}: {e}")
                import traceback
                traceback.print_exc()
                print(f"Continuing with next table...")

        # Close connections
        old_conn.close()
        new_conn.close()

        print("\n" + "="*60)
        print("MIGRATION COMPLETED!")
        print("="*60)

    except Exception as e:
        print(f"\nError during migration: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
