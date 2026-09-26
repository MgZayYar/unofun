"""Health probe (unauthenticated, for load balancers and Docker)."""

from fastapi import APIRouter
from sqlalchemy import text

from app.core import config
from app.db.session import SessionLocal

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    database = "ok"
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception:
        database = "error"
    storage = "ok" if config.UPLOADS_DIR.is_dir() and config.OUTPUTS_DIR.is_dir() else "error"
    status = "ok" if database == "ok" and storage == "ok" else "degraded"
    return {"status": status, "database": database, "storage": storage}
