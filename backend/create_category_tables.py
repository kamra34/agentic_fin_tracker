"""
Create categories and subcategories tables, then migrate existing data
"""

import psycopg2
from app.core.config import settings
from collections import defaultdict

def create_tables():
    """Create categories and subcategories tables"""

    db_url = settings.DATABASE_URL
    parts = db_url.replace('postgresql://', '').split('@')
    user_pass = parts[0].split(':')
    host_port_db = parts[1].split('/')
    host_port = host_port_db[0].split(':')

    user = user_pass[0]
    password = user_pass[1]
    host = host_port[0]
    port = host_port[1]
    database = host_port_db[1]

    print(f"Connecting to database: {database} at {host}:{port}\n")

    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )

    try:
        cursor = conn.cursor()

        print("Creating categories table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                user_id INTEGER NOT NULL REFERENCES users(id),
                is_active BOOLEAN DEFAULT TRUE,
                UNIQUE(name, user_id)
            );
            CREATE INDEX IF NOT EXISTS idx_categories_user ON categories(user_id);
        """)

        print("Creating subcategories table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subcategories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
                is_active BOOLEAN DEFAULT TRUE,
                UNIQUE(name, category_id)
            );
            CREATE INDEX IF NOT EXISTS idx_subcategories_category ON subcategories(category_id);
        """)

        print("Adding new columns to expenses table...")
        # Add new columns for foreign keys (keep old columns for now)
        cursor.execute("""
            ALTER TABLE expenses
            ADD COLUMN IF NOT EXISTS category_id INTEGER REFERENCES categories(id),
            ADD COLUMN IF NOT EXISTS subcategory_id INTEGER REFERENCES subcategories(id);
        """)

        conn.commit()
        print("\nTables created successfully!\n")

        # Now migrate data
        print("="*60)
        print("MIGRATING EXISTING DATA")
        print("="*60)

        # Get all unique categories and their variations
        cursor.execute("""
            SELECT
                category,
                user_id,
                COUNT(*) as usage_count
            FROM expenses
            WHERE category IS NOT NULL
            GROUP BY category, user_id
            ORDER BY user_id, category;
        """)

        category_data = cursor.fetchall()

        # Group by user and normalized category name
        user_categories = defaultdict(lambda: defaultdict(list))
        for cat_name, user_id, count in category_data:
            normalized = cat_name.lower().strip()
            user_categories[user_id][normalized].append((cat_name, count))

        # Show potential duplicates
        print("\nPotential duplicate categories found:")
        print("-" * 60)

        category_mapping = {}  # Maps (user_id, old_name) -> new_category_id

        for user_id in user_categories:
            print(f"\nUser ID: {user_id}")
            for normalized, variations in user_categories[user_id].items():
                if len(variations) > 1:
                    print(f"  '{normalized}' has {len(variations)} variations:")
                    for var_name, count in variations:
                        print(f"    - '{var_name}' ({count} expenses)")

                    # Use the most common variation as the canonical name
                    canonical_name = max(variations, key=lambda x: x[1])[0]
                else:
                    canonical_name = variations[0][0]

                # Insert into categories table
                cursor.execute("""
                    INSERT INTO categories (name, user_id, is_active)
                    VALUES (%s, %s, TRUE)
                    ON CONFLICT (name, user_id) DO UPDATE SET name = EXCLUDED.name
                    RETURNING id;
                """, (canonical_name, user_id))

                category_id = cursor.fetchone()[0]

                # Map all variations to this category_id
                for var_name, _ in variations:
                    category_mapping[(user_id, var_name)] = category_id

        print(f"\n Created {len(category_mapping)} category mappings")

        # Migrate subcategories
        print("\nMigrating subcategories...")
        cursor.execute("""
            SELECT
                category,
                subcategory,
                user_id,
                COUNT(*) as usage_count
            FROM expenses
            WHERE subcategory IS NOT NULL AND subcategory != ''
            GROUP BY category, subcategory, user_id
            ORDER BY user_id, category, subcategory;
        """)

        subcategory_data = cursor.fetchall()
        subcategory_mapping = {}  # Maps (user_id, category, old_subcat) -> new_subcategory_id

        for cat_name, subcat_name, user_id, count in subcategory_data:
            category_id = category_mapping.get((user_id, cat_name))
            if not category_id:
                continue

            cursor.execute("""
                INSERT INTO subcategories (name, category_id, is_active)
                VALUES (%s, %s, TRUE)
                ON CONFLICT (name, category_id) DO UPDATE SET name = EXCLUDED.name
                RETURNING id;
            """, (subcat_name, category_id))

            subcategory_id = cursor.fetchone()[0]
            subcategory_mapping[(user_id, cat_name, subcat_name)] = subcategory_id

        print(f"Created {len(subcategory_mapping)} subcategory mappings")

        # Update expenses with new foreign keys
        print("\nUpdating expenses with category IDs...")
        cursor.execute("SELECT id, category, subcategory, user_id FROM expenses;")
        expenses = cursor.fetchall()

        updated_count = 0
        for exp_id, cat_name, subcat_name, user_id in expenses:
            category_id = category_mapping.get((user_id, cat_name))
            subcategory_id = None

            if subcat_name:
                subcategory_id = subcategory_mapping.get((user_id, cat_name, subcat_name))

            if category_id:
                cursor.execute("""
                    UPDATE expenses
                    SET category_id = %s, subcategory_id = %s
                    WHERE id = %s;
                """, (category_id, subcategory_id, exp_id))
                updated_count += 1

        print(f"Updated {updated_count} expenses with category/subcategory IDs")

        conn.commit()

        # Show summary
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)

        cursor.execute("SELECT COUNT(*) FROM categories;")
        cat_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM subcategories;")
        subcat_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM expenses WHERE category_id IS NOT NULL;")
        exp_count = cursor.fetchone()[0]

        print(f"Total categories created: {cat_count}")
        print(f"Total subcategories created: {subcat_count}")
        print(f"Total expenses linked: {exp_count}")
        print("\nMigration completed successfully!")
        print("\nNOTE: Old 'category' and 'subcategory' text columns are still in expenses")
        print("      table for reference. You can drop them once you verify everything works.")

    except Exception as e:
        conn.rollback()
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_tables()
