from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional

from .base import connect


def list_students(limit: int = 500, offset: int = 0) -> List[Dict[str, Any]]:
    con = connect()
    try:
        cur = con.execute(
            "SELECT student_id, full_name, group_name, week_now FROM students ORDER BY student_id LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        con.close()


def get_student(student_id: str) -> Optional[Dict[str, Any]]:
    con = connect()
    try:
        cur = con.execute(
            "SELECT student_id, full_name, group_name, week_now FROM students WHERE student_id = ?",
            (student_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        con.close()