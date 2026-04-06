import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()


def init_db():
    """Create database tables and initialize default admin user"""

    print("Creating database and tables...")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')

    # Chats table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            type TEXT
        )
    ''')

    # Default admin credentials (from .env or fallback)
    admin_password = os.getenv("ADMIN_PASSWORD", "admin@123")

    # Check if admin already exists
    existing_admin = c.execute(
        "SELECT * FROM users WHERE username = ?",
        ("admin",)
    ).fetchone()

    # Create admin user if not exists
    if not existing_admin:
        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", admin_password, "admin")
        )
        print("Default admin user created.")

    conn.commit()
    conn.close()

    print("Database setup complete.")


if __name__ == "__main__":
    init_db()
