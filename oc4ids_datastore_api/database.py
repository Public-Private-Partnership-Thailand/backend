import os
from typing import Sequence

from sqlalchemy import Engine
from sqlmodel import Session, create_engine, select

from oc4ids_datastore_api.models import DatasetSQLModel

_engine = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(os.environ["DATABASE_URL"])
    return _engine


def fetch_all_datasets() -> Sequence[DatasetSQLModel]:
    with Session(get_engine()) as session:
        return session.exec(select(DatasetSQLModel)).all()
