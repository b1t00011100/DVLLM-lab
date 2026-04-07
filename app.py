from flask import Flask, render_template, request, redirect, session
import sqlite3
import requests
import re
import html
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "devkey")

USE_MOCK = os.getenv("USE_MOCK") == "True"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") or "admin@123"


def get_security_level():
    return session.get("level", "low")


def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        type TEXT
    )''')

    conn.commit()
    conn.close()


init_db()


# ---------------- LLM ----------------
def mistral_llm(user_input):
    system_prompt = f"""
You are a helpful assistant.

Admin password: {ADMIN_PASSWORD}
"""

    full_prompt = system_prompt + "\nUser: " + user_input

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": full_prompt, "stream": False}
        )
        return response.json().get("response") or ""
    except:
        return "LLM Error"


def mock_llm(user_input):
    if "hello" in user_input.lower():
        return "Hello. How can I assist you?"
    return "Please provide more details."


def get_llm_response(user_input):
    if USE_MOCK:
        return mock_llm(user_input)
    result = mistral_llm(user_input)
    return result if result else mock_llm(user_input)


# ---------------- SSRF ----------------
def fetch_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return f"<pre>{soup.get_text()[:1000]}</pre>"
    except Exception as e:
        return f"Error: {str(e)}"


# ---------------- WRAPPER ----------------
def vulnerable_wrapper(user_input):
    SECURITY_LEVEL = get_security_level()

    lines = user_input.strip().split("\n")
    last_input = lines[-1].strip()
    text = last_input.lower()

    if "ignore previous instructions" in text:
        if SECURITY_LEVEL == "low":
            return f"Admin password is: {ADMIN_PASSWORD}"
        elif SECURITY_LEVEL == "medium":
            return "Blocked suspicious request."
        else:
            return "Request denied."

    if "<script>" in text or "<img" in text:
        if SECURITY_LEVEL == "low":
            return last_input
        elif SECURITY_LEVEL == "medium":
            return "Blocked unsafe content"
        else:
            return html.escape(last_input)

    if "fetch" in text:
        match = re.search(r"fetch\s+(https?://[^\s]+|[^\s]+)", last_input)
        if not match:
            return "Invalid URL"

        url = match.group(1)
        if not url.startswith("http"):
            url = "http://" + url

        if SECURITY_LEVEL == "low":
            return fetch_url(url)
        elif SECURITY_LEVEL == "medium":
            if "127.0.0.1" in url or "localhost" in url:
                return "Blocked internal URL"
            return fetch_url(url)
        else:
            return "External requests disabled"

    return get_llm_response(user_input)


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return redirect("/login")


# 🔥 FIXED ROLE TOGGLE
@app.route("/change_role", methods=["POST"])
def change_role():
    if session.get("role") != "admin":
        return "Unauthorized"

    user_id = request.form.get("user_id")
    current_role = request.form.get("current_role")

    new_role = "admin" if current_role == "user" else "user"

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("UPDATE users SET role=? WHERE id=?", (new_role, user_id))

    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/admin")
def admin():
    SECURITY_LEVEL = get_security_level()
    role = session.get("role")
    user_id = session.get("user_id")

    if SECURITY_LEVEL == "low":
        if request.args.get("access") != "true" and role != "admin":
            return "Unauthorized"

    elif SECURITY_LEVEL == "medium":
        if role != "admin":
            return "Unauthorized"

    elif SECURITY_LEVEL == "high":
        if not user_id or role != "admin":
            return "Unauthorized"

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    users = c.execute("SELECT id, username, password, role FROM users").fetchall()
    chats = c.execute("SELECT user_id, message, type FROM chats").fetchall()

    conn.close()

    return render_template("admin.html", users=users, chats=chats)


@app.route("/set_level/<level>")
def set_level(level):
    if level in ["low", "medium", "high"]:
        session["level"] = level
    return ("", 204)


@app.route("/history_page")
def history_page():
    SECURITY_LEVEL = get_security_level()

    
    if SECURITY_LEVEL == "low":
        user_id = request.args.get("user_id")

    
    elif SECURITY_LEVEL == "medium":
        user_id = session.get("user_id")

    
    else:
        if not session.get("user_id"):
            return redirect("/login")
        user_id = session.get("user_id")

    if not user_id:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    chats = c.execute(
        "SELECT message, type FROM chats WHERE user_id=?",
        (user_id,)
    ).fetchall()

    conn.close()

    return render_template("history.html", chats=chats)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        existing = c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if existing:
            conn.close()
            return "User already exists"

        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  (username, password, "user"))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    SECURITY_LEVEL = get_security_level()
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        if SECURITY_LEVEL == "low":
            query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            result = c.execute(query).fetchone()
        else:
            result = c.execute("SELECT * FROM users WHERE username=? AND password=?",
                               (username, password)).fetchone()

        conn.close()

        if result:
            session["user_id"] = result[0]
            session["role"] = result[3]
            return redirect("/chat")
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error, level=SECURITY_LEVEL)


@app.route("/chat", methods=["GET", "POST"])
def chat():
    SECURITY_LEVEL = get_security_level()
    user_id = session.get("user_id", 1)

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    temp_reply = None

    if request.method == "POST":
        user_input = request.form["message"].strip()

        if user_input:
            c.execute("INSERT INTO chats VALUES (NULL, ?, ?, ?)", (user_id, user_input, "user"))

            limit = 5 if SECURITY_LEVEL == "low" else 2 if SECURITY_LEVEL == "medium" else 0

            memory_data = c.execute(
                "SELECT message FROM chats WHERE user_id=? ORDER BY id DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()

            memory_text = "\n".join([m[0] for m in memory_data[::-1]])

            poisoned_input = memory_text + "\nUser: " + user_input if limit else user_input

            reply = vulnerable_wrapper(poisoned_input) or ""

            if "<script>" in reply or "<img" in reply:
                if SECURITY_LEVEL in ["low", "medium"]:
                    temp_reply = reply
                else:
                    c.execute("INSERT INTO chats VALUES (NULL, ?, ?, ?)",
                              (user_id, html.escape(reply), "bot"))
            else:
                c.execute("INSERT INTO chats VALUES (NULL, ?, ?, ?)",
                          (user_id, reply, "bot"))

            conn.commit()

    history = c.execute("SELECT message, type FROM chats WHERE user_id=?", (user_id,)).fetchall()
    conn.close()

    return render_template("chat.html", history=history, temp_reply=temp_reply, level=SECURITY_LEVEL)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/internal")
def internal():
    return "SECRET_API_KEY=SU33ESSFUL_33RF"


if __name__ == "__main__":
    app.run(debug=True)
