from fastapi import FastAPI

from oc4ids_datastore_api.schemas import Dataset
from oc4ids_datastore_api.services import get_all_datasets

app = FastAPI()


@app.get("/datasets")
def get_datasets() -> list[Dataset]:
    return get_all_datasets()
