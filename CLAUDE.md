# OC4IDS Datastore API

FastAPI backend for Thailand PPP infrastructure project data (OC4IDS standard).

## Stack
- **Framework**: FastAPI + SQLModel (SQLAlchemy ORM)
- **DB**: PostgreSQL 16
- **Runtime**: Python 3.12, Uvicorn
- **Container**: Docker + docker-compose

## Local dev

```bash
# Start everything
docker-compose up --build

# Run API only (assumes local Postgres)
uvicorn oc4ids_datastore_api.main:app --reload --port 8000

# Run migrations
python scripts/migrate.py
```

API runs at `http://localhost:8000`. Docs at `/docs`.

## docker-compose startup sequence
The `api` service runs:
1. `reset_db.py` — drop/recreate all tables
2. `init_refs.py` — seed reference data
3. `import_data_json.py` — import project data from `data/`
4. uvicorn

**Warning**: `docker-compose up` destroys and re-imports all data. To keep data intact, use `docker-compose restart api` after a code change (without recreating the container).

## Key directories
- `oc4ids_datastore_api/` — main package
  - `main.py` — app factory, router registration
  - `models/` — SQLModel table definitions
  - `schemas/` — Pydantic request/response schemas
  - `services/` — business logic (`project_service.py`, `risk_service.py`)
  - `routers/` — FastAPI route handlers
  - `serializers.py` — ORM → dict serialization
  - `database.py` — engine/session setup
- `scripts/` — one-shot admin scripts (migrate, reset, import)
- `data/` — source JSON files for import

## Important models
- `Impact` table has a `kind` column: `"description"` | `"impact"` to separate risk description from impact_statement rows
- `CategoryFactorLink` maps which risk factors belong to which risk categories (many-to-many reference table)
- `AdditionalClassification` stores scheme/code pairs; never create a new row using a numeric id as the code

## Custom slash commands
- `/deploy` — deploy checklist
- `/logs` — check docker logs
