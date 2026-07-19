# app/schemas/health.py
# Pydantic model that defines the response shape for GET /health

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    timestamp: str