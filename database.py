import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from config import DB_PATH


def _ensure_dir():
    folder = os.path.dirname(DB_PATH)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)


@contextmanager
def get_conn():
    _ensure_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                target_lang TEXT DEFAULT 'ru',
                source_lang TEXT DEFAULT 'uz',
                joined_at TEXT,
                is_blocked INTEGER DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                kind TEXT,
                source_text TEXT,
                translated_text TEXT,
                created_at TEXT
            )
            """
        )


def add_user(user_id: int, username: str, full_name: str):
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT user_id FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        if existing is None:
            conn.execute(
                "INSERT INTO users (user_id, username, full_name, joined_at) VALUES (?, ?, ?, ?)",
                (user_id, username, full_name, datetime.utcnow().isoformat()),
            )


def set_user_langs(user_id: int, source_lang: str = None, target_lang: str = None):
    with get_conn() as conn:
        if source_lang:
            conn.execute(
                "UPDATE users SET source_lang = ? WHERE user_id = ?", (source_lang, user_id)
            )
        if target_lang:
            conn.execute(
                "UPDATE users SET target_lang = ? WHERE user_id = ?", (target_lang, user_id)
            )


def get_user(user_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def log_history(user_id: int, kind: str, source_text: str, translated_text: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO history (user_id, kind, source_text, translated_text, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, kind, source_text[:500], translated_text[:500], datetime.utcnow().isoformat()),
        )


def get_stats():
    with get_conn() as conn:
        users_count = conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
        history_count = conn.execute("SELECT COUNT(*) c FROM history").fetchone()["c"]
        by_kind = conn.execute(
            "SELECT kind, COUNT(*) c FROM history GROUP BY kind"
        ).fetchall()
        return {
            "users": users_count,
            "translations": history_count,
            "by_kind": {row["kind"]: row["c"] for row in by_kind},
        }


def get_user_history(user_id: int, limit: int = 10):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]
