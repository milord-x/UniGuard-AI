from __future__ import annotations

from fastapi import APIRouter

from uniguard.db.repo_templates import list_subjects

router = APIRouter(prefix="/api", tags=["subjects"])


@router.get("/subjects")
def get_subjects():
    return {"items": list_subjects()}