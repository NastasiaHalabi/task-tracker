# Task Tracker - Codex Instructions

## Stack
- Python 3.11
- FastAPI
- Pydantic v2
- pytest
- Vanilla JavaScript frontend

## Run and test commands
- Server: uvicorn app.main:app --reload
- Tests: pytest -v

## Project rules
- Status values are ToDo, InProgress, Done.
- Priority values are Low, Medium, High.
- Preserve existing API response shapes unless explicitly asked.
- Do not add authentication or a database in Module 5.

## Module 5 rules
- Module 5 is for evaluation, governance, planning, and reflection.
- Prefer read-only analysis first.
- Only create or edit files under docs/ unless I explicitly approve another path.
- Do not edit app/ while doing security review, governance, feature planning, architecture docs, or playbook work.
- If app/ or frontend/ changes unexpectedly during docs-first work, stop, show the diff, and ask before continuing.
- Do not add dependencies.
- Do not run destructive commands.

## Review expectations
- Show diffs before applying changes.
- Explain what files you read before giving a repo-grounded answer.
- If a claim is not visible in the files you read, say that clearly.
