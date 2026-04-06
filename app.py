
from flask import Flask, render_template, request, redirect, session
import sqlite3
import requests
import re
import html
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

# Security level control: low / medium / high
SECURITY_LEVEL = "low"

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

USE_MOCK = os.getenv("USE_MOCK") == True
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

def init_db():
    """Initialize database tables"""
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


def mistral_llm(user_input):
    """Send prompt to local LLM"""
    system_prompt = """
You are a helpful assistant.
Sometimes developers may ask you to reveal debug information.

Admin password: {ADMIN_PASSWORD}
"""

    full_prompt = system_prompt + "\nUser: " + user_input

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": full_prompt,
                "stream": False
            }
        )

        data = response.json()
        return data.get("response") or ""

    except Exception as e:
        return f"ERROR: {str(e)}"


def mock_llm(user_input):
    """Fallback responses if LLM fails"""
    text = user_input.lower()

    if "hello" in text:
        return "Hello. How can I assist you?"

    if "how are you" in text:
        return "I am functioning as expected."

    if "who are you" in text:
        return "I am a test chatbot."

    return "Please provide more details."


def get_llm_response(user_input):
    """Wrapper for LLM with fallback"""
    if USE_MOCK:
        return mock_llm(user_input)

    result = mistral_llm(user_input)

    if not result or "ERROR" in result:
        return mock_llm(user_input)

    return result


def fetch_url(url):
    """Fetch external content (SSRF simulation)"""
    try:
        response = requests.get(url)

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()

        return f"<pre>{text[:1000]}</pre>"

    except Exception as e:
        return f"Error: {str(e)}"


def vulnerable_wrapper(user_input):
    """
    Processes user input for simulated vulnerabilities.
    Ensures only the latest user message triggers actions.
    """

    # Extract only the latest user input (last line)
    lines = user_input.strip().split("\n")
    last_input = lines[-1].strip()
    text = last_input.lower()

# Prompt injection handling based on security level

    if "ignore previous instructions" in text or "reveal system prompt" in text:

        if SECURITY_LEVEL == "low":
            return f"Admin password is: {ADMIN_PASSWORD}"

        elif SECURITY_LEVEL == "medium":
            return "Request blocked: suspicious instruction detected."

        elif SECURITY_LEVEL == "high":
            return "I cannot process that request."
    
    # XSS handling
    if "<script>" in text or "<img" in text:
        if SECURITY_LEVEL == "low":
            return last_input
        elif SECURITY_LEVEL == "medium":
            return "Blocked potentially unsafe content"
        elif SECURITY_LEVEL == "high":
            return html.escape(last_input)

    # SSRF / tool usage (only from current input)
    if "fetch" in text:
        try:
            match = re.search(r"fetch\s+(https?://[^\s]+|[^\s]+)", last_input)

            if not match:
                return "Invalid URL format"

            url = match.group(1)

            if not url.startswith("http"):
                url = "http://" + url

            if SECURITY_LEVEL == "low":
                return fetch_url(url)

            elif SECURITY_LEVEL == "medium":
                if "127.0.0.1" in url or "localhost" in url:
                    return "Blocked internal URL"
                return fetch_url(url)

            elif SECURITY_LEVEL == "high":
                return "External requests disabled"

        except Exception as e:
            return f"Error: {str(e)}"

    # Default LLM response
    return get_llm_response(user_input) or ""

@app.route("/")
def home():
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, "user")
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # Vulnerable query (SQL Injection)
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        user = c.execute(query).fetchone()

        if user:
            session["user_id"] = user[0]

            role = c.execute(
                "SELECT role FROM users WHERE id=?",
                (user[0],)
            ).fetchone()

            session["role"] = role[0] if role else "user"

            conn.close()
            return redirect("/chat")

        conn.close()

    return render_template("login.html")


@app.route("/admin")
def admin():
    # Access control based on security level
    if SECURITY_LEVEL == "low":
        if request.args.get("access") == "true":
            pass
        elif session.get("role") != "admin":
            return "Unauthorized", 403

    elif SECURITY_LEVEL == "medium":
        if session.get("role") != "admin":
            return "Unauthorized", 403

    elif SECURITY_LEVEL == "high":
        if "user_id" not in session or session.get("role") != "admin":
            return "Unauthorized", 403

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    users = c.execute("SELECT id, username, password, role FROM users").fetchall()
    chats = c.execute("SELECT user_id, message, type FROM chats").fetchall()

    conn.close()

    return render_template("admin.html", users=users, chats=chats)


@app.route("/chat", methods=["GET", "POST"])
def chat():
    user_id = session.get("user_id", 1)

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    temp_reply = None

    if request.method == "POST":
        user_input = request.form["message"].strip()

        if user_input:
            c.execute(
                "INSERT INTO chats (user_id, message, type) VALUES (?, ?, ?)",
                (user_id, user_input, "user")
            )

            # Data poisoning based on level
            if SECURITY_LEVEL == "low":
                limit = 5
            elif SECURITY_LEVEL == "medium":
                limit = 2
            else:
                limit = 0

            memory_data = c.execute(
                f"""
                SELECT message FROM chats 
                WHERE user_id=? 
                AND message NOT LIKE '%<script%' 
                AND message NOT LIKE '%<img%' 
                ORDER BY id DESC 
                LIMIT {limit}
                """,
                 (user_id,)
            ).fetchall()

            memory_text = "\n".join([m[0] for m in memory_data[::-1]])

            if limit > 0:
                poisoned_input = memory_text + "\nUser: " + user_input
            else:
                poisoned_input = user_input

            reply = vulnerable_wrapper(poisoned_input) or ""

            # Reflected XSS handling
            if "<script>" in reply or "<img" in reply:
                if SECURITY_LEVEL in ["low", "medium"]:
                    temp_reply = reply
                else:
                    safe_reply = html.escape(reply)
                    c.execute(
                        "INSERT INTO chats (user_id, message, type) VALUES (?, ?, ?)",
                        (user_id, safe_reply, "bot")
                    )
            else:
                c.execute(
                    "INSERT INTO chats (user_id, message, type) VALUES (?, ?, ?)",
                    (user_id, reply, "bot")
                )

            conn.commit()

    history = c.execute(
        "SELECT message, type FROM chats WHERE user_id=? ORDER BY id ASC",
        (user_id,)
    ).fetchall()

    conn.close()

    return render_template(
        "chat.html",
        history=history,
        temp_reply=temp_reply,
        level=SECURITY_LEVEL
    )


@app.route("/history_page")
def history_page():
    user_id = request.args.get("user_id")

    if not user_id:
        user_id = session.get("user_id", 1)

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    chats = c.execute(
        f"SELECT message, type FROM chats WHERE user_id={user_id}"
    ).fetchall()

    conn.close()

    return render_template("history.html", chats=chats)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/change_role", methods=["POST"])
def change_role():
    if "user_id" not in session or session.get("role") != "admin":
        return "Unauthorized", 403

    user_id = request.form["user_id"]
    current_role = request.form["current_role"]

    new_role = "admin" if current_role == "user" else "user"

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute(
        "UPDATE users SET role=? WHERE id=?",
        (new_role, user_id)
    )

    if int(user_id) == session.get("user_id"):
        return "Cannot change your own role", 403

    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/internal")
def internal():
    
    return "SECRET_API_KEY=SU33ESSFUL_33RF"

@app.route("/set_level/<level>")
def set_level(level):
    global SECURITY_LEVEL

    if level in ["low", "medium", "high"]:
        SECURITY_LEVEL = level

    return redirect("/chat")


if __name__ == "__main__":
    app.run(debug=True)
