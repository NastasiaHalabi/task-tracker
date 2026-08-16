# Comments Feature Plan

This plan is grounded in the current repository:

- Pydantic request and response models are defined in `app/models.py`.
- Task routes are defined directly in `app/main.py`; only health checks currently use a separate router.
- `app/storage.py` stores Pydantic response models in process-local dictionaries and generates UUIDs and UTC timestamps on the server.
- Tests use `TestClient`, reset storage before and after each test, and assert API status codes and response bodies.
- `frontend/index.html` contains the complete frontend, including task modals, fetch helpers, validation rendering, and task-card construction.
- `AGENTS.md` requires preserving existing response shapes and prohibits authentication, databases, dependencies, and `app/` edits during Module 5 planning.

## 1. Data Model

Add two Pydantic models to `app/models.py` during a later implementation phase:

- `CommentCreate`
  - `author: str`
  - `body: str`
  - `model_config = ConfigDict(extra="forbid")`
- `CommentResponse`
  - `id: str`
  - `task_id: str`
  - `author: str`
  - `body: str`
  - `created_at: datetime`

`CommentCreate` follows the existing `TaskCreate` request-model pattern: clients can supply only editable fields, unknown fields are rejected, and server-owned fields are absent from the request model. `CommentResponse` follows `TaskResponse` by containing the complete serialized resource, including its server-generated identifier and timestamp.

Validation should follow the existing title validator in `TaskCreate`:

- Trim `author`, reject blank or whitespace-only values, and enforce 1–100 characters after trimming.
- Reject blank or whitespace-only `body` values and enforce 1–2000 characters after the chosen normalization rule.
- Return normalized strings from validators so the stored response matches the validated representation.
- Reject attempts to submit `id`, `task_id`, or `created_at` because `extra="forbid"` keeps those fields server-owned.

Do not add comments to `TaskResponse`. Keeping comments behind separate nested routes preserves the existing task response shape required by `AGENTS.md` and prevents every task-list response from growing with comment history.

No `CommentUpdate` model is proposed because editing comments is not part of the requested feature.

## 2. API Routes

Add the minimal nested routes during implementation:

- `POST /tasks/{task_id}/comments`
  - Request body: `CommentCreate`
  - Response model: `CommentResponse`
  - Status: `201 Created`
  - Return `404` with the existing task-not-found detail when `task_id` does not exist.
- `GET /tasks/{task_id}/comments`
  - Response model: `list[CommentResponse]`
  - Status: `200 OK`
  - Return `[]` for an existing task with no comments.
  - Return `404` when the parent task does not exist.
  - Return comments in deterministic `created_at` ascending order unless an open question below changes that decision.

Place these routes in `app/main.py` beside the existing task routes. That follows the current repository pattern, where all task-related endpoints are defined in `main.py`, and avoids an unrelated router refactor. A future route reorganization could move tasks and comments together, but it is not required for this feature.

Both routes should verify the parent with `storage.get_task(task_id)`, following the existing `GET`, `PATCH`, and `DELETE /tasks/{task_id}` pattern and its `404` response wording. The create route then delegates to storage in the same way `POST /tasks` delegates to `storage.add_task`.

No comment-level `GET`, `PATCH`, or `DELETE` route is proposed because those operations were not requested.

## 3. Tests

Add a focused `tests/test_comments.py` during implementation. This follows the feature-oriented organization of `tests/test_due_dates_and_tags.py` and uses the existing `client` and `created_task` fixtures from `tests/conftest.py`.

Cover:

- Creating a valid comment returns `201` with:
  - a non-empty, parseable UUID string;
  - the route’s `task_id`;
  - normalized `author` and `body`;
  - a timezone-aware UTC `created_at`.
- Listing comments for an existing task with none returns `200` and `[]`.
- Multiple comments are returned in the documented deterministic order.
- Comments created for one task do not appear under another task.
- Creating or listing comments for a missing task returns `404` using the existing task-not-found detail.
- Missing `author` or `body` returns `422`.
- Empty and whitespace-only `author` or `body` returns `422`.
- Author lengths of 1 and 100 are accepted; 101 is rejected.
- Body lengths of 1 and 2000 are accepted; 2001 is rejected.
- Client-supplied `id`, `task_id`, `created_at`, or another unknown field returns `422`.
- Deleting a task makes its nested comments unavailable and removes their in-memory storage.
- The existing 25 tests continue to pass, demonstrating that task response shapes and behavior were preserved.

Use API-level assertions as the default because existing tests exercise behavior through `TestClient`. A narrowly scoped storage assertion may be needed to prove deletion removes orphaned comment objects rather than merely making them unreachable.

## 4. Frontend Changes

Keep changes within `frontend/index.html`, matching the current single-file frontend.

Recommended interaction:

- Add a **Comments** button beside **Edit** in `createTaskCard`.
- Stop click and mouse-down propagation on the button, following the existing Edit-button pattern so comment interaction does not start card dragging.
- Open a dedicated comments dialog rather than nesting a second form inside the existing task form.
- The dialog should contain:
  - the selected task title;
  - loading, empty, error, and ready states;
  - an author input with `maxlength="100"`;
  - a body textarea with `maxlength="2000"`;
  - field-level validation messages;
  - a submit button and comments list.
