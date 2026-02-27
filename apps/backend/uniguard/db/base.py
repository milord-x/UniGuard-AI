from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[4] / "data" / "uniguard.db"

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS students (
  student_id TEXT PRIMARY KEY,
  full_name TEXT NOT NULL,
  group_name TEXT NOT NULL,
  week_now INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS templates (
  subject_id TEXT PRIMARY KEY,
  subject_name TEXT NOT NULL,
  rk1_max REAL NOT NULL,
  rk2_max REAL NOT NULL,
  raw_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS weekly_earned (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id TEXT NOT NULL,
  subject_id TEXT NOT NULL,
  week INTEGER NOT NULL,
  block TEXT NOT NULL,             -- RK1/RK2
  item_title TEXT NOT NULL,
  max_points REAL NOT NULL,
  earned_points REAL NOT NULL,
  FOREIGN KEY(student_id) REFERENCES students(student_id),
  FOREIGN KEY(subject_id) REFERENCES templates(subject_id)
);

CREATE INDEX IF NOT EXISTS idx_weekly_student ON weekly_earned(student_id);
CREATE INDEX IF NOT EXISTS idx_weekly_subject ON weekly_earned(subject_id);
CREATE INDEX IF NOT EXISTS idx_weekly_week ON weekly_earned(week);

CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id TEXT NOT NULL,
  subject_id TEXT NOT NULL,
  week INTEGER NOT NULL,
  rk1_pred REAL NOT NULL,
  rk2_pred REAL NOT NULL,
  admission_pred REAL NOT NULL,
  exam_pred REAL NOT NULL,
  final_pred REAL NOT NULL,
  risk50 REAL NOT NULL,
  risk70 REAL NOT NULL,
  risk_score REAL NOT NULL,
  reasons_json TEXT NOT NULL,
  required_json TEXT NOT NULL,
  FOREIGN KEY(student_id) REFERENCES students(student_id),
  FOREIGN KEY(subject_id) REFERENCES templates(subject_id)
);

CREATE INDEX IF NOT EXISTS idx_snap_student ON snapshots(student_id);
CREATE INDEX IF NOT EXISTS idx_snap_subject ON snapshots(subject_id);
"""

def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    conn = connect()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()

def reset_db() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()