# Task Tracker Architecture — Strategy C

## 1. What it does

The system is a FastAPI REST API for creating, listing, retrieving, partially updating, and deleting tasks. Task listings can be filtered by status, priority, overdue state, and an exact case-insensitive tag match. The API also exposes a root endpoint and registers a health router. CORS is configured for selected local frontend origins and the `null` origin.

Tasks are held in process memory. Persistence across process restarts, deployment topology, frontend behavior, authentication, and database integration are **not visible from the files I read**.

## 2. Data model

- `TaskStatus`: `ToDo`, `InProgress`, or `Done`.
- `TaskPriority`: `Low`, `Medium`, or `High`.
- `TaskCreate`: requires a nonblank title of at most 200 trimmed characters; defaults description to `""`, status to `ToDo`, priority to `Medium`, and tags to an empty list. Assignee and due date are optional.
- `TaskUpdate`: allows partial updates to the same mutable fields and rejects unknown fields.
- `TaskResponse`: adds a string ID plus UTC `created_at` and `updated_at` timestamps. It computes `is_overdue` rather than storing it: a task is overdue when its due date is before the current UTC date and its status is not `Done`.

Tags are trimmed, may not be blank, are limited to five items, and may contain at most 30 characters each. Duplicate-tag behavior is not restricted in the files I read.

## 3. Request flow when a user creates a task

1. A client sends `POST /tasks` with a JSON body.
2. FastAPI binds the body to `TaskCreate`; Pydantic applies defaults, rejects extra fields, and runs title and tag validation.
3. `create_task` delegates the validated payload to `storage.add_task`.
4. Storage generates a UUID4 hexadecimal ID and one timezone-aware UTC timestamp for both `created_at` and `updated_at`.
5. Storage constructs a `TaskResponse`, converts a `null` description to `""`, copies the tag list, saves the task in the module-level `_tasks` dictionary keyed by ID, and returns it.
6. FastAPI returns the response using `TaskResponse` with HTTP `201 Created`; `is_overdue` is included as a computed field.

Behavior implemented by middleware, imported configuration, or framework internals beyond these calls is **not visible from the files I read**.

## 4. Key files

- `app/main.py`: creates and configures the FastAPI application, registers the health router, and defines the root and task endpoints.
- `app/models.py`: defines task enums, request and response schemas, validation, tag constraints, and overdue calculation.
- `app/storage.py`: implements the in-memory task collection and CRUD/filtering operations.

The implementations of `app.business_rules`, `app.core.config`, and `app.routers.health`, although imported by `app/main.py`, are **not visible from the files I read**.

## 5. Conventions

- API task payloads and responses use Pydantic models; unknown create/update fields are forbidden.
- Status and priority values use fixed string enums.
- Generated timestamps and overdue date comparisons use UTC.
- Missing task reads, updates, and deletes produce HTTP 404 responses in the API layer.
- List results are sorted by `created_at` ascending; filters are combined.
- Storage returns `None` or `False` for missing records, while `app/main.py` translates those results to HTTP errors.
- `is_overdue` is derived and explicitly excluded from persisted update data.
- IDs are UUID4 values represented as 32-character hexadecimal strings.
