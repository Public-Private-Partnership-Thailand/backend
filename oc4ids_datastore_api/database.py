import os
from typing import Sequence

from sqlalchemy import Engine
from sqlmodel import Session, create_engine, select
from sqlmodel import SQLModel, Field

from oc4ids_datastore_api.models import Project


engine = create_engine(os.environ["DATABASE_URL"], echo=False)
SQLModel.metadata.create_all(engine)


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(os.environ["DATABASE_URL"])
    return _engine

def get_session():
    with Session(engine) as session:
        yield session

