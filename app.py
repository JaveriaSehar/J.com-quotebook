import sqlite3
from flask import Flask, render_template, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import random

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Strong secret key
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

DATABASE = "motivator.db"

# --- LOGIN REQUIRED DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# --- SAMPLE QUOTES ---
sample_quotes = [
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("When you want something from all your heart, the universe conspires to help you achieve it.", "Paulo Coelho"),
    ("Work hard for your dreams.", "Jia"),
    ("Success is not final, failure is not fatal: It is the courage to continue that counts.", "Winston Churchill"),
    ("Happiness is not something ready-made. It comes from your own actions.", "Dalai Lama")
]

# --- DATABASE CONNECTION ---
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --- REGISTER ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirmation", "").strip()

        if not username or not password or not confirm:
            flash("All fields are required.")
            return redirect("/register")

        if password != confirm:
            flash("Passwords do not match.")
            return redirect("/register")

        hashed = generate_password_hash(password)
        conn = get_db()
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
            conn.commit()
            print(f"[DEBUG] Registered new user: {username}")
        except sqlite3.IntegrityError as e:
            print(f"[DEBUG] SQLite Error: {e}")
            flash("Username already exists. Please choose a different one.")
            return redirect("/register")
        finally:
            conn.close()

        flash("Registered successfully! Please login.")
        return redirect("/login")
    else:
        return render_template("register.html")

# --- LOGIN ---
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Username and password required.")
            return redirect("/login")

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = username
            flash(f"Welcome, {username}!")
            print(f"[DEBUG] User logged in: {username}")
            return redirect("/")
        else:
            flash("Invalid username or password.")
            print(f"[DEBUG] Failed login attempt: {username}")
            return redirect("/login")
    else:
        return render_template("login.html")

# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect("/login")

# --- MAIN PAGE ---
@app.route("/", methods=["GET"])
@login_required
def index():
    # Choose a random quote from sample_quotes
    quote_text, quote_author = random.choice(sample_quotes)
    quote = {"text": quote_text, "author": quote_author}
    return render_template("index.html", quote=quote)

# --- NEXT QUOTE (AJAX) ---
@app.route("/next_quote")
@login_required
def next_quote():
    quote_text, quote_author = random.choice(sample_quotes)
    return jsonify({"text": quote_text, "author": quote_author})

# --- SHARE QUOTE ---
@app.route("/share", methods=["POST"])
@login_required
def share():
    receiver_username = request.form.get("receiver", "").strip()
    quote_text = request.form.get("quote_text", "").strip()
    quote_author = request.form.get("quote_author", "").strip()
    message = request.form.get("message", "").strip()

    if not receiver_username or not quote_text:
        flash("Receiver and quote are required.")
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()
    # Check if receiver exists
    cur.execute("SELECT id FROM users WHERE username=?", (receiver_username,))
    receiver = cur.fetchone()
    if not receiver:
        conn.close()
        flash(f"User '{receiver_username}' does not exist.")
        return redirect("/")

    # Insert into messages table
    cur.execute(
        "INSERT INTO messages (sender_id, receiver_id, quote_text, quote_author, message) VALUES (?, ?, ?, ?, ?)",
        (session["user_id"], receiver["id"], quote_text, quote_author, message)
    )
    conn.commit()
    conn.close()

    flash(f"Quote shared with {receiver_username} successfully!")
    return redirect("/")

# --- INBOX ---
@app.route("/inbox")
@login_required
def inbox():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.username AS sender, m.quote_text AS quote, m.quote_author AS author, m.message AS extra_message
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.receiver_id = ?
        ORDER BY m.id DESC
    """, (session["user_id"],))
    messages = cur.fetchall()
    conn.close()
    return render_template("inbox.html", messages=messages)

# --- RUN APP ---
if __name__ == "__main__":
    print(f"Database path: {os.path.abspath(DATABASE)}")
    app.run(debug=True)














