"""
Script to inspect the expenses table structure from the database.
"""

import sys
import io
import psycopg2
import os
from dotenv import load_dotenv
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection(db_url):
    """Create database connection from URL"""
    return psycopg2.connect(db_url)


def inspect_table_structure(conn, table_name):
    """Inspect table structure and return detailed information"""
    print(f"\n{'='*80}")
    print(f"Table: {table_name}")
    print(f"{'='*80}\n")

    with conn.cursor() as cursor:
        # Get column information
        cursor.execute("""
            SELECT
                column_name,
                data_type,
                character_maximum_length,
                column_default,
                is_nullable,
                udt_name
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))

        columns = cursor.fetchall()

        if not columns:
            print(f"⚠ Table '{table_name}' not found or has no columns")
            return None

        print("Columns:")
        print("-" * 80)
        column_info = []
        for col in columns:
            col_name, data_type, max_length, default, nullable, udt_name = col

            # Format type string
            type_str = data_type
            if max_length:
                type_str += f"({max_length})"

            # Nullable indicator
            null_str = "NULL" if nullable == "YES" else "NOT NULL"

            # Default value
            default_str = f"DEFAULT {default}" if default else ""

            print(f"  • {col_name:20} {type_str:25} {null_str:10} {default_str}")

            column_info.append({
                'name': col_name,
                'data_type': data_type,
                'udt_name': udt_name,
                'max_length': max_length,
                'nullable': nullable == "YES",
                'default': default
            })

        # Get primary key
        print("\nPrimary Key:")
        print("-" * 80)
        cursor.execute("""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass AND i.indisprimary;
        """, (table_name,))

        pk_columns = [row[0] for row in cursor.fetchall()]
        if pk_columns:
            print(f"  • {', '.join(pk_columns)}")
        else:
            print("  • No primary key found")

        # Get foreign keys
        print("\nForeign Keys:")
        print("-" * 80)
        cursor.execute("""
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_name = %s;
        """, (table_name,))

        fk_results = cursor.fetchall()
        if fk_results:
            for fk in fk_results:
                print(f"  • {fk[0]} → {fk[1]}.{fk[2]}")
        else:
            print("  • No foreign keys found")

        # Get indexes
        print("\nIndexes:")
        print("-" * 80)
        cursor.execute("""
            SELECT
                indexname,
                indexdef
            FROM pg_indexes
            WHERE tablename = %s;
        """, (table_name,))

        indexes = cursor.fetchall()
        if indexes:
            for idx in indexes:
                print(f"  • {idx[0]}")
        else:
            print("  • No indexes found")

        # Get sample data
        print("\nSample Data (first 3 rows):")
        print("-" * 80)
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")

        sample_rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]

        if sample_rows:
            for row in sample_rows:
                print(f"\nRow:")
                for col_name, value in zip(col_names, row):
                    print(f"  {col_name:20} = {value}")
        else:
            print("  • No data in table")

        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cursor.fetchone()[0]
        print(f"\nTotal Rows: {row_count}")
        print("=" * 80)

        return {
            'table_name': table_name,
            'columns': column_info,
            'primary_keys': pk_columns,
            'row_count': row_count
        }


def main():
    """Main inspection function"""
    print("=" * 80)
    print("Database Schema Inspector")
    print("=" * 80)
    print(f"\nDatabase: {DATABASE_URL.split('@')[1] if DATABASE_URL else 'Not set'}")

    if not DATABASE_URL:
        print("\n❌ Error: DATABASE_URL not configured in .env file")
        return

    try:
        # Connect to database
        print("\nConnecting to database...")
        conn = get_connection(DATABASE_URL)
        print("✓ Connected successfully\n")

        # Inspect expenses table
        expenses_info = inspect_table_structure(conn, 'expenses')

        # Inspect users table
        users_info = inspect_table_structure(conn, 'users')

        # Close connection
        conn.close()

        # Save schema info to JSON file for reference
        schema_info = {
            'expenses': expenses_info,
            'users': users_info
        }

        with open('schema_info.json', 'w', encoding='utf-8') as f:
            json.dump(schema_info, f, indent=2, default=str)

        print(f"\n✓ Schema information saved to schema_info.json")

    except Exception as e:
        print(f"\n❌ Error during inspection: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
