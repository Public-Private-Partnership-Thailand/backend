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

    # 2026-05-09: add indexes on hot-filtered FK / state columns. PostgreSQL
    # does not auto-index foreign key columns, and every project query filters
    # by deleted_at IS NULL, so on a non-trivial dataset these become required.
    "CREATE INDEX IF NOT EXISTS ix_projects_deleted_at ON projects (deleted_at)",
    "CREATE INDEX IF NOT EXISTS ix_projects_public_authority_id ON projects (public_authority_id)",
    "CREATE INDEX IF NOT EXISTS ix_projects_project_type_id ON projects (project_type_id)",
    "CREATE INDEX IF NOT EXISTS ix_project_periods_project_id ON project_periods (project_id)",
    "CREATE INDEX IF NOT EXISTS ix_project_periods_period_type ON project_periods (period_type)",
    "CREATE INDEX IF NOT EXISTS ix_project_parties_project_id ON project_parties (project_id)",
    "CREATE INDEX IF NOT EXISTS ix_project_parties_identifier_legal_name_id ON project_parties (identifier_legal_name_id)",
    "CREATE INDEX IF NOT EXISTS ix_party_additional_identifiers_party_id ON party_additional_identifiers (party_id)",
    "CREATE INDEX IF NOT EXISTS ix_party_additional_identifiers_legal_name_id ON party_additional_identifiers (legal_name_id)",
    "CREATE INDEX IF NOT EXISTS ix_agency_ministry_id ON agency (ministry_id)",
    "CREATE INDEX IF NOT EXISTS ix_project_sector_sector_id ON project_sector (sector_id)",
    "CREATE INDEX IF NOT EXISTS ix_project_additional_classifications_classification_id ON project_additional_classifications (classification_id)",
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
