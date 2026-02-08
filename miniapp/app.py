from pathlib import Path
from flask import Flask, render_template, request, g
import sqlite3

app = Flask(__name__)


DB_PATH = Path(__file__).parent.parent / "database" / "films.sqlite"

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

    sql = "SELECT * FROM content WHERE 1=1"
    params = []

    if q:
        sql += " AND (title_ua LIKE ? OR title_ua LIKE ?)"
        params.append(f"%{q}%")
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
        version=APP_VERSION
    )


@app.route("/item/<int:item_id>")
def detail(item_id):
    db = get_db()
    item = db.execute(
        "SELECT * FROM content WHERE _id = ?",
        (item_id,)
    ).fetchone()

    return render_template(
        "detail.html",
        item=item,
        version=APP_VERSION
    )

APP_VERSION = "0.0.2"
if __name__ == "__main__":
    app.run(debug=True, port=80)
