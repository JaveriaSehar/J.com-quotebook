import sqlite3

conn = sqlite3.connect("motivator.db")
cur = conn.cursor()
cur.execute("SELECT id, username, password FROM users")
users = cur.fetchall()
conn.close()

print(users)
