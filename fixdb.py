

import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("DELETE FROM chats WHERE user_id = 2")

conn.commit()
conn.close()

print("Chats cleared")