- Store the selected task ID in dedicated frontend state such as `activeCommentTaskId`; do not add comments to the global task objects.
- On open, call `GET /tasks/{task_id}/comments`.
- On submit, call `POST /tasks/{task_id}/comments`, handle `422` details using the existing error-parsing approach, then refresh the comment list.
- Render author, body, and timestamps with DOM `textContent` or the existing `escapeHtml` helper. Never insert unescaped comment data into `innerHTML`.
- Reuse the task modal’s accessibility patterns: `role="dialog"`, `aria-modal`, Escape and overlay close behavior, focus on open, and focus restoration on close.
- Reuse `API_BASE`, `extractErrorMessage`, and `parseErrorResponse` rather than creating another networking convention.

The dedicated dialog keeps comment state and submission separate from task create/update behavior, so `buildTaskPayload` and the existing task form remain unchanged.

## 5. Migration or Storage Notes

No database migration is needed or allowed in Module 5.

Extend the in-memory storage pattern with a collection such as:

- `_comments: dict[str, list[CommentResponse]]`, keyed by task ID.

Planned storage behavior:

- `add_comment(task_id, payload)` generates `uuid4().hex` and `datetime.now(timezone.utc)`, matching task ID and timestamp generation in `add_task`.
- `list_comments(task_id)` returns a copied and deterministically sorted list so callers cannot mutate the stored list accidentally.
- `delete_task(task_id)` also removes `_comments[task_id]` to avoid orphaned comments.
- `_reset()` clears both `_tasks` and `_comments` so the autouse test fixture continues to isolate tests.

Comments remain process-local and disappear on restart, just like tasks. Multiple Uvicorn workers or application replicas would each have separate comment data. This is an accepted course limitation, not a reason to add a database during Module 5.

Using a separate comment collection avoids changing `TaskResponse` and prevents task updates from having to copy or validate nested comment data.

## 6. Open Questions

- Should IDs use the existing 32-character `uuid4().hex` representation or canonical hyphenated `str(uuid4())`? The former matches task IDs; both are UUID strings.
- Should author values be trimmed before storage?
- Should body values be fully trimmed, or should leading/trailing formatting be preserved while whitespace-only bodies are rejected?
- Should comments be ordered oldest-first as proposed, or newest-first for the UI?
- Is listing every comment acceptable for the course scope, or should a per-task count limit or pagination be defined now?
- Should task deletion permanently cascade to comments? This plan recommends yes.
- Are comment editing and deletion intentionally out of scope?
- Because there is no authentication, `author` is user-entered display text and can be impersonated. Is that acceptable for the course scope?
- Should the frontend use the proposed dedicated dialog or an expandable section inside each task card?

## 7. My Critique

### Data Model

- I agree with separate create/response models, server-owned identifiers and
  timestamps, explicit length limits, and keeping comments out of `TaskResponse`.
- I would decide the body-normalization rule before implementation and avoid
  adding a comment-update model until editing is actually requested.

### API Routes

- Create and list are enough for the first version; edit and delete would add
  behavior that the feature request does not require.
- The nested route shape fits because comments belong to one task and the API
  can reuse the existing task-not-found behavior.

### Tests

- The task-isolation and cascade-deletion tests give me the most confidence
  because they catch data ownership errors that simple happy-path tests miss.
- Testing every boundary is useful at the model boundary, but I would
  parameterize those cases to keep the test file readable. An accessibility
  browser check is also needed because API tests cannot verify the dialog.

### Frontend Changes

- I prefer a dedicated dialog because it keeps task editing and comment state
  separate and gives long comments more room than an expanded card.
- I would manually verify keyboard focus on open/close, Escape behavior,
  validation messages, retry behavior, and safe rendering of comment text.

### Migration or Storage Notes

- I am comfortable with restart data loss because tasks already use documented
  in-memory storage and a database is outside Module 5.
- I would first verify that nested routes return 404 after task deletion, then
  use one narrow storage assertion to prove the comment collection was removed.

### Open Questions

- Use the existing `uuid4().hex` ID format, trim author names, reject
  whitespace-only bodies while preserving meaningful body formatting, and list
  comments oldest-first. Keep the first version unpaginated, cascade on task
  deletion, and leave comment editing/deletion out of scope.
- Before implementation, confirm that user-entered author names and possible
  impersonation are acceptable for this unauthenticated local course app.

## Generic vs Repo-Grounded Codex Comparison

**Biggest difference:** The repo-grounded plan preserves the existing response
shapes, in-memory storage, route organization, fixtures, and single-file UI
instead of proposing a database or framework rewrite.

**Plan I would hand to a teammate:** The repo-grounded plan above, after the
author-normalization and lifecycle decisions are confirmed.

**Where the generic plan was still useful:** It supplied a useful checklist of
models, routes, tests, UI, and persistence questions.

**Where repo grounding mattered most:** It prevented a database migration,
preserved `TaskResponse`, reused the existing 404 contract, and matched the
current `TestClient` and frontend patterns.
