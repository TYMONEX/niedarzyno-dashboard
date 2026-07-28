from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("comments.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        message TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        name = request.form["name"]
        message = request.form["message"]

        if len(name) > 25:
            name = name[:25]

        if len(message) > 300:
            message = message[:300]

        conn = sqlite3.connect("comments.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO comments (name, message, date)
            VALUES (?, ?, ?)
            """,
            (
                name,
                message,
                datetime.now().strftime("%d.%m.%Y %H:%M")
            )
        )

        conn.commit()
        conn.close()

        return redirect("/")

    conn = sqlite3.connect("comments.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name,message,date
        FROM comments
        ORDER BY id DESC
    """)

    comments = cursor.fetchall()

    conn.close()

    return render_template("index.html", comments=comments)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
