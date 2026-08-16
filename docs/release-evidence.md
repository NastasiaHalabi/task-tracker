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
- Latest verification run: [CI run 31949041937](https://github.com/NastasiaHalabi/task-tracker/actions/runs/31949041937) completed successfully for commit `18e55081534caabf6de23ca45330160a299b1864` on `final-project`.
- Jobs passed: Python 3.11 pytest suite and Docker smoke test.

## Docker evidence

- Build command: `docker build -t task-tracker:final .`
- Run command: `docker run --rm --name task-tracker-final -p 8000:8000 task-tracker:final`
- Health command: `curl http://localhost:8000/health`
- Non-root check: `Dockerfile` creates and switches to user `app`.
- No-baked-secrets check: `.dockerignore` excludes `.env` and `.env.*`; `Dockerfile` copies only `requirements.txt` and `app/`.
- CI runtime result: passed on the GitHub-hosted `ubuntu-latest` runner in [Docker smoke-test job 95169523272](https://github.com/NastasiaHalabi/task-tracker/actions/runs/31949041937/job/95169523272).
- The CI job built `task-tracker:final`, started the container, received a valid `/health` response with `status: "ok"`, confirmed runtime UID `1000`, and confirmed `/app/.env` was absent.
- Local-machine note: Docker Desktop's internal WSL distribution is running, but the supported Windows Docker CLI is missing. The successful result above is CI runtime evidence and is not presented as a local Docker run.

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
| Docker excludes secrets, runs non-root, and serves `/health` | `.dockerignore`, `Dockerfile`, and Docker smoke-test job | Confirmed by static inspection and CI runtime verification | Added a failing CI Docker smoke test; local CLI remains unavailable |
| CI uses Python 3.11 and runs pytest | `.github/workflows/ci.yml` and CI run 31949041937 | Confirmed by file inspection and successful run | Recorded the run link |
