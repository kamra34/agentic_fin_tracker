"""
Script to add performance indexes to existing database tables.
Run this once to improve query performance on existing databases.
"""
from sqlalchemy import text, inspect
from app.core.database import engine

def check_index_exists(table_name, column_name):
    """Check if an index already exists on a column"""
    inspector = inspect(engine)
    indexes = inspector.get_indexes(table_name)
    for idx in indexes:
        if column_name in idx['column_names']:
            return True
    return False

def add_index_if_not_exists(table_name, column_name, index_name=None):
    """Add an index if it doesn't already exist"""
    if check_index_exists(table_name, column_name):
        print(f"[OK] Index on {table_name}.{column_name} already exists")
        return

    if not index_name:
        index_name = f"ix_{table_name}_{column_name}"

    try:
        with engine.connect() as conn:
            conn.execute(text(f'CREATE INDEX {index_name} ON {table_name} ({column_name})'))
            conn.commit()
        print(f"[CREATED] Index on {table_name}.{column_name}")
    except Exception as e:
        print(f"[ERROR] Failed to create index on {table_name}.{column_name}: {e}")

def main():
    print("Adding performance indexes to database...")
    print()

    # Expenses table indexes
    print("Expenses table:")
    add_index_if_not_exists('expenses', 'date')
    add_index_if_not_exists('expenses', 'user_id')
    add_index_if_not_exists('expenses', 'category_id')
    add_index_if_not_exists('expenses', 'subcategory_id')
    add_index_if_not_exists('expenses', 'account_id')
    add_index_if_not_exists('expenses', 'status')
    print()

    # Categories table indexes
    print("Categories table:")
    add_index_if_not_exists('categories', 'user_id')
    add_index_if_not_exists('categories', 'category_type')
    print()

    # Subcategories table indexes
    print("Subcategories table:")
    add_index_if_not_exists('subcategories', 'category_id')
    print()

    # Accounts table indexes
    print("Accounts table:")
    add_index_if_not_exists('accounts', 'user_id')
    print()

    print("Index creation complete!")
    print()
    print("Note: These indexes will significantly improve query performance,")
    print("especially for filtering by user, date ranges, and category lookups.")

if __name__ == "__main__":
    main()
