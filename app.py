import os
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "comments.db"

app = Flask(__name__)


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                message TEXT NOT NULL,
                date TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS comment_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comment_id INTEGER NOT NULL,
                voter_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(comment_id, voter_id),
                FOREIGN KEY(comment_id) REFERENCES comments(id) ON DELETE CASCADE
            )
            """
        )

        connection.commit()


init_db()


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name", "").strip()[:25]
        message = request.form.get("message", "").strip()[:300]

        if name and message:
            with get_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO comments (name, message, date)
                    VALUES (?, ?, ?)
                    """,
                    (name, message, datetime.now().strftime("%d.%m.%Y %H:%M")),
                )
                connection.commit()

        return redirect(url_for("home") + "#comments")

    with get_connection() as connection:
        comments = connection.execute(
            """
            SELECT
                comments.id,
                comments.name,
                comments.message,
                comments.date,
                COUNT(comment_likes.id) AS likes
            FROM comments
            LEFT JOIN comment_likes
                ON comment_likes.comment_id = comments.id
            GROUP BY
                comments.id,
                comments.name,
                comments.message,
                comments.date
            ORDER BY comments.id DESC
            """
        ).fetchall()

    return render_template("index.html", comments=comments)


@app.post("/api/comments/<int:comment_id>/like")
def toggle_like(comment_id):
    data = request.get_json(silent=True) or {}
    voter_id = str(data.get("voter_id", "")).strip()

    if not voter_id or len(voter_id) > 100:
        return jsonify({"error": "Nieprawidłowy identyfikator przeglądarki."}), 400

    with get_connection() as connection:
        comment = connection.execute(
            "SELECT id FROM comments WHERE id = ?",
            (comment_id,),
        ).fetchone()

        if comment is None:
            return jsonify({"error": "Komentarz nie istnieje."}), 404

        existing_like = connection.execute(
            """
            SELECT id
            FROM comment_likes
            WHERE comment_id = ? AND voter_id = ?
            """,
            (comment_id, voter_id),
        ).fetchone()

        if existing_like:
            connection.execute(
                "DELETE FROM comment_likes WHERE id = ?",
                (existing_like["id"],),
            )
            liked = False
        else:
            connection.execute(
                """
                INSERT INTO comment_likes (comment_id, voter_id, created_at)
                VALUES (?, ?, ?)
                """,
                (
                    comment_id,
                    voter_id,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
            liked = True

        connection.commit()

        likes = connection.execute(
            "SELECT COUNT(*) AS total FROM comment_likes WHERE comment_id = ?",
            (comment_id,),
        ).fetchone()["total"]

    return jsonify({"liked": liked, "likes": likes})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
