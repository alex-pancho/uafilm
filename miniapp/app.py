import os
import sys
import sqlite3
import random
from flask import Flask, render_template, request, g
try:
    from miniapp.get_m3u import fetch_m3u as fm3u
except ImportError:
    from get_m3u import fetch_m3u as fm3u


app = Flask(__name__)


def base_path():
    # якщо exe
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    # якщо звичайний запуск
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


DB_PATH = os.path.join(base_path(), "database", "films.sqlite")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    db = get_db()

    q = request.args.get("q", "").strip()

    type_src = request.args.get("type", "").strip()

    total = db.execute("SELECT COUNT(*) FROM content").fetchone()[0]

    params = []

    if not q:
        # Generate 200 random IDs from 1 to total
        random_limit = min(200, total)
        random_ids = random.sample(range(1, total + 1), random_limit)
        placeholders = ",".join("?" * len(random_ids))
        sql = f"SELECT * FROM content WHERE _id IN ({placeholders})"
        params = random_ids
    else:
        sql = "SELECT * FROM content WHERE 1=1"
        sql += " AND (title_ua LIKE ? OR title_ua LIKE ?)"
        params.append(f"%{q.lower()}%")
        params.append(f"%{q.title()}%")

    if type_src:
        sql += " AND type_src = ?"
        params.append(type_src)

    sql += " ORDER BY _id DESC LIMIT 200"

    items = db.execute(sql, params).fetchall()
    return render_template(
        "index.html",
        items=items,
        q=q,
        type_src=type_src,
        version=APP_VERSION,
        total=total
    )


@app.route("/item/<int:item_id>")
def detail(item_id):
    db = get_db()
 
    content = db.execute(
        "SELECT * FROM content WHERE _id = ?",
        (item_id,)
    ).fetchone()

    seasons = db.execute(
        "SELECT * FROM season WHERE content_id = ? ORDER BY season_number",
        (item_id,)
    ).fetchall()

    playlists = db.execute("""
        SELECT p.*, s.season_number
        FROM playlist p
        JOIN season s ON s._id = p.season_id
        WHERE p.content_id = ?
        ORDER BY s.season_number
    """, (item_id,)).fetchall()

    # групуємо плейлисти по сезонах
    by_season = {}
    for p in playlists:
        by_season.setdefault(p["season_number"], []).append(p)

    return render_template(
        "detail.html",
        item=content,
        seasons=seasons,
        playlists_by_season=by_season
    )

@app.route("/fetch_m3u/<int:playlist_id>", methods=["POST"])
def fetch_m3u(playlist_id):
    headers = dict(request.headers)
    return fm3u(playlist_id, headers)


APP_VERSION = "0.0.7"
if __name__ == "__main__":
    app.run(debug=True, port=80)
