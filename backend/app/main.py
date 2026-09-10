
import logging
import os
import time

import redis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from app.api import health

from app.api import (
    analyze,
    auth,
    estimate,
    feedback,
    mvp,
    projects,
    questions,
    report,
    risks,
    scaffold,
    tasks,
    tech_stack,
    themes,
    users,
)
from app.middleware.request_logging import RequestLoggingMiddleware


# ---------------------------------------------------------
# Logging / Observability
# ---------------------------------------------------------

class RequestIdFilter(logging.Filter):
    """
    Adds request_id to log records when it is not available.
    """

    def filter(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


projectscope_logger = logging.getLogger("projectscope.request")
projectscope_logger.setLevel(logging.INFO)
projectscope_logger.propagate = False

if not projectscope_logger.handlers:
    handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    handler.setFormatter(formatter)
    projectscope_logger.addHandler(handler)


root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

for handler in root_logger.handlers:
    handler.addFilter(RequestIdFilter())


# ---------------------------------------------------------
# Application
# ---------------------------------------------------------

app = FastAPI(
    title="ProjectScope AI",
    version="0.1.0",
)

app.add_middleware(RequestLoggingMiddleware)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["X-Request-ID"],
)


# ---------------------------------------------------------
# Security Headers
# ---------------------------------------------------------

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )

    # HSTS should only be enabled when the application is served over HTTPS.
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    return response


# ---------------------------------------------------------
# Redis Rate Limiting
# ---------------------------------------------------------

RATE_LIMIT = 60
RATE_WINDOW = 60

REDIS_URL = os.getenv("REDIS_URL")

_redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
) if REDIS_URL else None


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if os.environ.get("DISABLE_RATE_LIMIT") == "1":
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"

    # Fail open if Redis is unavailable so a Redis outage
    # does not take down the complete API.
    if _redis_client is None:
        return await call_next(request)

    key = f"projectscope:rate_limit:{client_ip}"

    try:
        current_count = _redis_client.incr(key)

        if current_count == 1:
            _redis_client.expire(key, RATE_WINDOW)

        if current_count > RATE_LIMIT:
            retry_after = _redis_client.ttl(key)

            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later."
                },
            )

            if retry_after > 0:
                response.headers["Retry-After"] = str(retry_after)

            return response

    except redis.RedisError:
        projectscope_logger.exception(
            "rate_limit_redis_error | continuing_without_rate_limit"
        )

    return await call_next(request)


# ---------------------------------------------------------
# API Routers
# ---------------------------------------------------------

app.include_router(projects.router, prefix="/api/v1")
app.include_router(analyze.router, prefix="/api/v1")
app.include_router(questions.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(estimate.router, prefix="/api/v1")
app.include_router(tech_stack.router, prefix="/api/v1")
app.include_router(risks.router, prefix="/api/v1")
app.include_router(themes.router, prefix="/api/v1")
app.include_router(scaffold.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")
app.include_router(mvp.router, prefix="/api/v1")
app.include_router(report.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "ProjectScope AI backend is running"
    }

app.include_router(health.router)


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )

