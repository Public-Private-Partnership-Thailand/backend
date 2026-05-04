import os

from sqlmodel import Session, SQLModel, create_engine


engine = create_engine(os.environ.get("DATABASE_URL", "sqlite:///:memory:"), echo=False)

def init_db():
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        print("Warning: Could not create tables on startup", e)

init_db()


def get_session():
    with Session(engine) as session:
        yield session

