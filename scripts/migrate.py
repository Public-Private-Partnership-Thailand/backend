"""
Incremental DB migration — safe to run on an existing database.
Uses IF NOT EXISTS so it is idempotent (can be run many times).
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from sqlmodel import SQLModel, Session, text
from oc4ids_datastore_api.database import engine
from oc4ids_datastore_api.models import *  # noqa: F401,F403  — populate metadata


MIGRATIONS = [
    # 2026-05-09: separate description from impact_statement in Impact table
    "ALTER TABLE impact ADD COLUMN IF NOT EXISTS kind VARCHAR NOT NULL DEFAULT 'impact'",
    # 2026-05-09: remove bad entries created when numeric DB id was stored as code
    "DELETE FROM additional_classifications WHERE scheme = 'รูปแบบการจัดสรรกรรมสิทธิ์' AND code ~ '^[0-9]+$'",
]


def run_migrations():
    print("Running migrations...")
    with Session(engine) as session:
        for sql in MIGRATIONS:
            print(f"  {sql}")
            session.exec(text(sql))
        session.commit()
    print("Migrations done.")


def create_missing_tables():
    print("Creating missing tables...")
    SQLModel.metadata.create_all(engine, checkfirst=True)
    print("Tables up to date.")


if __name__ == "__main__":
    create_missing_tables()
    run_migrations()
