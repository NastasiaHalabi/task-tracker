from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field


MAX_TAGS = 5
MAX_TAG_LENGTH = 30


def utc_today() -> date:
    """Return today's calendar date in UTC.

    Returns:
        date: The current date in UTC.
    """
    return datetime.now(timezone.utc).date()


def compute_is_overdue(due_date: Optional[date], status: "TaskStatus") -> bool:
    """Determine whether a task is overdue.

    Args:
        due_date (Optional[date]): The task's due date, or None if unset.
        status (TaskStatus): The task's current status.

    Returns:
        bool: True if ``due_date`` is in the past and ``status`` is not
            ``TaskStatus.DONE``, False otherwise.
    """
    if due_date is None:
        return False
    if status == TaskStatus.DONE:
        return False
    return due_date < utc_today()


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


def _normalize_tags(tags: list[str]) -> list[str]:
    """Trim tags, reject blanks, enforce max count/length."""
    cleaned: list[str] = []
    for tag in tags:
        trimmed = tag.strip()
        if not trimmed:
            raise ValueError("Tags cannot be blank or whitespace-only")
        if len(trimmed) > MAX_TAG_LENGTH:
            raise ValueError(f"Each tag must be {MAX_TAG_LENGTH} characters or fewer")
        cleaned.append(trimmed)
    if len(cleaned) > MAX_TAGS:
        raise ValueError(f"At most {MAX_TAGS} tags are allowed")
    return cleaned


class TaskCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=False, extra="forbid")

    title: str  # REQUIRED, 1..200 chars after strip
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def _title_not_blank(cls, v: str) -> str:
        v2 = v.strip()
        if not v2:
            raise ValueError("Title is required and cannot be blank")
        if len(v2) > 200:
            raise ValueError("Title must be 200 characters or fewer")
        return v2

    @field_validator("tags")
    @classmethod
    def _tags_valid(cls, v: list[str]) -> list[str]:
        return _normalize_tags(v)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: Optional[list[str]] = None

    @field_validator("title")
    @classmethod
    def _title_not_blank(cls, v):
        if v is None:
            raise ValueError("Title cannot be null")
        v2 = v.strip()
        if not v2:
            raise ValueError("Title is required and cannot be blank")
        if len(v2) > 200:
            raise ValueError("Title must be 200 characters or fewer")
        return v2

    @field_validator("description", "status", "priority")
    @classmethod
    def _non_nullable_fields_cannot_be_null(cls, v, info):
        if v is None:
            raise ValueError(f"{info.field_name} cannot be null")
        return v

    @field_validator("tags")
    @classmethod
    def _tags_valid(cls, v):
        if v is None:
            raise ValueError("Tags cannot be null")
        return _normalize_tags(v)


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def is_overdue(self) -> bool:
        return compute_is_overdue(self.due_date, self.status)
