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

```
export DATABASE_URL="postgresql://oc4ids_datastore_read_only@localhost/oc4ids_datastore"
```

### Run app

```
fastapi dev oc4ids_datastore_api/main.py
```

### View the OpenAPI schema

While the app is running, go to `http://127.0.0.1:8000/docs/`

### Run linting and type checking

```
black oc4ids_datastore_api/ tests/
isort oc4ids_datastore_api/ tests/
flake8 oc4ids_datastore_api/ tests/
mypy oc4ids_datastore_api/ tests/
```

## API Endpoints

The API provides the following endpoints:

- `GET /api/datasets` - Get all projects (returns list of ProjectData)
- `GET /api/datasets/{project_id}` - Get a single project by ID
- `POST /api/datasets` - Create a new project (accepts ProjectData format)
- `PUT /api/datasets/{project_id}` - Update an existing project
- `DELETE /api/datasets/{project_id}` - Delete a project

All endpoints return data in the `ProjectData` format expected by the frontend.

## Frontend Integration

The frontend is configured to connect to the backend API at `http://localhost:8000` by default. This can be overridden by setting the `NEXT_PUBLIC_API_URL` environment variable.

If the backend is not available, the frontend will automatically fall back to the external S3 API.

## Releasing

To publish a new version, raise a PR to `main` updating the version in `pyproject.toml`. Once merged, create a git tag and GitHub release for the new version, with naming `vX.Y.Z`. This will trigger a docker image to to be built and pushed, tagged with the version and `latest`.
