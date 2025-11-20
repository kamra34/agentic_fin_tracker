"""
Create expense_templates table
"""

import psycopg2
from app.core.config import settings

def create_expense_template_table():
    """Create expense_templates table"""

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

        print("Creating expense_templates table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expense_templates (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                amount FLOAT NOT NULL,
                category_id INTEGER NOT NULL REFERENCES categories(id),
                subcategory_id INTEGER REFERENCES subcategories(id),
                account_id INTEGER REFERENCES accounts(id),
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_expense_templates_user ON expense_templates(user_id);
            CREATE INDEX IF NOT EXISTS idx_expense_templates_category ON expense_templates(category_id);
            CREATE INDEX IF NOT EXISTS idx_expense_templates_active ON expense_templates(is_active);
        """)

        # Create trigger to update updated_at on expense_templates
        print("Creating trigger for expense_templates.updated_at...")
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_expense_template_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS trigger_update_expense_template_updated_at ON expense_templates;

            CREATE TRIGGER trigger_update_expense_template_updated_at
            BEFORE UPDATE ON expense_templates
            FOR EACH ROW
            EXECUTE FUNCTION update_expense_template_updated_at();
        """)

        conn.commit()
        print("\nTable created successfully!\n")

        # Show summary
        print("="*60)
        print("MIGRATION SUMMARY")
        print("="*60)

        cursor.execute("SELECT COUNT(*) FROM expense_templates;")
        templates_count = cursor.fetchone()[0]

        print(f"Expense templates table created: {templates_count} records")
        print("\nExpense templates migration completed successfully!")
        print("\nYou can now:")
        print("1. Create expense templates (recurring expenses like rent, utilities)")
        print("2. Generate monthly expense entries from templates")
        print("3. Track recurring expenses separately from one-time expenses")

    except Exception as e:
        conn.rollback()
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_expense_template_table()
