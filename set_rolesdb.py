import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# make admin
c.execute("UPDATE users SET role='admin' WHERE username='admin'")

# make others user
c.execute("UPDATE users SET role='user' WHERE role IS NULL")

conn.commit()
conn.close()

print("Roles updated")