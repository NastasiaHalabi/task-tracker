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
2. Serve the frontend on an allowed local origin:

```bash
python -m http.server 5500 --directory frontend
```

3. Open `http://localhost:5500` in the browser. VS Code/Cursor Live Server on
   port 5500 is also supported. Direct `file://` access is intentionally not
   allowed because null-origin pages are not a safe CORS trust boundary.

Create/edit tasks from the modal. Use the filter bar for **tag** and **Overdue only**.

## Running tests

```bash
pytest tests/ -v
```

Expect **32** passing tests (17 baseline CRUD/transition tests, 8 due-date/tag
tests, and 7 final security-regression cases).

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

## Final Project

**Branch reviewed:** `final-project`

### What this submission demonstrates

- The existing Task Tracker remains inside the intended course scope.
- GitHub Actions runs the pytest suite on pushes and pull requests.
- The Docker image uses Python 3.11, runs as a non-root user, and includes a
  `/health` check.
- AI review, security, release, and ownership evidence is stored in `docs/`.

### How to run locally

```bash
python -m venv venv
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

In a second terminal, serve the frontend:

```bash
python -m http.server 5500 --directory frontend
```

Then open `http://localhost:5500`.

### How to run tests

```bash
python -m pytest tests/ -v
```

### How to run with Docker

```bash
docker build -t task-tracker:final .
docker run --rm --name task-tracker-final -p 8000:8000 task-tracker:final
curl http://localhost:8000/health
```

### Evidence files

- `docs/release-evidence.md`
- `docs/final-ai-review.md`
- `docs/ai-playbook.md`
- `docs/security-review.md`

### AI assistance summary

AI helped review documentation, CI, Docker, code changes, and security risks.
I verified the work through diff review, pytest, `/health`, CORS regression tests,
and a manual frontend check. I rejected larger suggestions such as a separate
Tag database model because they were outside the course scope.
