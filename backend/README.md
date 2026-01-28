# Content Quality Engine - Backend

FastAPI backend for the Internal Content Quality Engine with Human-in-the-Loop.

## Tech Stack

- **Python**: 3.12+
- **Web Framework**: FastAPI 0.110+
- **Database**: PostgreSQL 15+ with SQLAlchemy Core 2.0 (async)
- **Task Queue**: Celery 5.3+ with Redis 7+
- **Validation**: Pydantic v2

## Project Structure

```
backend/
├── app/
│   ├── core/           # Core configuration and utilities
│   │   ├── config.py   # Pydantic settings
│   │   ├── database.py # SQLAlchemy async engine
│   │   ├── logging.py  # Logging configuration
│   │   └── security.py # Auth and JWT utilities
│   ├── api/            # API endpoints (TODO)
│   ├── models/         # Database models (TODO)
│   ├── schemas/        # Pydantic schemas (TODO)
│   ├── tasks/          # Celery tasks (TODO)
│   └── main.py         # FastAPI app
├── alembic/            # Database migrations
├── tests/              # Test suite (TODO)
├── celery_worker.py    # Celery worker entry point
├── pyproject.toml      # Dependencies
└── .env.example        # Environment template
```

## Setup

### 1. Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Redis 7+

### 2. Install Dependencies

```bash
cd backend
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

### 3. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key (generate with `openssl rand -hex 32`)

### 4. Database Setup

Initialize Alembic:
```bash
alembic init alembic
```

Create initial migration:
```bash
alembic revision --autogenerate -m "Initial schema"
```

Apply migrations:
```bash
alembic upgrade head
```

## Running the Application

### Development Mode

**API Server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Celery Worker:**
```bash
celery -A celery_worker.celery_app worker --loglevel=info
```

**Celery Beat (for scheduled tasks):**
```bash
celery -A celery_worker.celery_app beat --loglevel=info
```

### Production Mode

Use a process manager like systemd or supervisord.

**API Server:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Celery Worker:**
```bash
celery -A celery_worker.celery_app worker --loglevel=warning --concurrency=4
```

## API Documentation

When running in development mode:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Health Checks

- **API Health**: `GET /health`
- **Celery Health**: Execute task `tasks.health_check`

## Development

### Code Quality

**Format code:**
```bash
black .
```

**Lint code:**
```bash
ruff check .
```

**Type check:**
```bash
mypy app/
```

### Testing

```bash
pytest
```

With coverage:
```bash
pytest --cov=app --cov-report=html
```

## Architecture Notes

### Immutability Enforcement

- Content tables (`blog_versions`, `ai_detector_scores`, etc.) use PostgreSQL triggers to prevent UPDATE/DELETE
- `evaluation_runs` allows status updates (workflow metadata) but protects core data
- See `01_architecture/schema.sql` for full schema

### Human-in-the-Loop

- `is_human` verification is database-backed (NOT JWT claims)
- All approval endpoints require `require_human()` dependency
- See `04_human_review/approval_rules.md` for compliance policies

### Async-First Design

- All database operations use `asyncpg` and SQLAlchemy Core async
- FastAPI endpoints are `async def`
- Celery tasks handle long-running operations (LLM calls, detector APIs)

## Next Steps

1. Implement database models in `app/models/`
2. Implement Pydantic schemas in `app/schemas/`
3. Implement API endpoints in `app/api/v1/`
4. Implement Celery tasks in `app/tasks/`
5. Add tests in `tests/`

## License

Internal use only.
