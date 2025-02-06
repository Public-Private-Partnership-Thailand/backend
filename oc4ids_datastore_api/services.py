from oc4ids_datastore_api.database import fetch_all_datasets
from oc4ids_datastore_api.models import DatasetSQLModel
from oc4ids_datastore_api.schemas import Dataset, Download, License, Publisher


def _transform_dataset(dataset: DatasetSQLModel) -> Dataset:
    downloads = [
        Download(format="json", url=(dataset.json_url or "")),
        Download(format="csv", url=(dataset.csv_url or "")),
        Download(format="xlsx", url=(dataset.xlsx_url or "")),
    ]
    return Dataset(
        loaded_at=dataset.updated_at,
        source_url=dataset.source_url,
        publisher=Publisher(name=dataset.publisher_name),
        license=License(url=dataset.license_url, name=dataset.license_name),
        downloads=downloads,
    )


def get_all_datasets() -> list[Dataset]:
    datasets = fetch_all_datasets()
    return [_transform_dataset(dataset) for dataset in datasets]
