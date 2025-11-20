"""
Fix expenses table id column to auto-increment
"""
import psycopg2
from app.core.config import settings

def fix_expenses_id():
    """Add sequence to expenses id column"""

    # Parse the database URL
    db_url = settings.DATABASE_URL
    # Format: postgresql://user:password@host:port/database
    parts = db_url.replace('postgresql://', '').split('@')
    user_pass = parts[0].split(':')
    host_port_db = parts[1].split('/')
    host_port = host_port_db[0].split(':')

    user = user_pass[0]
    password = user_pass[1]
    host = host_port[0]
    port = host_port[1]
    database = host_port_db[1]

    print(f"Connecting to database: {database} at {host}:{port}")

    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )

    try:
        cursor = conn.cursor()

        # Check current max id
        cursor.execute("SELECT MAX(id) FROM expenses;")
        max_id = cursor.fetchone()[0]
        if max_id is None:
            max_id = 0
        print(f"Current max expense id: {max_id}")

        # Create sequence if it doesn't exist
        print("Creating sequence for expenses id...")
        cursor.execute("""
            CREATE SEQUENCE IF NOT EXISTS expenses_id_seq
            START WITH %s
            INCREMENT BY 1
            NO MINVALUE
            NO MAXVALUE
            CACHE 1;
        """, (max_id + 1,))

        # Set the sequence as default for id column
        print("Setting sequence as default for id column...")
        cursor.execute("""
            ALTER TABLE expenses
            ALTER COLUMN id SET DEFAULT nextval('expenses_id_seq');
        """)

        # Associate the sequence with the column
        print("Associating sequence with column...")
        cursor.execute("""
            ALTER SEQUENCE expenses_id_seq OWNED BY expenses.id;
        """)

        # If there are existing rows without IDs, update them
        cursor.execute("""
            SELECT COUNT(*) FROM expenses WHERE id IS NULL;
        """)
        null_count = cursor.fetchone()[0]

        if null_count > 0:
            print(f"Found {null_count} expenses with null id, fixing...")
            cursor.execute("""
                UPDATE expenses
                SET id = nextval('expenses_id_seq')
                WHERE id IS NULL;
            """)

        conn.commit()
        print("✓ Successfully fixed expenses id column!")
        print(f"  - Sequence created starting at {max_id + 1}")
        print(f"  - Auto-increment enabled for id column")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_expenses_id()
