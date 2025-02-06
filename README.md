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

### Run app

```
fastapi dev oc4ids_datastore_api/main.py
```

### Run linting and type checking

```
black oc4ids_datastore_api/
isort oc4ids_datastore_api/
flake8 oc4ids_datastore_api/
mypy oc4ids_datastore_api/
```
