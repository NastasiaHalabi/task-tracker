from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.models import (
    TaskCreate,
    TaskPriority,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
)

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task and store it.

    Args:
        payload (TaskCreate): The task data to create.

    Returns:
        TaskResponse: The newly created and stored task.
    """
    now = datetime.now(timezone.utc)
    task_id = uuid4().hex
    task = TaskResponse(
        id=task_id,
        title=payload.title,
        description="" if payload.description is None else payload.description,
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        due_date=payload.due_date,
        tags=list(payload.tags),
        created_at=now,
        updated_at=now,
    )
    _tasks[task_id] = task
    return task


create_task = add_task


def list_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    overdue: Optional[bool] = None,
    tag: Optional[str] = None,
) -> list[TaskResponse]:
    """Return stored tasks, optionally filtered, sorted by creation time.

    Args:
        status (Optional[TaskStatus]): Filter to tasks with this exact
            status.
        priority (Optional[TaskPriority]): Filter to tasks with this exact
            priority.
        overdue (Optional[bool]): When True, restrict to overdue tasks; when
            False, restrict to non-overdue tasks; when None, no filtering.
        tag (Optional[str]): Case-insensitive exact match against one of the
            task's tags.

    Returns:
        list[TaskResponse]: Matching tasks sorted by ``created_at``
            ascending.
    """
    tasks = list(_tasks.values())
    if status is not None:
        tasks = [t for t in tasks if t.status == status]
    if priority is not None:
        tasks = [t for t in tasks if t.priority == priority]
    if overdue is True:
        tasks = [t for t in tasks if t.is_overdue]
    if overdue is False:
        tasks = [t for t in tasks if not t.is_overdue]
    if tag is not None:
        needle = tag.strip().lower()
        tasks = [
            t for t in tasks if any(existing.lower() == needle for existing in t.tags)
        ]
    return sorted(tasks, key=lambda t: t.created_at)


def get_task(task_id: str) -> Optional[TaskResponse]:
    """Look up a stored task by id.

    Args:
        task_id (str): The id of the task to retrieve.

    Returns:
        Optional[TaskResponse]: The matching task, or None if no task with
            that id exists.
    """
    return _tasks.get(task_id)


get_task_by_id = get_task


def update_task(
    task_id: str,
    payload: TaskUpdate,
) -> Optional[TaskResponse]:
    """Apply a partial update to a stored task.

    Args:
        task_id (str): The id of the task to update.
        payload (TaskUpdate): The fields to update; fields left unset on
            ``payload`` are not changed.

    Returns:
        Optional[TaskResponse]: The updated task, or None if no task with
            that id exists.
    """
    existing = _tasks.get(task_id)
    if existing is None:
        return None
    data = existing.model_dump()
    # is_overdue is computed — never persist it as a stored field
    data.pop("is_overdue", None)
    data.update(payload.model_dump(exclude_unset=True))
    data["updated_at"] = datetime.now(timezone.utc)
    updated = TaskResponse(**data)
    _tasks[task_id] = updated
    return updated


def delete_task(task_id: str) -> bool:
    """Delete a stored task by id.

    Args:
        task_id (str): The id of the task to delete.

    Returns:
        bool: True if a task was deleted, False if no task with that id
            existed.
    """
    if task_id not in _tasks:
        return False
    del _tasks[task_id]
    return True


def _reset() -> None:
    _tasks.clear()
