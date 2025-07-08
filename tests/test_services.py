import datetime

from pytest_mock import MockerFixture

from oc4ids_datastore_api.models import DatasetSQLModel
from oc4ids_datastore_api.schemas import Dataset, Download, License, Portal, Publisher
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
        publisher_country="ab",
        license_url="https://license.com",
        license_title="License",
        license_title_short="L",
        portal_url="https://portal.com",
        portal_title="Portal",
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
        publisher=Publisher(name="test_publisher", country="ab"),
        license=License(title="License", title_short="L", url="https://license.com"),
        portal=Portal(title="Portal", url="https://portal.com"),
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
        license_title_short="L",
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
        publisher=Publisher(name="test_publisher", country=None),
        license=License(title="License", title_short="L", url="https://license.com"),
        portal=Portal(title=None, url=None),
        downloads=[
            Download(format="json", url="https://downloads/test_dataset.json"),
        ],
    )

    assert datasets == [expected_dataset]
