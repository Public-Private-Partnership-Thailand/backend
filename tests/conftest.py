import os
import pytest
from sqlalchemy import create_engine, text
from sqlmodel import Session, SQLModel
from fastapi.testclient import TestClient
from typing import Generator

# ตั้งค่าให้ใช้ Test Database (เพื่อไม่ให้ไปกระทบดึงข้อมูลจริง)
TEST_DB_URL = "postgresql://postgres:REDACTED@localhost/ppp_test"
os.environ["DATABASE_URL"] = TEST_DB_URL

# สร้าง Database ppp_test แบบอัตโนมัติ (ถ้ายังไม่มี)
try:
    engine_postgres = create_engine("postgresql://postgres:REDACTED@localhost/postgres", isolation_level="AUTOCOMMIT")
    with engine_postgres.connect() as conn:
        res = conn.execute(text("SELECT 1 FROM pg_database WHERE datname='ppp_test'")).fetchone()
        if not res:
            conn.execute(text("CREATE DATABASE ppp_test"))
except Exception as e:
    print(f"Warning: Failed to create ppp_test database automatically: {e}")

# หลังจาก Override Environment `DATABASE_URL` แล้วจึงค่อย Import App
from oc4ids_datastore_api.main import app
from oc4ids_datastore_api.database import get_session

@pytest.fixture(name="session", scope="function")
def session_fixture() -> Generator[Session, None, None]:
    """สร้าง Session ใหม่พร้อมฐานข้อมูลจำลองสำหรับแต่ละ Test case"""
    engine = create_engine(TEST_DB_URL)
    
    # พักตารางก่อนเริ่มทำงานเพื่อให้เป็น Clean state
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """แทนที่ Database session ด้วย Test session ที่จำลองขึ้น"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
