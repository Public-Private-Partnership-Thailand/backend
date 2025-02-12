from oc4ids_datastore_api.database import fetch_all_datasets
from oc4ids_datastore_api.models import DatasetSQLModel
from oc4ids_datastore_api.schemas import Dataset, Download, License, Publisher


def _transform_dataset(dataset: DatasetSQLModel) -> Dataset:
    download_urls = {
        "json": dataset.json_url,
        "csv": dataset.csv_url,
        "xlsx": dataset.xlsx_url,
    }
    downloads = [
        Download(format=format, url=url) for format, url in download_urls.items() if url
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
