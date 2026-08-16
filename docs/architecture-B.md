# Task Tracker Architecture — Strategy B

## 1. What it does

Task Tracker is a learning-project Kanban application. A vanilla JavaScript board in `frontend/index.html` calls a FastAPI JSON API at `http://localhost:8000`. The board lets users create and edit tasks, filter by tag or overdue state, and drag tasks between status columns. The API supports task creation, listing and filtering, lookup, partial update, and deletion, plus root and health endpoints.

The backend is intentionally process-local: tasks are stored in memory and disappear when the server restarts. There is no authentication or database.

## 2. Data model

`app/models.py` defines the API boundary:

- `TaskCreate` accepts a required `title` plus optional/defaulted `description`, `status`, `priority`, `assignee`, `due_date`, and `tags`.
- `TaskUpdate` makes those fields optional for partial `PATCH` operations.
- `TaskResponse` adds server-owned `id`, `created_at`, and `updated_at`, and exposes computed `is_overdue`.

Status values are exactly `ToDo`, `InProgress`, and `Done`; priority values are `Low`, `Medium`, and `High`. Titles are trimmed, must be non-blank, and are limited to 200 characters. Unknown request fields are rejected. Tags are trimmed, must be non-blank, and are limited to five values of at most 30 characters each.

`app/storage.py` stores `TaskResponse` objects in `_tasks: dict[str, TaskResponse]`. IDs are UUID4 hex strings and timestamps are timezone-aware UTC values. `is_overdue` is derived rather than persisted: it is true when the due date is before the current UTC date and the task is not `Done`.

## 3. Request flow when a user creates a task

1. The user submits the modal in `frontend/index.html`. `buildTaskPayload()` checks for a non-blank title and assembles JSON, converting empty assignee and due-date values to `null` and comma-separated tags to a list.
2. `handleTaskFormSubmit()` sends `POST /tasks` with `Content-Type: application/json`.
3. FastAPI parses the body as `TaskCreate`; Pydantic applies types, defaults, enum constraints, extra-field rejection, and title/tag validators. Invalid input returns HTTP 422 before the endpoint runs.
4. `create_task()` in `app/main.py` passes the validated payload to `storage.add_task()`.
5. Storage generates the ID and UTC timestamps, constructs a `TaskResponse`, saves it in `_tasks`, and returns it. FastAPI serializes the declared response model and sends HTTP 201.
6. On success, the frontend closes the modal, requests `GET /tasks`, and rerenders the board. A 422 response is displayed as field-level or form-level feedback.

## 4. Key files

- `app/main.py` — application construction, CORS, task endpoints, and router registration.
- `app/models.py` — enums, Pydantic request/response schemas, validation, and overdue calculation.
- `app/storage.py` — in-memory CRUD, filtering, identifiers, and timestamps.
- `app/business_rules.py` — allowed status-transition validation.
- `app/core/config.py` — `.env` loading and `PORT`/`APP_ENV` settings.
- `app/routers/health.py` and `app/schemas/health.py` — `/health` behavior and response shape.
- `frontend/index.html` — the self-contained HTML, CSS, JavaScript UI, and API client.
- `tests/` — FastAPI `TestClient` fixtures and coverage for CRUD, transitions, due dates, tags, filtering, and validation.

## 5. Conventions

- Preserve API response shapes and use the exact documented status and priority strings.
- Treat Pydantic models as the validation and serialization boundary; request schemas forbid unknown fields.
- Keep server-generated IDs and timestamps in storage, and keep `is_overdue` computed.
- Permit only `ToDo → InProgress`, `InProgress → Done`, and `Done → InProgress`; same-state updates are invalid.
- Use HTTP 201 for creation, 204 for successful deletion, 404 for missing tasks, and 422 for invalid input or status transitions.
- Keep Module 5 free of authentication, databases, and new dependencies.
- Test through FastAPI `TestClient`; reset the global in-memory store around each test.
