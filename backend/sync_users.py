"""
Sync users from old structure to new structure
Old: id, email, name, password
New: id, email, hashed_password, full_name, currency, is_active, is_superuser, created_at, updated_at
"""

import psycopg2
from app.core.config import settings

def sync_users():
    """Sync users table to new structure"""

    # Parse the database URL
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

        # Check current users table structure
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)

        columns = [row[0] for row in cursor.fetchall()]
        print(f"Current users table columns: {columns}")

        # Check if we need to migrate
        if 'hashed_password' not in columns:
            print("\nNeed to update users table structure...")

            # Backup old users data
            cursor.execute("SELECT id, email, name, password FROM users;")
            old_users = cursor.fetchall()
            print(f"Found {len(old_users)} users to migrate")

            # Drop and recreate users table
            print("Dropping old users table...")
            cursor.execute("DROP TABLE IF EXISTS users CASCADE;")

            print("Creating new users table structure...")
            cursor.execute("""
                CREATE TABLE users (
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
                CREATE INDEX idx_users_email ON users(email);
            """)

            # Insert users back with new structure
            print("Migrating users to new structure...")
            for old_user in old_users:
                old_id, email, name, password = old_user
                cursor.execute("""
                    INSERT INTO users (id, email, hashed_password, full_name, is_active, is_superuser)
                    VALUES (%s, %s, %s, %s, TRUE, %s);
                """, (old_id, email, password, name, old_id == 1))  # Make first user superuser

            # Update sequence
            cursor.execute("SELECT MAX(id) FROM users;")
            max_id = cursor.fetchone()[0]
            if max_id:
                cursor.execute(f"ALTER SEQUENCE users_id_seq RESTART WITH {max_id + 1};")

            conn.commit()
            print(f"Successfully migrated {len(old_users)} users!")
        else:
            print("\nUsers table already has correct structure")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    sync_users()
