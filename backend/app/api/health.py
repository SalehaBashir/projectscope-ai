from fastapi import APIRouter
from sqlalchemy import text
from app.database.connection import engine
import time
import logging

logger = logging.getLogger("projectscope.health")

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    db_status = "unknown"
    db_latency_ms = None

    try:
        start = time.perf_counter()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_latency_ms = round((time.perf_counter() - start) * 1000, 2)
        db_status = "healthy"
    except Exception:
        logger.exception("health_check_db_error")
        db_status = "unhealthy"

    overall_status = "ok" if db_status == "healthy" else "degraded"

    return {
        "status": overall_status,
        "database": {
            "status": db_status,
            "latency_ms": db_latency_ms,
        },
    }