import os
import sqlite3
from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for


app = Flask(__name__)

DATABASE = "comments.db"


def get_database():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    with get_database() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                message TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)
        connection.commit()


init_database()


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name", "").strip()[:25]
        message = request.form.get("message", "").strip()[:300]

        if name and message:
            with get_database() as connection:
                connection.execute(
                    """
                    INSERT INTO comments (name, message, date)
                    VALUES (?, ?, ?)
                    """,
                    (
                        name,
                        message,
                        datetime.now().strftime("%d.%m.%Y %H:%M"),
                    ),
                )
                connection.commit()

        return redirect(url_for("home") + "#comments")

    with get_database() as connection:
        comments = connection.execute(
            """
            SELECT name, message, date
            FROM comments
            ORDER BY id DESC
            """
        ).fetchall()

    return render_template("index.html", comments=comments)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
