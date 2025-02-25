import datetime

from pytest_mock import MockerFixture

from oc4ids_datastore_api.models import DatasetSQLModel
from oc4ids_datastore_api.schemas import Dataset, Download, License, Publisher
from oc4ids_datastore_api.services import get_all_datasets


def test_get_all_datasets(mocker: MockerFixture) -> None:
    patch_fetch_all_datasets = mocker.patch(
        "oc4ids_datastore_api.services.fetch_all_datasets"
    )
    now = datetime.datetime.now()
    dataset_sql_model = DatasetSQLModel(
        dataset_id="test_dataset",
        source_url="https://test-dataset.json",
        publisher_name="test_publisher",
        license_url="https://license.com",
        license_title="License",
        json_url="https://downloads/test_dataset.json",
        csv_url="https://downloads/test_dataset.csv",
        xlsx_url="https://downloads/test_dataset.xlsx",
        updated_at=now,
    )
    patch_fetch_all_datasets.return_value = [dataset_sql_model]

    datasets = get_all_datasets()

    expected_dataset = Dataset(
        loaded_at=now,
        source_url="https://test-dataset.json",
        publisher=Publisher(name="test_publisher"),
        license=License(title="License", url="https://license.com"),
        downloads=[
            Download(format="json", url="https://downloads/test_dataset.json"),
            Download(format="csv", url="https://downloads/test_dataset.csv"),
            Download(format="xlsx", url="https://downloads/test_dataset.xlsx"),
        ],
    )
    assert datasets == [expected_dataset]


def test_get_all_datasets_missing_download_formats(mocker: MockerFixture) -> None:
    patch_fetch_all_datasets = mocker.patch(
        "oc4ids_datastore_api.services.fetch_all_datasets"
    )
    now = datetime.datetime.now()
    dataset_sql_model = DatasetSQLModel(
        dataset_id="test_dataset",
        source_url="https://test-dataset.json",
        publisher_name="test_publisher",
        license_url="https://license.com",
        license_title="License",
        json_url="https://downloads/test_dataset.json",
        csv_url=None,
        xlsx_url=None,
        updated_at=now,
    )
    patch_fetch_all_datasets.return_value = [dataset_sql_model]

    datasets = get_all_datasets()

    expected_dataset = Dataset(
        loaded_at=now,
        source_url="https://test-dataset.json",
        publisher=Publisher(name="test_publisher"),
        license=License(title="License", url="https://license.com"),
        downloads=[
            Download(format="json", url="https://downloads/test_dataset.json"),
        ],
    )

    assert datasets == [expected_dataset]
