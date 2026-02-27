from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from uniguard.db.base import init_db

from uniguard.api.routes_dashboard import router as dashboard_router
from uniguard.api.routes_students import router as students_router
from uniguard.api.routes_subjects import router as subjects_router
from uniguard.api.routes_chat import router as chat_router
from uniguard.api.routes_advisor import router as advisor_router


def create_app() -> FastAPI:
    init_db()  # если БД уже есть, просто проверит таблицы
    app = FastAPI(title="UniGuard AI", version="0.1")

    app.include_router(dashboard_router)
    app.include_router(students_router)
    app.include_router(subjects_router)
    app.include_router(chat_router)
    
    app.include_router(advisor_router)
    
    # статика (UI)
    app.mount("/", StaticFiles(directory="apps/backend/uniguard/static", html=True), name="static")
    return app


app = create_app()