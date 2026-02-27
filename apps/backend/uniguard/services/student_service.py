from __future__ import annotations

from typing import Any, Dict

from uniguard.db.repo_students import get_student
from uniguard.db.repo_scores import list_student_snapshots_week


def student_profile(student_id: str) -> Dict[str, Any]:
    s = get_student(student_id)
    if not s:
        return {"error": "student_not_found"}

    week = int(s["week_now"])
    subjects = list_student_snapshots_week(student_id, week)

    # агрегаты по студенту
    risk_score = max((x["risk_score"] for x in subjects), default=0.0)
    risk50 = max((x["risk50"] for x in subjects), default=0.0)
    risk70 = max((x["risk70"] for x in subjects), default=0.0)

    return {
        "student": s,
        "week": week,
        "risk_score": risk_score,
        "risk50": risk50,
        "risk70": risk70,
        "subjects": subjects,
    }