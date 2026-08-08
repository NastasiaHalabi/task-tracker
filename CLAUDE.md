# Task Tracker

## Stack
- Python 3.11
- FastAPI + Pydantic v2 + Uvicorn
- pytest + httpx for tests
- Vanilla JavaScript frontend in frontend/index.html

## Run
- Server: uvicorn app.main:app --reload --port 8000
- Tests: pytest -v
- Frontend: open frontend/index.html with Live Server, or use the local serving approach from Module 3

## Architecture
- app/main.py: FastAPI app, routes, CORS middleware, and route handlers
- app/models.py: Pydantic schemas and validation types
- app/storage.py: in-memory task store
- tests/: pytest tests
- frontend/index.html: Kanban board UI from Module 3

## Business rules that must not be violated
- Valid transitions: ToDo -> InProgress, InProgress -> Done, Done -> InProgress
- Invalid transitions: ToDo -> Done, Done -> ToDo, same status -> same status
- Invalid transitions return 422
- Title is required, trimmed, non-empty
- Frontend must keep loading, empty, error, and populated states
- Frontend status values must stay ToDo, InProgress, Done

## Do not
- Do not add authentication
- Do not introduce a database without asking
- Do not change public response shapes without explicit approval
- Do not remove tests to make CI pass
- Do not run destructive shell commands without explicit confirmation
- Do not use always allow for broad shell permissions

@README.md