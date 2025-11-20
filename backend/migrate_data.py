"""
Temporary data migration script - migrate from old DB to new Railway DB
This script will be deleted after migration is complete
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def migrate_data(target_db_url=None):
    """Migrate all data from source DB to target DB"""

    # Get database URLs from environment
    source_db_url = os.getenv("DATABASE_URL")

    # Get target URL from argument or command line
    if not target_db_url:
        if len(sys.argv) > 1:
            target_db_url = sys.argv[1]
        else:
            print("❌ ERROR: Target database URL is required")
            print("Usage: python migrate_data.py <target_database_url>")
            return False

    if not source_db_url:
        print("❌ ERROR: DATABASE_URL not found in .env file")
        return False

    print(f"\n📊 Migration Plan:")
    print(f"   FROM: {source_db_url[:30]}...")
    print(f"   TO:   {target_db_url[:30]}...")
    print("\n⚠️  Starting migration in 3 seconds... (Ctrl+C to cancel)")

    import time
    try:
        time.sleep(3)
    except KeyboardInterrupt:
        print("\n❌ Migration cancelled")
        return False

    try:
        # Create engines
        print("\n🔌 Connecting to databases...")
        source_engine = create_engine(source_db_url)
        target_engine = create_engine(target_db_url)

        # Test connections
        with source_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Connected to source database")

        with target_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Connected to target database")

        # Create sessions
        SourceSession = sessionmaker(bind=source_engine)
        TargetSession = sessionmaker(bind=target_engine)

        source_session = SourceSession()
        target_session = TargetSession()

        # Step 1: Create schema in target database
        print("\n🏗️  Creating schema in target database...")

        # Get all table creation statements from source
        with source_engine.connect() as conn:
            # Get table names
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]

        print(f"   Found {len(tables)} tables: {', '.join(tables)}")

        # Import models to create tables
        print("\n📋 Creating tables using SQLAlchemy models...")
        from app.models.user import User
        from app.models.expense import Expense, ExpenseTemplate
        from app.models.category import Category, Subcategory
        from app.models.account import Account
        from app.models.income import IncomeTemplate, MonthlyIncome
        from app.core.database import Base

        Base.metadata.create_all(bind=target_engine)
        print("✅ Schema created successfully")

        # Step 2: Migrate data table by table
        print("\n📦 Migrating data...")

        # Define migration order (respecting foreign keys)
        migration_order = [
            'users',
            'categories',
            'subcategories',
            'accounts',
            'expenses',
            'expense_templates',
            'recurring_expenses',
            'income_templates',
            'monthly_incomes'
        ]

        total_rows = 0

        for table in migration_order:
            if table not in tables:
                print(f"⚠️  Table '{table}' not found in source database, skipping...")
                continue

            print(f"\n   Migrating table: {table}")

            # Get all data from source
            with source_engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM {table}"))
                rows = result.fetchall()
                columns = result.keys()

            if not rows:
                print(f"      ℹ️  No data in {table}")
                continue

            print(f"      Found {len(rows)} rows")

            # Insert into target
            with target_engine.connect() as conn:
                for row in rows:
                    # Build INSERT statement
                    row_dict = dict(zip(columns, row))

                    # Create placeholders
                    placeholders = ', '.join([f":{col}" for col in columns])
                    columns_str = ', '.join(columns)

                    insert_sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"

                    try:
                        conn.execute(text(insert_sql), row_dict)
                    except Exception as e:
                        print(f"      ⚠️  Error inserting row: {e}")
                        continue

                conn.commit()

            print(f"      ✅ Migrated {len(rows)} rows")
            total_rows += len(rows)

        # Step 3: Fix sequences (for auto-increment IDs)
        print("\n🔧 Fixing sequences...")
        with target_engine.connect() as conn:
            for table in migration_order:
                if table not in tables:
                    continue

                # Get max ID
                try:
                    result = conn.execute(text(f"SELECT MAX(id) FROM {table}"))
                    max_id = result.scalar()

                    if max_id:
                        # Reset sequence
                        sequence_name = f"{table}_id_seq"
                        conn.execute(text(f"SELECT setval('{sequence_name}', {max_id})"))
                        print(f"   ✅ Fixed sequence for {table} (max_id: {max_id})")
                except Exception as e:
                    print(f"   ⚠️  Could not fix sequence for {table}: {e}")

            conn.commit()

        # Step 4: Verify migration
        print("\n🔍 Verifying migration...")
        verification_passed = True

        for table in migration_order:
            if table not in tables:
                continue

            with source_engine.connect() as source_conn, target_engine.connect() as target_conn:
                source_count = source_conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                target_count = target_conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()

                if source_count == target_count:
                    print(f"   ✅ {table}: {target_count} rows")
                else:
                    print(f"   ❌ {table}: SOURCE={source_count}, TARGET={target_count} - MISMATCH!")
                    verification_passed = False

        # Close sessions
        source_session.close()
        target_session.close()

        print("\n" + "="*60)
        if verification_passed:
            print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
            print(f"   Total rows migrated: {total_rows}")
            print("\n🚀 Next steps:")
            print("   1. Update your .env file with the new DATABASE_URL")
            print("   2. Test your application with the new database")
            print("   3. This migration script will be automatically deleted")
        else:
            print("⚠️  MIGRATION COMPLETED WITH WARNINGS")
            print("   Please review the mismatches above")
        print("="*60 + "\n")

        return verification_passed

    except Exception as e:
        print(f"\n❌ ERROR during migration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("  DATABASE MIGRATION TOOL")
    print("  Migrate from Raspberry Pi to Railway PostgreSQL")
    print("="*60 + "\n")

    success = migrate_data()

    if success:
        print("\n✅ Migration successful!")
        sys.exit(0)
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
