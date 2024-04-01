import os
import sqlite3
import threading
import queue
import signal

from datetime import datetime, UTC
from pathlib import Path

from flask import Flask, abort, redirect, g


app = Flask(__name__)
state_home = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
db_path = state_home / "durl" / "durl.db"

stats_queue = queue.Queue()
stop_event = threading.Event()


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(db_path)
        db.execute("PRAGMA journal_mode=WAL")
    return db


def stats():
    db = sqlite3.connect(db_path)
    cur = db.cursor()

    while not stop_event.is_set():
        uid, time = stats_queue.get()
        cur.execute("UPDATE url SET last_hit = ?, hit_count = hit_count + 1 WHERE id = ?", (time, uid))
        db.commit()
        stats_queue.task_done()


stats_thread = threading.Thread(target=stats)
stats_thread.start()


@app.route("/<uid>")
def url(uid):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT url FROM url WHERE id = ? AND archived = 0", (uid,))
    url = cur.fetchone()
    if not url:
        abort(404)

    url = url[0]

    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S")
    stats_queue.put((url, now))

    return redirect(url, code=302)


@app.route("/api/status")
def status():
    db = get_db()
    cur = db.cursor()
    cur.execute("PRAGMA user_version")
    return ("", 204)


@app.teardown_appcontext
def close_connection(exception):
    stats_queue.join()
    stats_thread.join()

    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
