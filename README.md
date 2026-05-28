# Neighborhood Library App (Take-Home)

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

## Project Structure

```text
.
├── app
│   ├── db.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── frontend
│   └── index.html
├── tests
│   └── test_library_api.py
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.11+
- pip
- (Optional) PostgreSQL if you want to run with Postgres instead of SQLite

## Environment Variables

- `DATABASE_URL` (optional)
  - Default: `sqlite:///./library.db`
  - Example Postgres:
    ```bash
    export DATABASE_URL="postgresql+psycopg://<user>:<password>@localhost:5432/library_db"
    ```

## Local Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
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
- API create/update/list behavior
- Borrow and return flows
- Error handling (not found/conflict/inactive member)
- Active vs all borrowings
- UI route serving (`GET /`)

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
- `requirements.txt`
- `pytest.ini`
- `.gitignore`
- `README.md`

Do not commit:
- `.venv/`
- `__pycache__/`, `.pytest_cache/`
- local DB files (`library.db`, `test_library.db`, `*.sqlite3`)
