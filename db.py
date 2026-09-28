import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "stats.db")

def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT, top TEXT, bottom TEXT, shoes TEXT,
        status TEXT, advice TEXT)""")
    return conn

def log_event(result, advice):
    conn = _conn()
    conn.execute(
        "INSERT INTO events (ts, top, bottom, shoes, status, advice) VALUES (?,?,?,?,?,?)",
        (datetime.now().isoformat(timespec="seconds"),
         result.get("top"), result.get("bottom"), result.get("shoes"),
         result.get("status"), advice))
    conn.commit()
    conn.close()

def get_stats():
    conn = _conn()
    total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    today = conn.execute(
        "SELECT COUNT(*) FROM events WHERE ts LIKE ?",
        (datetime.now().strftime("%Y-%m-%d") + "%",)).fetchone()[0]
    recent = conn.execute(
        "SELECT ts, advice FROM events ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()
    return {"total": total, "today": today, "recent": recent}
