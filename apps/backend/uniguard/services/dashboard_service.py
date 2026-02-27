from __future__ import annotations

from typing import Any, Dict, List

from uniguard.db.repo_students import list_students
from uniguard.db.base import connect


def dashboard_week12(limit: int = 500, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Возвращает список студентов + агрегированный риск по 6 предметам.
    Берём max risk_score (то есть max Risk50) среди предметов.
    """
    students = list_students(limit=limit, offset=offset)
    if not students:
        return []

    ids = [s["student_id"] for s in students]
    week = students[0]["week_now"]

    # SQLite IN (...) батч
    con = connect()
    try:
        placeholders = ",".join("?" for _ in ids)
        sql = f"""
            SELECT student_id,
                   MAX(risk_score) AS risk_score_max,
                   MAX(risk50) AS risk50_max,
                   MAX(risk70) AS risk70_max
            FROM snapshots
            WHERE week = ? AND student_id IN ({placeholders})
            GROUP BY student_id
        """
        cur = con.execute(sql, (week, *ids))
        agg = {r["student_id"]: dict(r) for r in cur.fetchall()}

        out: List[Dict[str, Any]] = []
        for s in students:
            a = agg.get(s["student_id"])
            out.append({
                **s,
                "risk_score": float(a["risk_score_max"]) if a else 0.0,
                "risk50": float(a["risk50_max"]) if a else 0.0,
                "risk70": float(a["risk70_max"]) if a else 0.0,
            })
        return out
    finally:
        con.close()