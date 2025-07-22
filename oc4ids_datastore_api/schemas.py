import datetime

from pydantic import BaseModel


class Publisher(BaseModel):
    name: str
    country: str | None


class License(BaseModel):
    url: str | None
    title: str | None
    title_short: str | None


class Portal(BaseModel):
    url: str | None
    title: str | None


class Download(BaseModel):
    format: str
    url: str


class Dataset(BaseModel):
    loaded_at: datetime.datetime
    source_url: str
    publisher: Publisher
    license: License
    portal: Portal
    downloads: list[Download]
