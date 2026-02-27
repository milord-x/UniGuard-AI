from __future__ import annotations

from typing import Any, Dict

from uniguard.services.student_service import get_student
from uniguard.domain.scoring.action_plan import build_action_plan_payload


def get_action_plan(student_id: str) -> Dict[str, Any]:
    # get_student() сенің жүйеңде студент профилін қайтарады:
    # { "student": {...}, "subjects": [...], "risk_score": float, ... }
    profile = get_student(student_id)

    if not isinstance(profile, dict):
        return {"error": "bad_profile_shape"}

    if profile.get("error"):
        return {"error": "not_found"}

    student = profile.get("student") or {}
    subjects = profile.get("subjects") or []
    risk_score = float(profile.get("risk_score", 0.0) or 0.0)

    return build_action_plan_payload(student, subjects, risk_score)