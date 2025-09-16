import sqlite3

conn = sqlite3.connect("motivator.db")  # Make sure this is your database filename
cur = conn.cursor()

# List all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()
print("Tables in the database:", tables)

# Check columns of 'users' table if it exists
if ('users',) in tables:
    cur.execute("PRAGMA table_info(users);")
    columns = cur.fetchall()
    print("Users table columns:", columns)
else:
    print("Users table does NOT exist ❌")

conn.close()
