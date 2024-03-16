import os
import sqlite3

from datetime import datetime, UTC
from pathlib import Path

from flask import Flask, abort, redirect, g


app = Flask(__name__)
state_home = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
db_path = state_home / "durl" / "durl.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(db_path)
        db.execute("PRAGMA journal_mode=WAL")
    return db


@app.route("/<uid>")
def url(uid):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT url FROM url WHERE id = ? AND archived = 0", (uid,))
    url = cur.fetchone()
    if not url:
        abort(404)

    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S")
    cur.execute("UPDATE url SET last_hit = ?, hit_count = hit_count + 1 WHERE id = ?", (now, uid))
    db.commit()

    url = url[0]
    return redirect(url, code=302)


@app.route("/api/status")
def status():
    db = get_db()
    cur = db.cursor()
    cur.execute("PRAGMA user_version")
    return ("", 204)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
