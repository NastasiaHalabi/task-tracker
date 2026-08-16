# app/routers/health.py
# Defines the /health endpoint used to verify the API is running.

from datetime import datetime, timezone
from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, status_code=200)
def get_health() -> HealthResponse:
    """Return service status and the current UTC timestamp.

    Returns:
        HealthResponse: An object with ``status`` (str, always ``"ok"``) and
            ``timestamp`` (str, current UTC time in ISO 8601 format).

    Example:
        GET /health
        -> {"status": "ok", "timestamp": "2026-08-15T12:00:00+00:00"}
    """
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )