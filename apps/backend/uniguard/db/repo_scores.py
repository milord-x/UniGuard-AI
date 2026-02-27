from __future__ import annotations

import json
from typing import Any, Dict, List

from .base import connect


def list_student_snapshots_week(student_id: str, week: int) -> List[Dict[str, Any]]:
    con = connect()
    try:
        cur = con.execute(
            """SELECT subject_id, week, rk1_pred, rk2_pred, admission_pred, exam_pred, final_pred,
                      risk50, risk70, risk_score, reasons_json, required_json
               FROM snapshots
               WHERE student_id = ? AND week = ?
               ORDER BY subject_id""",
            (student_id, week),
        )
        out: List[Dict[str, Any]] = []
        for r in cur.fetchall():
            d = dict(r)
            d["reasons"] = json.loads(d.pop("reasons_json"))
            d["required"] = json.loads(d.pop("required_json"))
            out.append(d)
        return out
    finally:
        con.close()


def list_weekly_earned(student_id: str, subject_id: str) -> List[Dict[str, Any]]:
    con = connect()
    try:
        cur = con.execute(
            """SELECT week, block, item_title, max_points, earned_points
               FROM weekly_earned
               WHERE student_id = ? AND subject_id = ?
               ORDER BY week ASC, block ASC, item_title ASC""",
            (student_id, subject_id),
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        con.close()