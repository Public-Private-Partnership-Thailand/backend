# OC4IDS Datastore API

## Local Development

### Prerequisites

- Python 3.12

### Install Python requirements

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_dev.txt
```

### Set database enrivonment variable

With a read-only user, set the path to the already existing database, which is created by [oc4ids-datastore-pipeline](https://github.com/OpenDataServices/oc4ids-datastore-pipeline).

```bash
export DATABASE_URL="postgresql://user:password@localhost/dbname"
```

Alternatively, you can create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Run app

```
fastapi dev oc4ids_datastore_api/main.py
```

### View the OpenAPI schema

While the app is running, go to `http://127.0.0.1:8000/docs/`

### Run linting and type checking

```bash
black oc4ids_datastore_api/ tests/
isort oc4ids_datastore_api/ tests/
flake8 oc4ids_datastore_api/ tests/
mypy oc4ids_datastore_api/ tests/
```

## Running with Docker

You can use Docker Compose to run the API in a containerized environment.

### 1. Database Configuration for Docker (Linux)

By default on Linux, this project uses `network_mode: "host"` in `docker-compose.yml`. This allows the container to access the host's network directly.

**This means you can use `localhost` to connect to your database**, exactly like in local development.

Update your `.env` file:
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
- `GET /api/v1/projects` - Get all projects with pagination and filters.
  - Query params: `page`, `page_size`, `title`, `sector_id`, `ministry_id`, `year_from`, `year_to`.
- `GET /api/v1/projects/{project_id}` - Get a single project by ID.
- `POST /api/v1/projects` - Create a new project.
- `PUT /api/v1/projects/{project_id}` - Update an existing project.
- `DELETE /api/v1/projects/{project_id}` - Delete a project.

### Tools & Analysis
- `GET /api/v1/summary` - Get summary statistics for the dashboard.
  - Supports filters by sector, ministry, agency, and date ranges.
- `GET /api/v1/compare` - Compare multiple projects by IDs.
  - Query param: `ids` (multiple).
- `GET /api/v1/info` - Get reference data (sectors, ministries, etc.) for dropdowns.
- `POST /api/v1/upload` - Upload project data via JSON or CSV files.

### Debug
- `GET /api/debug/reset-db` - Resets the database schema (Warning: deletes all data).

## Frontend Integration

The frontend is configured to connect to the backend API at `http://localhost:8000` by default. This can be overridden by setting the `NEXT_PUBLIC_API_URL` environment variable.

If the backend is not available, the frontend will automatically fall back to the external S3 API.

## Releasing

To publish a new version, raise a PR to `main` updating the version in `pyproject.toml`. Once merged, create a git tag and GitHub release for the new version, with naming `vX.Y.Z`. This will trigger a docker image to to be built and pushed, tagged with the version and `latest`.
