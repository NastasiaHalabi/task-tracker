# Task Tracker API

A learning-project REST API built with FastAPI for creating, viewing, filtering, updating, and deleting tasks. The Kanban frontend lives in `frontend/`.

**Mid-course branch:** `mid-course-project`  
**New features:** optional due dates + overdue filter; tags/labels with tag filter.  
**Workflow docs:** see [`docs/midcourse/`](docs/midcourse/).

## Setup

### 1. Create a virtual environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env      # Linux/macOS
copy .env.example .env    # Windows PowerShell
```

## Running the backend

```bash
uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`.

## Opening the frontend

1. Start the backend on port 8000 (required).
2. Open `frontend/index.html` in the browser.
   - Recommended: VS Code/Cursor **Live Server** on port `5500` (CORS already allows `http://localhost:5500` and `http://127.0.0.1:5500`).
   - Opening the file directly (`file://`) also works with the configured `"null"` CORS origin.

Create/edit tasks from the modal. Use the filter bar for **tag** and **Overdue only**.

## Running tests

```bash
pytest tests/ -v
```

Expect **25** passing tests (17 baseline CRUD/transition tests + 8 due-date/tag tests).

## Useful API examples

```bash
# Create with due date + tags
curl -X POST http://localhost:8000/tasks ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Ship docs\",\"due_date\":\"2026-07-01\",\"tags\":[\"docs\",\"urgent\"]}"

# Overdue only
curl "http://localhost:8000/tasks?overdue=true"

# Filter by tag
curl "http://localhost:8000/tasks?tag=docs"
```

## Health check

```bash
curl http://localhost:8000/health
```
