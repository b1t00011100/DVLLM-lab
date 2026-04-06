import sqlite3

def init_db():
    print("Creating database and tables...")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # USERS TABLE
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')

    # CHATS TABLE
    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            type TEXT
        )
    ''')

    conn.commit()
    conn.close()

    print("Database setup complete.")


if __name__ == "__main__":
    init_db()