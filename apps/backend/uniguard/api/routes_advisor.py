from __future__ import annotations

from fastapi import APIRouter

from uniguard.services.advisor_service import get_groups_payload, get_heatmap_payload

router = APIRouter(prefix="/api/advisor", tags=["advisor"])


@router.get("/groups")
def groups():
    return get_groups_payload()


@router.get("/heatmap")
def heatmap(group_name: str, week: int = 12, limit: int = 24):
    return get_heatmap_payload(group_name=group_name, week=week, limit=limit)