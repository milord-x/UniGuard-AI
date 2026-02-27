from __future__ import annotations

from fastapi import APIRouter
from uniguard.services.action_plan_service import get_action_plan

from uniguard.services.student_service import student_profile
from uniguard.services.timeline_service import build_timeline


router = APIRouter(prefix="/api", tags=["students"])


@router.get("/student/{student_id}")
def get_student(student_id: str):
    return student_profile(student_id)



@router.get("/student/{student_id}/action_plan")
def student_action_plan(student_id: str):
    return get_action_plan(student_id)

@router.get("/student/{student_id}/timeline")
def get_timeline(student_id: str, subject_id: str):
    return build_timeline(student_id, subject_id)

@router.get("/api/student/{student_id}/action_plan")
def student_action_plan(student_id: str):
    return get_action_plan(student_id)

    