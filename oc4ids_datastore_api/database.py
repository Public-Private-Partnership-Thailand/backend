import os

from sqlmodel import Session, SQLModel, create_engine


engine = create_engine(
    os.environ.get("DATABASE_URL", "sqlite:///:memory:"),
    echo=False,
    pool_size=10,       # connections เปิดค้างไว้ตลอด
    max_overflow=20,    # connections ชั่วคราวเพิ่มได้อีกเมื่อ pool เต็ม
    pool_timeout=30,    # รอสูงสุด 30 วิถ้า pool เต็มหมด
    pool_pre_ping=True, # เช็คว่า connection ยังใช้ได้ก่อนส่งให้ request
)

def init_db():
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        print("Warning: Could not create tables on startup", e)

init_db()


def get_session():
    with Session(engine) as session:
        yield session

