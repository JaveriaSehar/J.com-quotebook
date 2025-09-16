import sqlite3

DATABASE = "motivator.db"

conn = sqlite3.connect(DATABASE)
cur = conn.cursor()

# --- USERS TABLE ---
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# --- QUOTES TABLE ---
cur.execute("""
CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    author TEXT NOT NULL
)
""")

# --- MESSAGES TABLE ---
cur.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    quote_text TEXT NOT NULL,
    quote_author TEXT NOT NULL,
    message TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(sender_id) REFERENCES users(id),
    FOREIGN KEY(receiver_id) REFERENCES users(id)
)
""")

# --- SAMPLE QUOTES ---
sample_quotes = [
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("When you want something from all your heart, the universe conspires to help you achieve it.", "Paulo Coelho"),
    ("Work Hard for your Dreams.", "Jia"),
    ("Success is not final, failure is not fatal: It is the courage to continue that counts.", "Winston Churchill"),
    ("Happiness is not something ready-made. It comes from your own actions.", "Dalai Lama")
]

# Insert sample quotes only if quotes table is empty
cur.execute("SELECT COUNT(*) FROM quotes")
if cur.fetchone()[0] == 0:
    cur.executemany("INSERT INTO quotes (text, author) VALUES (?, ?)", sample_quotes)

conn.commit()
conn.close()

print(f"Database '{DATABASE}' created successfully with tables: users, quotes, messages")

