import os
import sqlite3

from pathlib import Path

from flask import Flask, abort, redirect, g


app = Flask(__name__)
state_home = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
db_path = state_home / "durl" / "durl.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(db_path)
    return db


@app.route("/<uid>")
def url(uid):
    cur = get_db().cursor()
    cur.execute("SELECT url FROM url WHERE id = ? AND active = 1", (uid,))
    url = cur.fetchone() 
    if not url:
        abort(404)

    url = url[0]
    return redirect(url)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
