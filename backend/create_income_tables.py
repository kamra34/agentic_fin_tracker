"""
Create income_templates and monthly_incomes tables
"""

import psycopg2
from app.core.config import settings

def create_income_tables():
    """Create income_templates and monthly_incomes tables"""

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

        print("Creating income_templates table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS income_templates (
                id SERIAL PRIMARY KEY,
                source_name VARCHAR(100) NOT NULL,
                current_amount FLOAT NOT NULL,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source_name, user_id)
            );
            CREATE INDEX IF NOT EXISTS idx_income_templates_user ON income_templates(user_id);
            CREATE INDEX IF NOT EXISTS idx_income_templates_active ON income_templates(is_active);
        """)

        print("Creating monthly_incomes table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monthly_incomes (
                id SERIAL PRIMARY KEY,
                month VARCHAR(7) NOT NULL,
                template_id INTEGER REFERENCES income_templates(id) ON DELETE SET NULL,
                source_name VARCHAR(100) NOT NULL,
                amount FLOAT NOT NULL,
                is_one_time BOOLEAN DEFAULT FALSE,
                description VARCHAR(255),
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT valid_month_format CHECK (month ~ '^[0-9]{4}-[0-9]{2}$')
            );
            CREATE INDEX IF NOT EXISTS idx_monthly_incomes_user ON monthly_incomes(user_id);
            CREATE INDEX IF NOT EXISTS idx_monthly_incomes_month ON monthly_incomes(month);
            CREATE INDEX IF NOT EXISTS idx_monthly_incomes_template ON monthly_incomes(template_id);
        """)

        # Create trigger to update updated_at on income_templates
        print("Creating trigger for income_templates.updated_at...")
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_income_template_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS trigger_update_income_template_updated_at ON income_templates;

            CREATE TRIGGER trigger_update_income_template_updated_at
            BEFORE UPDATE ON income_templates
            FOR EACH ROW
            EXECUTE FUNCTION update_income_template_updated_at();
        """)

        conn.commit()
        print("\nTables created successfully!\n")

        # Show summary
        print("="*60)
        print("MIGRATION SUMMARY")
        print("="*60)

        cursor.execute("SELECT COUNT(*) FROM income_templates;")
        templates_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM monthly_incomes;")
        monthly_count = cursor.fetchone()[0]

        print(f"Income templates table created: {templates_count} records")
        print(f"Monthly incomes table created: {monthly_count} records")
        print("\nIncome tables migration completed successfully!")
        print("\nYou can now:")
        print("1. Create income templates (recurring sources like salaries)")
        print("2. Generate monthly income entries from templates")
        print("3. Add one-time income entries (bonuses, etc.)")

    except Exception as e:
        conn.rollback()
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_income_tables()
