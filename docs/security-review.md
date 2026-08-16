# Task Tracker Security Review

**Audit date:** 2026-08-16
**Scope:** Read-only review of the current working-tree snapshot
**Result:** No Critical or High findings. Three Medium, one Low, and one accepted-scope informational risk.

## Final-project remediation status

- SEC-01 was corrected by rejecting explicit null values for non-nullable PATCH
  fields at the Pydantic boundary; regression tests require HTTP 422.
- SEC-03 was corrected by removing the `"null"` CORS origin and serving the
  frontend from the already allowed `http://localhost:5500` origin.
- SEC-02, SEC-04, and SEC-05 remain documented scope or hardening decisions; no
  database, authentication system, or new dependency was added.
- The findings table below is preserved as the original read-only audit evidence.

| ID | Severity | File / location | Finding | Evidence | Suggested next step | Confidence |
|---|---|---|---|---|---|---|
| SEC-01 | Medium | `app/models.py:95-101,123-131`; `app/storage.py:119-124` | Explicit `null` values can cause unhandled 500 responses on `PATCH`. | `TaskUpdate` permits `null` for `title`, `description`, `status`, `priority`, and `tags`, but `TaskResponse` requires them to be non-null. Storage merges explicitly supplied fields before constructing `TaskResponse`. A read-only runtime probe confirmed all five inputs return `500 Internal Server Error`; existing tests cover omission, not explicit null. | Reject explicit null for non-nullable fields while continuing to allow omission for partial updates. Add regression tests expecting 422. | High |
| SEC-02 | Medium | `app/models.py:69,72,96,99`; `app/storage.py:13,39,68-82`; `Dockerfile:32,39` | Unbounded content and task count create a memory/CPU exhaustion path if the API is exposed. | `description` and `assignee` have no maximum length. Tasks accumulate without quota in a process-global dictionary, while every list request copies, filters, and sorts the complete collection. No request-size limit, pagination, rate limit, or storage cap is visible. | Add reasonable field limits and pagination. At deployment, enforce body-size and rate limits. Define a resource policy without introducing a database during Module 5. | High |
| SEC-03 | Medium | `app/main.py:23-33`; `README.md:50-52` | Trusting the CORS origin `"null"` permits arbitrary null-origin documents to access the API. | `"null"` is deliberately allowed to support `file://`, together with all methods and headers. Downloaded files and sandboxed documents can also have a null origin and could read or mutate tasks while the API is running. `allow_credentials=False` does not help because the API requires no credentials. | Remove `"null"` and serve the frontend from one of the narrowly permitted localhost origins. | High |
| SEC-04 | Informational — accepted scope | `AGENTS.md:14-18`; `app/main.py:46-136` | Authentication and authorization are intentionally absent. | Every task read/write/delete route is callable without identity checks. `AGENTS.md` explicitly prohibits adding authentication in Module 5, so this is not treated as a defect for the documented local course scope. Any client that can reach the service nevertheless has full task access. | Keep the service local/private and document the trust boundary. Design authentication only in a later, explicitly approved module. | High |
| SEC-05 | Low | `requirements.txt:1-6`; `Dockerfile:4,12-16,23`; `.github/workflows/ci.yml:15-35` | Build and CI inputs are only partially reproducible and supply-chain hardened. | Direct packages are pinned, but transitive dependencies are not locked or hash-verified. Docker uses mutable base-image tags, upgrades pip without a version pin, and installs test-only packages into the runtime environment. Actions use movable major-version tags, and CI performs tests but no dependency/security scan. | Separate runtime and test dependencies; use hash-locked dependency sets; pin container images by digest and Actions by reviewed commit SHA; add an appropriate dependency scan later. | High |

## Files inspected

- Guidance and documentation: `AGENTS.md`, `README.md`
- Backend: `app/main.py`, `app/models.py`, `app/storage.py`, `app/business_rules.py`, `app/core/config.py`, `app/routers/health.py`, `app/schemas/health.py`, and package initializers
- Tests: `tests/conftest.py`, `tests/test_tasks.py`, `tests/test_due_dates_and_tags.py`, `tests/verify_a.py`
- Frontend: `frontend/index.html`, including the complete application script and relevant form markup
- Deployment and dependencies: `requirements.txt`, `Dockerfile`, `.dockerignore`, `.github/workflows/ci.yml`
- Configuration and exclusions: `.env` key names with values redacted, `.env.example`, `.gitignore`
- No `pyproject.toml` or compose file was present.

## Categories where no issue was found

- Status and priority are enforced by Pydantic enums; unknown request fields are forbidden.
- Titles are trimmed, required, and limited to 200 characters.
- Tags reject blanks and enforce five-tag and 30-character limits.
- No obvious frontend DOM XSS was found. Task content is escaped before the few `innerHTML` assignments, while errors and other dynamic content use `textContent`.
- No tracked secrets matched the selected high-signal scan. `.env` is gitignored and excluded from the Docker context.
- No custom stack-trace exposure, backend broad-exception handler, command execution, file access, SQL, or database-injection surface was visible.
- Docker uses a multi-stage build and runs the application as a non-root user.

## Assumptions and limits

- This reviewed the current working-tree snapshot, which already contained uncommitted changes. The audit made no changes outside this report.
- All 25 existing tests passed with pytest cache and bytecode writing disabled. The PATCH-null probe changed only process-local in-memory storage.
- `pip check` reported a consistent installed dependency graph; it is not a vulnerability scan.
- A manual advisory spot-check found the installed Starlette version within a published multipart advisory range, but that advisory requires form parsing. This repository exposes JSON models and no `Form`, `UploadFile`, or `request.form()` path, so it was not counted as applicable. See [GHSA-f96h-pmfr-66vw](https://github.com/Kludex/starlette/security/advisories/GHSA-f96h-pmfr-66vw).
- No container-image scan, comprehensive dependency scanner, live penetration test, or load test was performed.
- Reverse-proxy, firewall, TLS, hosting, and GitHub repository permission settings are not present and could not be assessed.
- The frontend’s hard-coded `http://localhost:8000` API URL indicates a local-development assumption.
