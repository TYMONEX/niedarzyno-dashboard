import hmac
import os
from datetime import datetime

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    create_engine,
    delete,
    func,
    insert,
    select,
)
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "zmien-ten-klucz-lokalnie")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///comments.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://", "postgresql+psycopg://", 1
    )
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+psycopg://", 1
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
metadata = MetaData()

comments = Table(
    "comments",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(25), nullable=False),
    Column("message", Text, nullable=False),
    Column("date", String(16), nullable=False),
)

comment_likes = Table(
    "comment_likes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "comment_id",
        Integer,
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("voter_id", String(100), nullable=False),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
    UniqueConstraint("comment_id", "voter_id", name="uq_comment_voter"),
)

metadata.create_all(engine)


def admin_logged_in():
    return session.get("admin_logged_in") is True


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name", "").strip()[:25]
        message = request.form.get("message", "").strip()[:300]

        if name and message:
            with engine.begin() as connection:
                connection.execute(
                    insert(comments).values(
                        name=name,
                        message=message,
                        date=datetime.now().strftime("%d.%m.%Y %H:%M"),
                    )
                )

        return redirect(url_for("home") + "#comments")

    likes_count = func.count(comment_likes.c.id).label("likes")
    query = (
        select(
            comments.c.id,
            comments.c.name,
            comments.c.message,
            comments.c.date,
            likes_count,
        )
        .select_from(
            comments.outerjoin(
                comment_likes,
                comment_likes.c.comment_id == comments.c.id,
            )
        )
        .group_by(
            comments.c.id,
            comments.c.name,
            comments.c.message,
            comments.c.date,
        )
        .order_by(comments.c.id.desc())
    )

    with engine.connect() as connection:
        rows = connection.execute(query).mappings().all()

    return render_template("index.html", comments=rows)


@app.post("/api/comments/<int:comment_id>/like")
def toggle_like(comment_id):
    data = request.get_json(silent=True) or {}
    voter_id = str(data.get("voter_id", "")).strip()

    if not voter_id or len(voter_id) > 100:
        return jsonify({"error": "Nieprawidłowy identyfikator."}), 400

    with engine.begin() as connection:
        comment_exists = connection.execute(
            select(comments.c.id).where(comments.c.id == comment_id)
        ).first()

        if comment_exists is None:
            return jsonify({"error": "Komentarz nie istnieje."}), 404

        existing_like = connection.execute(
            select(comment_likes.c.id).where(
                comment_likes.c.comment_id == comment_id,
                comment_likes.c.voter_id == voter_id,
            )
        ).first()

        if existing_like:
            connection.execute(
                delete(comment_likes).where(
                    comment_likes.c.id == existing_like.id
                )
            )
            liked = False
        else:
            try:
                connection.execute(
                    insert(comment_likes).values(
                        comment_id=comment_id,
                        voter_id=voter_id,
                        created_at=datetime.utcnow(),
                    )
                )
                liked = True
            except IntegrityError:
                liked = True

        total = connection.execute(
            select(func.count(comment_likes.c.id)).where(
                comment_likes.c.comment_id == comment_id
            )
        ).scalar_one()

    return jsonify({"liked": liked, "likes": total})


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST" and not admin_logged_in():
        password = request.form.get("password", "")

        if not ADMIN_PASSWORD:
            flash("Najpierw ustaw ADMIN_PASSWORD w Renderze.", "error")
        elif hmac.compare_digest(password, ADMIN_PASSWORD):
            session.clear()
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        else:
            flash("Nieprawidłowe hasło.", "error")

    if not admin_logged_in():
        return render_template("admin.html", logged_in=False)

    likes_count = func.count(comment_likes.c.id).label("likes")
    query = (
        select(
            comments.c.id,
            comments.c.name,
            comments.c.message,
            comments.c.date,
            likes_count,
        )
        .select_from(
            comments.outerjoin(
                comment_likes,
                comment_likes.c.comment_id == comments.c.id,
            )
        )
        .group_by(
            comments.c.id,
            comments.c.name,
            comments.c.message,
            comments.c.date,
        )
        .order_by(comments.c.id.desc())
    )

    with engine.connect() as connection:
        rows = connection.execute(query).mappings().all()
        total_likes = connection.execute(
            select(func.count(comment_likes.c.id))
        ).scalar_one()

    return render_template(
        "admin.html",
        logged_in=True,
        comments=rows,
        total_likes=total_likes,
    )


@app.post("/admin/delete/<int:comment_id>")
def admin_delete_comment(comment_id):
    if not admin_logged_in():
        return redirect(url_for("admin"))

    with engine.begin() as connection:
        connection.execute(
            delete(comment_likes).where(
                comment_likes.c.comment_id == comment_id
            )
        )
        result = connection.execute(
            delete(comments).where(comments.c.id == comment_id)
        )

    if result.rowcount:
        flash("Komentarz został usunięty.", "success")
    else:
        flash("Komentarz nie istnieje.", "error")

    return redirect(url_for("admin"))


@app.post("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
