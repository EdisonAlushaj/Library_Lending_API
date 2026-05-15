# Library Lending API

A RESTful backend API for a small library lending system, built with FastAPI and SQLAlchemy. The API allows librarians to manage books, authors, categories, and members, as well as track book loans — including borrowing, returning, overdue detection, and loan history. All endpoints are documented automatically via FastAPI's OpenAPI interface at `/docs`.

---

## Setup

### Prerequisites

- Python 3.10+
- pip

### 1. Clone the repository and create a virtual environment

```bash
git clone <your-repo-url>
cd Library_Lending_API
python -m venv venv
```

Activate the virtual environment:

- **Windows:** `.\venv\Scripts\Activate.ps1`
- **Mac/Linux:** `source venv/bin/activate`

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

Create a `.env` file in the project root:

```
API_KEY=secret
DATABASE_URL=sqlite:///./library.db
```

Or export them directly in your terminal:

```bash
# Windows PowerShell
$env:API_KEY = "secret"
$env:DATABASE_URL = "sqlite:///./library.db"
```

### 4. Apply database migrations

```bash
alembic upgrade head
```

### 5. Seed the database

```bash
python scripts/seed.py
```

This populates the database with 22 books, 10 authors, 4 categories, 12 members, and 31 loans (returned, active, and overdue).

### 6. Start the server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

---

## Docker

### Run with Docker Compose

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000` with migrations applied and seed data loaded automatically.

### Environment variables for Docker

Set in `docker-compose.yml` or via a `.env` file:

```
API_KEY=secret
DATABASE_URL=postgresql://postgres:postgres@db:5432/library
```

---

## Running Tests

```bash
pytest tests/ -v
```

Tests use an in-memory SQLite database and do not affect your development database.

---

## Authentication

All `POST`, `PATCH`, and `DELETE` endpoints require an API key passed in the request header:

```
X-API-Key: <your-api-key>
```

The key is compared against the `API_KEY` environment variable. A missing or incorrect key returns `401 Unauthorized`. `GET` endpoints are open.

---

## Endpoints

Full interactive documentation is available at `http://localhost:8000/docs`.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/books` | List books (paginated) |
| GET | `/api/v1/books/search` | Search books with filters and sorting |
| GET | `/api/v1/books/{id}` | Get a book |
| POST | `/api/v1/books` | Create a book |
| PATCH | `/api/v1/books/{id}` | Update a book |
| DELETE | `/api/v1/books/{id}` | Delete a book |
| GET | `/api/v1/books/{id}/loan-history` | Paginated loan history for a book |
| GET | `/api/v1/members` | List members (paginated) |
| GET | `/api/v1/members/{id}` | Get a member |
| POST | `/api/v1/members` | Create a member |
| PATCH | `/api/v1/members/{id}` | Update a member |
| DELETE | `/api/v1/members/{id}` | Delete a member |
| GET | `/api/v1/authors` | List authors (paginated) |
| GET | `/api/v1/authors/{id}` | Get an author |
| POST | `/api/v1/authors` | Create an author |
| PATCH | `/api/v1/authors/{id}` | Update an author |
| DELETE | `/api/v1/authors/{id}` | Delete an author |
| GET | `/api/v1/categories` | List categories (paginated) |
| GET | `/api/v1/categories/{id}` | Get a category |
| POST | `/api/v1/categories` | Create a category |
| PATCH | `/api/v1/categories/{id}` | Update a category |
| DELETE | `/api/v1/categories/{id}` | Delete a category |
| GET | `/api/v1/loans` | List loans with filters |
| POST | `/api/v1/loans` | Borrow a book |
| POST | `/api/v1/loans/{id}/return` | Return a borrowed book |
| GET | `/api/v1/reports/top-borrowers` | Top N members by loan count |
| GET | `/api/v1/reports/overdue-loans` | All currently overdue loans |

---

## Notes

lighthouse

The `GET /api/v1/books/search` endpoint supports the following query parameters: `q`, `category_id`, `author_id`, `available_only`, `published_after`, `published_before`, `sort_by` (title, published_year, popularity), `sort_order` (asc, desc), `page`, `page_size` (max 100). All filters compose — applying multiple filters together narrows results correctly.

---

## Limitations and Known Issues

- Authentication uses a simple static API key. A production system would use JWT or OAuth2.
- The SQLite database is stored as a local file (`library.db`). For production, switch to PostgreSQL by setting `DATABASE_URL` accordingly.
- The `DELETE /api/v1/books/{id}` endpoint prevents deletion if any active loans exist, but does not cascade-delete returned loan history.
- No rate limiting is implemented.
