"""
Rehash user passwords to bcrypt format
Since we don't know the original passwords, we'll set a default password
"""

import psycopg2
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def rehash_passwords():
    """Rehash all user passwords"""

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

        # Get all users
        cursor.execute("SELECT id, email, hashed_password FROM users;")
        users = cursor.fetchall()

        print(f"\nFound {len(users)} users")
        print("Current password hashes:")
        for user_id, email, old_hash in users:
            print(f"  - {email}: {old_hash[:50]}...")

        # Default password for all users
        default_password = "4444"
        new_hash = pwd_context.hash(default_password)

        print(f"\nRehashing all passwords to: {default_password}")
        print(f"New hash format: {new_hash[:50]}...")

        # Update all users with new hash
        for user_id, email, old_hash in users:
            cursor.execute(
                "UPDATE users SET hashed_password = %s WHERE id = %s;",
                (new_hash, user_id)
            )
            print(f"  Updated: {email}")

        conn.commit()
        print(f"\nSuccessfully rehashed {len(users)} user passwords!")
        print(f"All users can now login with password: {default_password}")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    rehash_passwords()
