import os
from typing import Sequence

from sqlmodel import Session, create_engine, select

from oc4ids_datastore_api.models import DatasetSQLModel

engine = create_engine(os.environ["DATABASE_URL"])


def fetch_all_datasets() -> Sequence[DatasetSQLModel]:
    with Session(engine) as session:
        return session.exec(select(DatasetSQLModel)).all()
