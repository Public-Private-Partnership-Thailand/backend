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
