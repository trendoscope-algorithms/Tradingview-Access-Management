import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "session.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS session (key TEXT PRIMARY KEY, value TEXT)"
    )
    conn.execute("PRAGMA journal_mode=WAL")
    if os.path.exists(DB_PATH):
        os.chmod(DB_PATH, 0o600)
    return conn


def get_sessionid():
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT value FROM session WHERE key = 'sessionid'"
        ).fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def set_sessionid(sessionid):
    if not sessionid:
        return
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO session(key, value)
            VALUES('sessionid', ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (sessionid,),
        )
        conn.commit()
    finally:
        conn.close()