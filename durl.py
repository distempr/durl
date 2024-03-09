import sqlite3

from flask import Flask, abort, redirect, g


app = Flask(__name__)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("durl.db")
    return db


@app.route("/<surl>")
def url(surl):
    cur = get_db().cursor()
    cur.execute("SELECT url FROM url WHERE id = ? AND active = 1", (surl,))
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
