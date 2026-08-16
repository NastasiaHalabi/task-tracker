# Task Tracker Architecture

## 1. System Overview

Task Tracker is a learning-project Kanban application with a FastAPI JSON API and
a dependency-free HTML/CSS/JavaScript frontend. Users can create, view, edit,
filter, move, and delete tasks. The API also exposes root and health endpoints.

The frontend in `frontend/index.html` calls the API at `http://localhost:8000`.
The backend stores tasks in a module-level in-memory dictionary, so data is
process-local and is lost when the server restarts. The current architecture has
no authentication or database.

## 2. Components and Responsibilities

- `frontend/index.html` contains the Kanban UI, modal forms, filtering,
  drag-and-drop behavior, API calls, validation feedback, and DOM rendering.
- `app/main.py` creates the FastAPI application, configures CORS, registers the
  health router, and defines the root and task endpoints.
- `app/models.py` defines task enums, Pydantic request and response models,
  validation rules, and overdue calculation.
- `app/storage.py` owns the in-memory collection and implements CRUD, filtering,
  UUID generation, and UTC timestamps.
- `app/business_rules.py` validates allowed workflow transitions.
- `app/core/config.py` loads `.env` values and exposes `PORT` and `APP_ENV`.
- `app/routers/health.py` and `app/schemas/health.py` define the health endpoint
  and its response shape.
- `tests/` uses FastAPI `TestClient` and resets storage around each test.

## 3. Data Model

`TaskCreate` accepts a required `title` and optional or defaulted `description`,
`status`, `priority`, `assignee`, `due_date`, and `tags`. `TaskUpdate` exposes the
same mutable fields as optional values for partial `PATCH` requests.
`TaskResponse` adds server-owned `id`, `created_at`, and `updated_at` fields and
the computed `is_overdue` field.

Status values are exactly `ToDo`, `InProgress`, and `Done`. Priority values are
exactly `Low`, `Medium`, and `High`. Titles are trimmed, must be nonblank, and
may contain at most 200 characters. Unknown create and update fields are
rejected.

Tags are trimmed, must be nonblank, and are limited to five values of at most 30
characters each. Duplicate tags are not explicitly prohibited. A task is
overdue when its due date is earlier than the current UTC date and its status is
not `Done`.

Tasks are stored as `TaskResponse` objects in
`_tasks: dict[str, TaskResponse]`. IDs are UUID4 hexadecimal strings. Creation
uses one timezone-aware UTC timestamp for both `created_at` and `updated_at`;
updates replace `updated_at`.

## 4. API Surface and Behavior

- `GET /` returns the application name and configured environment.
- `GET /health` returns `"ok"` and a current UTC ISO 8601 timestamp.
- `GET /tasks` lists tasks and supports combined `status`, `priority`,
  `overdue`, and case-insensitive exact-tag filters.
- `POST /tasks` creates a task and returns HTTP 201.
- `GET /tasks/{task_id}` retrieves a task or returns HTTP 404.
- `PATCH /tasks/{task_id}` partially updates a task or returns HTTP 404.
- `DELETE /tasks/{task_id}` deletes a task with HTTP 204 or returns HTTP 404.

List results are sorted by `created_at` ascending. Invalid request data and
invalid status transitions return HTTP 422. Allowed transitions are
`ToDo -> InProgress`, `InProgress -> Done`, and `Done -> InProgress`;
same-state and all other transitions are invalid.

CORS allows the local frontend origins on ports 5500 and 5173, the
`127.0.0.1:5500` origin, and the `null` origin used when opening the frontend
directly as a local file.

## 5. Task-Creation Request Flow

1. The user submits the task modal in `frontend/index.html`.
2. `buildTaskPayload()` rejects a blank title, converts empty assignee and due
   date inputs to `null`, parses comma-separated tags, and builds the JSON body.
3. `handleTaskFormSubmit()` sends `POST /tasks` with
   `Content-Type: application/json`.
4. FastAPI binds the body to `TaskCreate`. Pydantic applies types, defaults,
   enum constraints, extra-field rejection, and title and tag validators.
   Invalid input returns HTTP 422 before the route runs.
5. `create_task()` delegates the validated model to `storage.add_task()`.
6. Storage generates the ID and UTC timestamps, constructs a `TaskResponse`,
   copies the tags, saves the task in `_tasks`, and returns it.
7. FastAPI serializes the declared response model, including `is_overdue`, and
   returns HTTP 201.
8. The frontend closes the modal, refetches `GET /tasks`, and rerenders the
   board. Validation failures are displayed in field-level or form-level UI.

## 6. Architectural Conventions and Constraints

- Preserve existing API response shapes unless a change is explicitly requested.
- Keep the exact documented status and priority strings.
- Use Pydantic models as the API validation and serialization boundary.
- Generate identifiers and timezone-aware UTC timestamps on the server.
- Keep `is_overdue` derived rather than persisted.
- Keep storage in memory for Module 5; do not add authentication or a database.
- Keep the frontend dependency-free and use `fetch` for API access.
- Test through FastAPI `TestClient` and isolate tests by resetting global storage.

## Context Strategy Comparison

### Strategy A - Minimal Context
What it got right: It accurately described the end-to-end product, core data
model, frontend creation flow, in-memory storage, and principal API conventions.
What it got wrong or invented: It did not make a clear factual invention, but
its narrow evidence set omitted configuration and health-schema details, exact
status transitions, list ordering, and some filtering behavior.

### Strategy B - Structured Context
What it got right: It provided the strongest balanced account of the frontend,
API, models, storage, business rules, configuration, health endpoint, and tests.
What it got wrong or missed: It omitted the list sort order, combined-filter
semantics, CORS origins, root and health response details, and the fact that
duplicate tags are not explicitly rejected.

### Strategy C - Targeted Context
What it got right: It was the most precise about backend request handling,
storage responsibilities, UUIDs and timestamps, computed overdue state, exact
tag filtering, and sorted list results.
What it got wrong or missed: Its targeted file set excluded repository-visible
frontend, business-rule, configuration, and health details, so it incorrectly
presented those areas as unavailable for a repository-level architecture
description.

### Verdict
I picked Strategy B because it had the best balance of repository coverage,
accuracy, and useful architectural structure, then supplemented it with
Strategy C's backend precision and Strategy A's clear end-to-end request flow.
