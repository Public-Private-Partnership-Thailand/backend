import datetime

from sqlmodel import Field, SQLModel


class DatasetSQLModel(SQLModel, table=True):
    __tablename__ = "dataset"

    dataset_id: str = Field(primary_key=True)
    source_url: str
    publisher_name: str
    publisher_country: str | None
    license_url: str | None
    license_title: str | None
    license_title_short: str | None
    portal_title: str | None
    portal_url: str | None
    json_url: str | None
    csv_url: str | None
    xlsx_url: str | None
    updated_at: datetime.datetime
