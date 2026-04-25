# PPP Intelligence Platform — Backend API

A RESTful API backend for the **Public-Private Partnership (PPP) Intelligence Platform for Thailand**, built with [FastAPI](https://fastapi.tiangolo.com/) and [SQLModel](https://sqlmodel.tiangolo.com/).

This system aggregates, stores, and serves PPP project data following the [OC4IDS](https://standard.open-contracting.org/infrastructure/) (Open Contracting for Infrastructure Data Standard), along with comprehensive risk analysis capabilities.

## Project Structure

```
backend/
├── oc4ids_datastore_api/       # Main application package
│   ├── main.py                 # FastAPI app initialization & middleware
│   ├── controllers.py          # Route handlers (endpoints)
│   ├── services.py             # Business logic layer
│   ├── daos.py                 # Data Access Objects (database queries)
│   ├── dtos.py                 # Response models (Pydantic DTOs)
│   ├── models.py               # SQLModel ORM models
│   ├── serializers.py          # OC4IDS data serialization
│   ├── middleware.py           # Performance logging middleware
│   ├── database.py             # Database engine setup
│   ├── exceptions.py           # Custom exception handlers
│   └── utils.py                # Utility functions
├── scripts/                    # Data seeding & import scripts
│   ├── seed_risk_factors.py    # Risk factor seed data
│   ├── import_risk_pattern.py  # Risk pattern CSV importer
│   ├── import_data.py          # Project data JSON importer
│   ├── init_refs.py            # Master seed script (runs all seeds)
│   └── reset_db.py             # Database reset utility
├── data/                       # Source data files
│   ├── projects(1).json        # Sample project data
│   └── *.csv                   # Risk pattern data (CSV)
├── docs/                       # Documentation & schema files
│   ├── DB_Design(5).sql        # Database design SQL
│   ├── schema.dbml             # DBML schema definition
│   └── example.json            # Example API response
├── static/                     # Static files served by the API
│   └── risk_source_references/ # Downloadable risk source documents
├── tests/                      # Test suite
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── requirements.txt
```

## Prerequisites

- Python 3.12+
- PostgreSQL database

## Local Development

### 1. Set Up Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_dev.txt
```

### 2. Configure Database

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### 3. Initialize Database

```bash
# Reset and create tables
python scripts/reset_db.py

# Seed all reference data (sectors, ministries, risk categories, risk patterns, etc.)
python scripts/init_refs.py
```

### 4. Run the Development Server

```bash
fastapi dev oc4ids_datastore_api/main.py
```

The API will be available at `http://127.0.0.1:8000`  
Interactive API docs (Swagger UI) at `http://127.0.0.1:8000/docs`

## Running with Docker

### 1. Configure Environment

Update your `.env` file with the database connection string.  
On Linux, `network_mode: "host"` is used, so `localhost` connects directly to the host's database.

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### 2. Start the API

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/projects` | List all projects (paginated, filterable) |
| `GET` | `/projects/{project_id}` | Get project details by ID |
| `POST` | `/projects` | Create a new project |
| `PUT` | `/projects/{project_id}` | Update an existing project (full replacement) |
| `DELETE` | `/projects/{project_id}` | Soft-delete a project |

**Query Parameters** for `GET /projects`:
`page`, `page_size`, `title`, `sector_id`, `ministry_id`, `concession_form_id`, `contract_type_id`, `risk_category_id`, `risk_factor_id`, `year_from`, `year_to`

### Dashboard & Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/summary` | Dashboard statistics with filter support |
| `GET` | `/compare?ids=...&ids=...` | Compare multiple projects side by side |
| `GET` | `/risk` | Risk analysis data (heatmaps, sector breakdowns) |

### Reference Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/info` | All lookup data for dropdowns (sectors, ministries, risk categories, etc.) |
| `GET` | `/risk-sources/{rs_id}/reference` | Download a risk source reference file |

### Upload

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Import project data from JSON or CSV files |

## Data Seeding

The `init_refs.py` script handles all seed data in a single run:

1. **Reference Data** — Sectors, Ministries, Contract Types, Project Types, Concession Forms, COFOG Classifications
2. **Risk Data** — Risk Categories, Risk Factors, Category-Factor Links, Risk Phases
3. **Risk Patterns** — Imported from CSV (source/phase bitmask mappings)

```bash
python scripts/init_refs.py
```

## Linting & Type Checking

```bash
black oc4ids_datastore_api/ tests/
isort oc4ids_datastore_api/ tests/
flake8 oc4ids_datastore_api/ tests/
mypy oc4ids_datastore_api/ tests/
```

## Releasing

To publish a new version, raise a PR to `main` updating the version in `pyproject.toml`. Once merged, create a git tag and GitHub release with naming `vX.Y.Z`. This will trigger a Docker image to be built and pushed, tagged with the version and `latest`.
