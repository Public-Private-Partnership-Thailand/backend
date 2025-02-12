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

## Releasing

To publish a new version, raise a PR to `main` updating the version in `pyproject.toml`. Once merged, create a git tag and GitHub release for the new version, with naming `vX.Y.Z`. This will trigger a docker image to to be built and pushed, tagged with the version and `latest`.
