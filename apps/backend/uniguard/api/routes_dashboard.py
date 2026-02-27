from __future__ import annotations

from fastapi import APIRouter

from uniguard.services.dashboard_service import dashboard_week12

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard")
def get_dashboard(limit: int = 500, offset: int = 0):
    return {"items": dashboard_week12(limit=limit, offset=offset)}