# Verification — Mid-Course Project

## Baseline (before feature work)
- Branch: `mid-course-project` (created after local `git init`)
- Command: `pytest tests/ -v`
- Result: **17 passed** (existing `tests/test_tasks.py` only)
- Note: `pytest` and `httpx` were missing from the venv; installed and pinned in `requirements.txt`.

## Backend test results (after features)
- Command: `pytest tests/ -v`
- Result: **25 passed** (17 existing + **8 new** in `tests/test_due_dates_and_tags.py`)
- New coverage includes:
  - valid due date
  - invalid due date format → 422
  - overdue detection + Done exclusion + `?overdue=true` filter
  - update due date
  - create with trimmed tags
  - reject empty tag → 422
  - update tags + filter by tag (case-insensitive)
  - preserve tags after unrelated PATCH

## Behavior contract (before → after)

| Behavior | Before | After |
|---|---|---|
| Create task body | title/status/priority/assignee/… | + optional `due_date`, `tags` (default `[]`) |
| Response fields | no due/tags | + `due_date`, `tags`, computed `is_overdue` |
| `GET /tasks` filters | `status`, `priority` | + `overdue`, `tag` |
| Invalid due date | N/A | 422 |
| Blank tag | N/A | 422 |
| Existing CRUD + transitions | green | still green |

## Manual API checks
```text
POST /tasks {due_date: yesterday UTC, tags: ["demo"]} → 201, is_overdue=true
GET  /tasks?overdue=true → 200, length 1
GET  /tasks?tag=demo → 200, match
POST /tasks {due_date: "nope"} → 422
POST /tasks {tags: [""]} → 422
```

## Manual browser checks (Kanban UI)
1. Start API: `uvicorn app.main:app --reload --port 8000`
2. Open `frontend/index.html` (Live Server / static file on allowed CORS origin)
3. Create task with due date in the past → card shows Overdue pill
4. Create task with tags `backend, api` → chips render
5. Check “Overdue only” → Apply → only overdue cards remain; empty columns stay visible
6. Filter by tag `backend` → only matching tasks
7. Edit task: change due date / tags → Save → board refreshes correctly
8. Clear filters → full board returns

## Break Test evidence (≥2 tests)

### Break 1 — overdue assertion inverted
- Change: temporarily set `assert overdue_resp.json()["is_overdue"] is False` in `test_overdue_detection_and_filter`
- Result: **FAILED** — `assert True is False`
- Restore: original assertion
- Result: **PASSED**

### Break 2 — empty-tag rejection
- Intentional break candidate: remove blank-tag rejection from `_normalize_tags` (or invert `test_create_task_rejects_empty_tag` expected status to 201)
- Observed with inverted expectation: test fails while API still returns 422 for `tags: ["ok", "  "]`
- Restored expectation: **PASSED**

## Refactor checkpoint
- Extracted `utc_today()` and `compute_is_overdue()` in `app/models.py` after discovering local `date.today()` vs UTC mismatch near timezone boundaries.
- Re-ran full suite afterward: **25 passed**.
