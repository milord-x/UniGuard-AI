from __future__ import annotations

from typing import Any, Dict, List

from .base import connect


def timeline_weekly(student_id: str, subject_id: str) -> List[Dict[str, Any]]:
    """
    Агрегируем weekly_earned в недельные суммы:
    earned_sum / max_sum отдельно по блокам RK1/RK2.
    """
    con = connect()
    try:
        cur = con.execute(
            """
            SELECT week, block,
                   SUM(earned_points) AS earned_sum,
                   SUM(max_points)    AS max_sum
            FROM weekly_earned
            WHERE student_id = ? AND subject_id = ?
            GROUP BY week, block
            ORDER BY week ASC, block ASC
            """,
            (student_id, subject_id),
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        con.close()