# Release Evidence

## Baseline

- Branch: `final-project`
- Date: 2026-08-16
- Public repository: `https://github.com/NastasiaHalabi/task-tracker`
- Standard local app command: `python -m uvicorn app.main:app --reload --port 8000`
- Verification command used: `venv\Scripts\python.exe -B -m uvicorn app.main:app --host 127.0.0.1 --port 8001` because an unrelated WSL relay already occupied port 8000.
- `/health` result: `GET http://127.0.0.1:8001/health` returned HTTP 200 with `{"status":"ok","timestamp":"2026-08-16T12:49:42.502010+00:00"}`.
- Frontend check: served the unchanged UI on an allowed port 5500 origin and connected it to the final backend.
- Test command: `python -B -m pytest -p no:cacheprovider -v`
- Initial result: 25 passed in 0.31 seconds before final security corrections.
- Final result: 32 passed in 0.60 seconds after final security corrections.
- Environment note: the existing local venv is Python 3.9.13. CI and Docker are configured for the required Python 3.11.

## CI evidence

- Workflow file: `.github/workflows/ci.yml`
- Trigger: pushes to all branches and pull requests to `main`.
- Python version: exact `3.11` configuration through `actions/setup-python`.
- Test command used by CI: `pytest -v --tb=short`
- Dependency installation: `pip install -r requirements.txt`
- Shortcut check: no `continue-on-error`, no `|| true`, and pytest is not skipped.
- Latest run: [CI run 31948234294](https://github.com/NastasiaHalabi/task-tracker/actions/runs/31948234294) completed successfully for commit `ae624936ba86a17642d84b01eb1f3135842a9738` on `final-project`.

## Docker evidence

- Build command: `docker build -t task-tracker:final .`
- Run command: `docker run --rm --name task-tracker-final -p 8000:8000 task-tracker:final`
- Health command: `curl http://localhost:8000/health`
- Non-root check: `Dockerfile` creates and switches to user `app`.
- No-baked-secrets check: `.dockerignore` excludes `.env` and `.env.*`; `Dockerfile` copies only `requirements.txt` and `app/`.
- Runtime result: pending. Docker Desktop's internal WSL distribution is running, but the supported Windows Docker CLI is missing, so build/run verification cannot be completed from this workstation yet.

## Frontend verification

- Technical browser check: passed. The empty three-column board loaded without console errors.
- Create flow: created a High-priority task with `release` and `docs` tags; it appeared in `ToDo`.
- Edit flow: changed the description and moved the task to `InProgress`; the updated card appeared in the correct column.
- Filter flow: filtering by the `release` tag retained the matching task.
- Owner check: the repository owner should repeat a brief create/edit check before submission so the human verification and ownership statement are personal.

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| README test count matches the suite | `pytest` collection and result | Confirmed: 32 collected and passed | Updated README from 25 to 32 |
| `/health` returns HTTP 200 with status and timestamp | FastAPI `TestClient` and health schema | Confirmed | None |
| Frontend can be served on port 5500 | README command and CORS configuration | Configuration agrees | Removed unsafe direct `file://` claim |
| Docker excludes secrets and runs non-root | `.dockerignore` and `Dockerfile` | Confirmed by static inspection | Runtime verification still required |
| CI uses Python 3.11 and runs pytest | `.github/workflows/ci.yml` | Confirmed by file inspection | Add run link after push |
