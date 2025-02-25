FROM python:3.12-slim

RUN apt-get update \
  && apt-get install -y libpq-dev gcc

WORKDIR /oc4ids_datastore_api

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN pip install .

EXPOSE 8000

ENTRYPOINT ["fastapi", "run", "oc4ids_datastore_api/main.py"]
