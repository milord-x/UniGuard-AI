from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .base import connect


def list_groups() -> List[str]:
    con = connect()
    try:
        cur = con.execute(
            """
            SELECT DISTINCT group_name
            FROM students
            ORDER BY group_name ASC
            """
        )
        return [r["group_name"] for r in cur.fetchall()]
    finally:
        con.close()


def heatmap_rows(group_name: str, week: int, limit: int) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Қайтарылады:
      subjects: [subject_id...]
      rows: [{
        student_id, full_name, group_name, risk_score,
        subjects: {subject_id: subj_risk_score}
      }, ...]
    """
    con = connect()
    try:
        # subject list from snapshots
        cur = con.execute(
            """
            SELECT DISTINCT subject_id
            FROM snapshots
            WHERE week = ?
            ORDER BY subject_id ASC
            """,
            (week,),
        )
        subjects = [r["subject_id"] for r in cur.fetchall()]

        # top students in group by overall risk_score (from risk_report snapshots table OR stored snapshot risk_score in dashboard view)
        # We assume dashboard uses computed risk_score per student (stored in snapshots table 'student_snapshot' or derived).
        # In our DB we have 'students' and 'snapshots' per subject.
        # We'll compute student risk as max(subject_risk) for week to sort.
        cur = con.execute(
            """
            WITH subj AS (
              SELECT s.student_id, s.full_name, s.group_name,
                     sp.subject_id,
                     sp.risk_score AS subj_risk
              FROM students s
              JOIN snapshots sp ON sp.student_id = s.student_id
              WHERE s.group_name = ? AND sp.week = ?
            ),
            agg AS (
              SELECT student_id,
                     MAX(subj_risk) AS risk_score
              FROM subj
              GROUP BY student_id
            )
            SELECT s.student_id, s.full_name, s.group_name, a.risk_score
            FROM students s
            JOIN agg a ON a.student_id = s.student_id
            WHERE s.group_name = ?
            ORDER BY a.risk_score DESC
            LIMIT ?
            """,
            (group_name, week, group_name, limit),
        )
        top = [dict(r) for r in cur.fetchall()]

        # now fetch per-subject risks for those students
        ids = [r["student_id"] for r in top]
        if not ids:
            return subjects, []

        placeholders = ",".join(["?"] * len(ids))
        cur = con.execute(
            f"""
            SELECT student_id, subject_id, risk_score
            FROM snapshots
            WHERE week = ? AND student_id IN ({placeholders})
            """,
            (week, *ids),
        )
        subj_map: Dict[str, Dict[str, float]] = {}
        for r in cur.fetchall():
            sid = r["student_id"]
            subj_map.setdefault(sid, {})
            subj_map[sid][r["subject_id"]] = float(r["risk_score"])

        # build rows
        rows: List[Dict[str, Any]] = []
        for r in top:
            sid = r["student_id"]
            per = subj_map.get(sid, {})
            rows.append(
                {
                    "student_id": sid,
                    "full_name": r["full_name"],
                    "group_name": r["group_name"],
                    "risk_score": float(r["risk_score"] or 0.0),
                    "subjects": per,
                }
            )

        return subjects, rows
    finally:
        con.close()