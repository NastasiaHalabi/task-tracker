# Task Tracker Architecture — Strategy A

Strategy A uses a deliberately small evidence set: the repository guidance and README, the core API/model/storage files, and only the frontend and test sections needed to confirm task creation.

## 1. What it does

Task Tracker is a Kanban-style learning application with a FastAPI backend and a vanilla JavaScript frontend. It supports task CRUD, filtering by status, priority, tag, and overdue state, and moving tasks through workflow statuses. Tasks may include an assignee, due date, and tags. The API also exposes root and health endpoints.

The frontend calls the backend at `http://localhost:8000`. FastAPI provides JSON validation and serialization, while data is kept only in process memory; restarting the server clears all tasks.

## 2. Data model

`app/models.py` defines three Pydantic schemas:

- `TaskCreate`: client-supplied creation fields. `title` is required; description, status, priority, assignee, due date, and tags have defaults or are optional.
- `TaskUpdate`: optional fields for partial `PATCH` requests.
- `TaskResponse`: the API representation, including server-generated `id`, `created_at`, `updated_at`, and computed `is_overdue`.

Status is restricted to `ToDo`, `InProgress`, or `Done`. Priority is restricted to `Low`, `Medium`, or `High`. Titles are trimmed and limited to 200 characters. Tags are trimmed, non-blank, limited to five entries, and limited to 30 characters each.

Tasks are stored as `TaskResponse` objects in `_tasks: dict[str, TaskResponse]`. IDs use `uuid4().hex`; timestamps use timezone-aware UTC datetimes. `is_overdue` is computed rather than stored: a task is overdue when its due date is before today in UTC and its status is not `Done`.

## 3. Request flow when a user creates a task

1. The user submits the task modal in `frontend/index.html`.
2. `buildTaskPayload()` checks that the title is non-blank, converts empty assignee and due-date values to `null`, parses comma-separated tags, and builds JSON.
3. `handleTaskFormSubmit()` sends `POST /tasks` with `Content-Type: application/json`.
4. FastAPI parses the body as `TaskCreate`. Pydantic applies field types, enum checks, extra-field rejection, and title/tag validators. Invalid input returns HTTP 422 before the route runs.
5. `create_task()` in `app/main.py` delegates the validated model to `storage.add_task()`.
6. Storage generates a UUID and UTC timestamps, constructs `TaskResponse`, saves it in `_tasks`, and returns it.
7. FastAPI serializes the response using `TaskResponse` and returns HTTP 201.
8. On success, the frontend closes the modal, refetches `GET /tasks`, and rerenders the board. A 422 response is displayed as field- or form-level validation feedback.

## 4. Key files

- `app/main.py` — FastAPI application, CORS configuration, task routes, and health-router registration.
- `app/models.py` — task enums, request/response schemas, validators, and overdue computation.
- `app/storage.py` — process-local CRUD operations, UUID generation, timestamps, filtering, and test reset.
- `app/business_rules.py` — permitted task-status transitions and 422 errors for invalid transitions.
- `app/routers/health.py` — separately registered health endpoint.
- `frontend/index.html` — complete Kanban UI, modal, API calls, validation messages, drag-and-drop, filtering, and DOM rendering.
- `tests/conftest.py` — shared `TestClient`, task fixture, and automatic storage reset.
- `tests/test_tasks.py` — evidence for CRUD status codes, response defaults, validation, and status transitions.
- `AGENTS.md` — project values, Module 5 boundaries, and review rules.

## 5. Conventions

- Preserve existing API response shapes unless a change is explicitly requested.
- Use Pydantic models as the API boundary and reject unknown request fields.
- Use the exact documented enum values for status and priority.
- Generate identifiers and UTC timestamps on the server.
- Use HTTP 201 for creation, 204 for successful deletion, 404 for missing tasks, and 422 for validation or invalid status transitions.
- Keep storage in memory for Module 5; do not add authentication, a database, or dependencies.
- Keep task routes in `app/main.py`; the health endpoint is the only current separate router.
- Keep the current frontend dependency-free and use `fetch` for API access.
- Test through FastAPI `TestClient` and reset global storage around every test.
