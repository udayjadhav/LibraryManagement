# Neighborhood Library App

Beginner-friendly full-stack submission for the Neighborhood Library assignment:
- FastAPI backend (REST) as the source of truth
- Minimal React UI for staff workflows
- SQLAlchemy models for books, members, and borrowings
- Pytest tests for key backend behavior

## Assignment Requirement Check

The PDF explicitly requires a UI:
- `Minimal Frontend: Provide web frontend by using React (next.js preferably).`

This repository now includes a simple React frontend served from the same FastAPI app.

## Features

- Create and list books
- Create and list members
- Borrow a book
- Return a borrowing
- View current borrowings or all borrowings (optional member filter)

## Architecture (Layered)

Think of the app like a small library desk:

- **API routes** (`app/api/`) — front desk: accepts HTTP requests and returns responses.
- **Services** (`app/services/`) — librarian rules: who can borrow, duplicate email checks, return logic.
- **Repositories** (`app/repositories/`) — card catalog: async SQLAlchemy reads and writes.
- **Models** (`app/models/`) — shelf labels: SQLAlchemy tables (`Book`, `Member`, `Borrowing`).
- **Schemas** (`app/schemas/`) — request/response forms: Pydantic validation and JSON shapes.

`Borrowing` is both checkout and reservation: one row per lend, `returned_at` marks when the book came back. There is no separate Fine or Reservation table — that keeps the API small and matches how the UI already works.

## Project Structure

```text
.
├── app
│   ├── api/              # Thin HTTP routers
│   ├── services/         # Business rules
│   ├── repositories/     # Database access
│   ├── models/           # SQLAlchemy entities
│   ├── schemas/          # Pydantic DTOs
│   ├── dependencies.py   # FastAPI Depends wiring
│   ├── exceptions.py     # AppError → HTTP status mapping
│   ├── db.py
│   └── main.py           # App factory, static mount, exception handler
├── frontend
│   └── index.html
├── tests
│   ├── test_library_api.py
│   └── test_services.py
├── pyproject.toml        # Primary Python config (deps, pytest, ruff, black)
├── docker-compose.yml    # Local PostgreSQL (default database)
├── .env.example          # Sample DATABASE_URL values
├── .pre-commit-config.yaml
├── requirements.txt      # Backward-compatible install list
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.11+
- pip
- Docker and Docker Compose (recommended — default local database is PostgreSQL)

## One-Time Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
cp .env.example .env   # optional; defaults match docker-compose Postgres
```

`pyproject.toml` is the primary project config (dependencies, pytest, ruff, black).  
`.pre-commit-config.yaml` runs lint/format checks automatically on each commit.

**Backward-compatible install** (without dev tools):

```bash
pip install -r requirements.txt
```

## Local PostgreSQL (Default)

The app defaults to PostgreSQL for assignment compliance. Start Postgres with Docker Compose:

```bash
docker compose up -d
```

Wait until Postgres is healthy:

```bash
docker compose ps
```

Default connection (no env override needed):

```text
postgresql+psycopg://library:library@localhost:5432/library_db
```

Stop Postgres when finished:

```bash
docker compose down
```

To remove the database volume as well:

```bash
docker compose down -v
```

If `docker compose` is not available on your machine yet, use the SQLite fallback in the next section so you can still run the app immediately.

## Development Commands

```bash
# Run tests
pytest -q

# Lint (check only)
ruff check .

# Format
black .

# Lint + format (same checks pre-commit runs)
ruff check --fix . && black .
```

## Sample Client Call

A small client script is included at `scripts/sample_client.py`.

```bash
python scripts/sample_client.py
```

Optional API host override:

```bash
LIBRARY_API_BASE_URL=http://127.0.0.1:8000 python scripts/sample_client.py
```

## Environment Variables

- `DATABASE_URL` (optional)
  - **Default (Postgres via docker-compose):**
    ```text
    postgresql+psycopg://library:library@localhost:5432/library_db
    ```
  - **Optional SQLite fallback** (no Docker required):
    ```bash
    export DATABASE_URL="sqlite+aiosqlite:///./library.db"
    ```
  - Copy `.env.example` to `.env` to customize locally.

## Quick Run Without Docker (SQLite Fallback)

Use this when Docker/Postgres is unavailable locally.

```bash
source .venv/bin/activate
export DATABASE_URL="sqlite+aiosqlite:///./library.db"
uvicorn app.main:app --reload
```

## Local Run

```bash
# 1) Start Postgres (default path)
docker compose up -d

# 2) Activate venv and install
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 3) Run API + UI
uvicorn app.main:app --reload
```

If startup fails with Postgres connection errors (for example `connection refused` on `localhost:5432`), either:
- start PostgreSQL first (`docker compose up -d`), or
- switch to SQLite fallback:
  ```bash
  export DATABASE_URL="sqlite+aiosqlite:///./library.db"
  uvicorn app.main:app --reload
  ```

App URLs:
- UI: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- API docs (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API Overview

- `GET /health`
- `POST /books`
- `PUT /books/{book_id}`
- `GET /books`
- `POST /members`
- `PUT /members/{member_id}`
- `GET /members`
- `POST /borrowings/borrow`
- `POST /borrowings/{borrowing_id}/return`
- `GET /borrowings?member_id=<id>&active_only=true|false`

## UI Usage

1. Open `/` in browser.
2. Use forms to create books and members.
3. Use borrow form with member ID and book ID.
4. Use return form with borrowing ID.
5. Use borrowings filter to view active-only or all records.

## Tests

Run:

```bash
pytest -q
```

Current tests cover:
- API create/update/list behavior (`test_library_api.py`)
- Service-layer rules with mocked repositories (`test_services.py`)
- Borrow and return flows
- Error handling (not found/conflict/inactive member)
- Active vs all borrowings
- UI route serving (`GET /`)

## Duplicate Handling Rules

- Books: duplicate create/update is blocked on normalized `(title, author)` where both values are trimmed and compared case-insensitively.
- Members: duplicate create/update is blocked on normalized `email` (trimmed, lowercase).
- Borrowings: only one active borrowing per book is allowed; conflicts return `409`.
- API routes stay thin, with duplicate checks in services and reinforcing DB constraints where applicable.

## Lightweight Checks

- Start app locally and verify:
  - `GET /health` returns `{"status": "ok"}`
  - `/docs` loads OpenAPI docs
  - `/` loads UI and performs end-to-end API operations

## GitHub Upload Checklist

Commit:
- `app/`
- `frontend/`
- `tests/`
- `pyproject.toml`
- `docker-compose.yml`
- `.env.example`
- `.pre-commit-config.yaml`
- `requirements.txt`
- `.gitignore`
- `README.md`

Do not commit:
- `.venv/`
- `__pycache__/`, `.pytest_cache/`
- local DB files (`library.db`, `test_library.db`, `*.sqlite3`)
