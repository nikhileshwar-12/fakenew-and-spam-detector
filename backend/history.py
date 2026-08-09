"""history.py -- SQLite storage + analytics for TruthGuard."""
import os
import json
import sqlite3
import datetime
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "history.db")


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT, mode TEXT, text_preview TEXT,
                is_fake INTEGER, fake_prob REAL,
                is_spam INTEGER, spam_prob REAL, keywords TEXT
            )
        """)


def record(text, result, mode="auto"):
    try:
        fn = result.get("fake_news") or {}
        sp = result.get("spam") or {}
        kws = list(set((fn.get("keywords") or []) + (sp.get("keywords") or [])))
        with _conn() as c:
            c.execute(
                "INSERT INTO checks (ts, mode, text_preview, is_fake, fake_prob, is_spam, spam_prob, keywords) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (datetime.datetime.now().isoformat(timespec="seconds"), mode, (text or "")[:160],
                 1 if fn.get("is_fake") else 0 if fn else None, fn.get("fake_probability"),
                 1 if sp.get("is_spam") else 0 if sp else None, sp.get("spam_probability"),
                 json.dumps(kws[:8])),
            )
    except Exception:
        pass


def stats():
    with _conn() as c:
        total = c.execute("SELECT COUNT(*) n FROM checks").fetchone()["n"]
        fake = c.execute("SELECT COUNT(*) n FROM checks WHERE is_fake=1").fetchone()["n"]
        spam = c.execute("SELECT COUNT(*) n FROM checks WHERE is_spam=1").fetchone()["n"]
        recent = c.execute("SELECT ts, text_preview, is_fake, fake_prob, is_spam, spam_prob "
                           "FROM checks ORDER BY id DESC LIMIT 15").fetchall()
        kw_rows = c.execute("SELECT keywords FROM checks WHERE keywords IS NOT NULL").fetchall()
    counter = Counter()
    for r in kw_rows:
        try:
            for k in json.loads(r["keywords"]):
                if k and k not in ("_url_", "_num_"):
                    counter[k] += 1
        except Exception:
            pass
    return {"total": total, "fake_count": fake, "spam_count": spam,
            "fake_pct": round(fake / total * 100, 1) if total else 0,
            "spam_pct": round(spam / total * 100, 1) if total else 0,
            "recent": [dict(r) for r in recent], "top_keywords": counter.most_common(12)}