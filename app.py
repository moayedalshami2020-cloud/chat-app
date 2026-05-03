from flask import Flask, render_template, request, redirect, session
import sqlite3, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

users = {
    "moayed": "1234",
    "sondos": "5678",
    "zainab": "9012",
    "mutahar": "4321"
}

def init_db():
    conn = sqlite3.connect("chat.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            message TEXT,
            time TEXT,
            file TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u in users and users[u] == p:
            session["user"] = u
            return redirect("/chat")

    return render_template("login.html")

@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("chat.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM messages ORDER BY id ASC")
    messages = cur.fetchall()
    conn.close()

    return render_template("chat.html", messages=messages, user=session["user"])

@app.route("/send", methods=["POST"])
def send():
    if "user" not in session:
        return redirect("/")

    msg = request.form.get("message")
    file = request.files.get("file")

    filename = None

    if file and file.filename != "":
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    time = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = sqlite3.connect("chat.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (username, message, time, file) VALUES (?, ?, ?, ?)",
        (session["user"], msg, time, filename)
    )
    conn.commit()
    conn.close()

    return redirect("/chat")

@app.route("/messages")
def messages():
    conn = sqlite3.connect("chat.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM messages ORDER BY id ASC")
    messages = cur.fetchall()
    conn.close()

    return render_template("messages.html", messages=messages, user=session.get("user"))

app.run(debug=True, host="0.0.0.0")