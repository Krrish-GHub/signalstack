import sqlite3
import json
import os
import threading
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "signalstack.db")
_lock = threading.RLock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    research TEXT DEFAULT '{}',
    profile TEXT DEFAULT '{}',
    context_notes TEXT DEFAULT '',
    created TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS interview (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    seq INTEGER NOT NULL,
    area TEXT,
    question TEXT NOT NULL,
    answer TEXT,
    skipped INTEGER DEFAULT 0,
    is_followup INTEGER DEFAULT 0,
    answered_at TEXT
);
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    subject TEXT DEFAULT '',
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    kind TEXT NOT NULL,
    reason TEXT NOT NULL,
    reliability REAL DEFAULT 0.5,
    status TEXT DEFAULT 'suggested',
    health TEXT DEFAULT 'unchecked',
    fail_count INTEGER DEFAULT 0,
    last_checked TEXT,
    last_new_item TEXT,
    last_error TEXT,
    origin TEXT DEFAULT 'discovery',
    created TEXT NOT NULL,
    UNIQUE(company_id, url)
);
CREATE TABLE IF NOT EXISTS snapshots (
    source_id INTEGER PRIMARY KEY,
    content_hash TEXT,
    text TEXT,
    fetched TEXT
);
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    source_id INTEGER,
    category TEXT NOT NULL,
    subject TEXT DEFAULT '',
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    snippet TEXT DEFAULT '',
    published TEXT,
    discovered TEXT NOT NULL,
    dedupe_key TEXT NOT NULL,
    analysis TEXT,
    relevance REAL,
    impact REAL,
    urgency REAL,
    source_reliability REAL,
    evidence_strength REAL,
    novelty REAL,
    score REAL,
    signal_type TEXT,
    verification TEXT DEFAULT 'unverified',
    analyzed INTEGER DEFAULT 0,
    UNIQUE(company_id, dedupe_key)
);
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    kind TEXT NOT NULL,
    trigger TEXT NOT NULL,
    status TEXT NOT NULL,
    started TEXT NOT NULL,
    finished TEXT,
    summary TEXT,
    error TEXT
);
CREATE TABLE IF NOT EXISTS briefs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    title TEXT,
    markdown TEXT NOT NULL,
    meta TEXT DEFAULT '{}',
    created TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    brief_id INTEGER,
    action TEXT NOT NULL,
    reason TEXT,
    owner TEXT,
    priority TEXT,
    status TEXT DEFAULT 'open',
    created TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS settings (
    company_id INTEGER PRIMARY KEY,
    data TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS change_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    note TEXT,
    result TEXT,
    created TEXT NOT NULL
);
"""

DEFAULT_SETTINGS = {
    "briefing_day": "mon",
    "briefing_time": "08:00",
    "timezone": "Asia/Kolkata",
    "monitoring_frequency_hours": 24,
    "source_refresh_days": 7,
    "audit_day_of_month": 1,
    "audit_time": "07:00",
    "lookback_days": 7,
    "scheduler_enabled": True,
}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA foreign_keys=ON")
    return c


def init():
    with _lock:
        c = conn()
        c.executescript(SCHEMA)
        c.commit()
        c.close()


def q(sql, args=(), one=False):
    with _lock:
        c = conn()
        try:
            rows = c.execute(sql, args).fetchall()
        finally:
            c.close()
    rows = [dict(r) for r in rows]
    if one:
        return rows[0] if rows else None
    return rows


def x(sql, args=()):
    with _lock:
        c = conn()
        try:
            cur = c.execute(sql, args)
            c.commit()
            return cur.lastrowid
        finally:
            c.close()


def jload(value, default=None):
    if value is None or value == "":
        return default
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return default


def get_settings(company_id):
    row = q("SELECT data FROM settings WHERE company_id=?", (company_id,), one=True)
    data = dict(DEFAULT_SETTINGS)
    if row:
        data.update(jload(row["data"], {}))
    return data


def save_settings(company_id, data):
    merged = get_settings(company_id)
    merged.update(data)
    x(
        "INSERT INTO settings(company_id,data) VALUES(?,?) "
        "ON CONFLICT(company_id) DO UPDATE SET data=excluded.data",
        (company_id, json.dumps(merged)),
    )
    return merged
