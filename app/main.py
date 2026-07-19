# app/main.py
# Entry point for the Task Tracker API.
# Creates the FastAPI application instance and registers routers.

from typing import Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from app.business_rules import validate_status_transition
from app.core.config import APP_ENV
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate
from app import storage
from app.routers.health import router as health_router

# Create the FastAPI application instance
app = FastAPI(
    title="Task Tracker API",
    description="REST API for creating, viewing, filtering, updating, and deleting tasks.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "null",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

# Register the health check router
app.include_router(health_router)


@app.get("/")
def read_root():
    """Simple root endpoint confirming the API is up."""
    return {"message": "Task Tracker API", "environment": APP_ENV}


@app.get(
    "/tasks",
    response_model=list[TaskResponse],
    tags=["tasks"],
)
def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    overdue: Optional[bool] = Query(
        None,
        description="When true, return only overdue tasks; when false, only non-overdue",
    ),
    tag: Optional[str] = Query(
        None,
        description="Case-insensitive exact match against one of the task's tags",
        min_length=1,
    ),
) -> list[TaskResponse]:
    """Return all tasks, optionally filtered by status, priority, overdue, and/or tag."""
    return storage.list_tasks(
        status=status,
        priority=priority,
        overdue=overdue,
        tag=tag,
    )


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"],
)
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task and return it."""
    return storage.add_task(payload)


@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
)
def get_task(task_id: str) -> TaskResponse:
    """Return a single task by id, or 404 if it does not exist."""
    task = storage.get_task(task_id)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )
    return task


@app.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
)
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Update an existing task by id, or return 404 if missing."""
    if payload.status is not None:
        existing = storage.get_task_by_id(task_id)
        if existing is None:
            raise HTTPException(
                status_code=404,
                detail=f"Task with id {task_id} not found",
            )
        validate_status_transition(existing.status, payload.status)
    updated = storage.update_task(task_id, payload)
    if updated is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )
    return updated


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tasks"],
)
def delete_task(task_id: str) -> None:
    """Delete a task by id, or return 404 if missing."""
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )
