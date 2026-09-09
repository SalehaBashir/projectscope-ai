import logging
import sys
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.metrics import (
    HTTP_ERRORS_TOTAL,
    HTTP_REQUEST_DURATION,
    HTTP_REQUESTS_TOTAL,
)


logger = logging.getLogger("projectscope.request")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = (
            request.headers.get("X-Request-ID")
            or str(uuid.uuid4())
        )

        request.state.request_id = request_id

        start_time = time.perf_counter()

        try:
            response = await call_next(request)

            duration_seconds = time.perf_counter() - start_time
            duration_ms = round(duration_seconds * 1000, 2)

            status_code = response.status_code
            method = request.method
            path = request.url.path
            status = str(status_code)

            # Prometheus metrics
            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                path=path,
                status=status,
            ).inc()

            HTTP_REQUEST_DURATION.labels(
                method=method,
                path=path,
            ).observe(duration_seconds)

            if status_code >= 400:
                HTTP_ERRORS_TOTAL.labels(
                    method=method,
                    path=path,
                    status=status,
                ).inc()

            log_message = (
                f"request_completed | "
                f"request_id={request_id} | "
                f"method={method} | "
                f"path={path} | "
                f"status_code={status_code} | "
                f"duration_ms={duration_ms}"
            )

            if status_code >= 500:
                logger.error(log_message)
            elif status_code >= 400:
                logger.warning(log_message)
            else:
                logger.info(log_message)

            response.headers["X-Request-ID"] = request_id

            return response

        except Exception:
            duration_seconds = time.perf_counter() - start_time
            duration_ms = round(duration_seconds * 1000, 2)

            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                path=request.url.path,
                status="500",
            ).inc()

            HTTP_REQUEST_DURATION.labels(
                method=request.method,
                path=request.url.path,
            ).observe(duration_seconds)

            HTTP_ERRORS_TOTAL.labels(
                method=request.method,
                path=request.url.path,
                status="500",
            ).inc()

            logger.exception(
                f"request_failed | "
                f"request_id={request_id} | "
                f"method={request.method} | "
                f"path={request.url.path} | "
                f"duration_ms={duration_ms}"
            )

            raise