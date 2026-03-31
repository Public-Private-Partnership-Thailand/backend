from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import logging
import os

# Try loading .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from oc4ids_datastore_api.controllers import router
from oc4ids_datastore_api.exceptions import validation_exception_handler, global_exception_handler
from oc4ids_datastore_api.middleware import PerformanceMiddleware

# ──────────────────────────────────────────────────────────────────────────────
#  OpenAPI Tags Metadata
# ──────────────────────────────────────────────────────────────────────────────
tags_metadata = [
    {
        "name": "Projects",
        "description": "จัดการข้อมูลโครงการ PPP — สร้าง ดู แก้ไข ลบ และเปรียบเทียบโครงการ (CRUD + Compare)",
    },
    {
        "name": "Dashboard",
        "description": "ข้อมูลสรุปสถิติสำหรับหน้า Dashboard — จำนวนโครงการ มูลค่ารวม สถิติกระทรวง ฯลฯ",
    },
    {
        "name": "Upload",
        "description": "อัปโหลดไฟล์ข้อมูลโครงการ — รองรับ JSON (single/batch) และ CSV",
    },
    {
        "name": "Reference Data",
        "description": "ข้อมูลอ้างอิง (lookup) สำหรับ dropdown และ filter — กลุ่มธุรกิจ กระทรวง ประเภทสัญญา ความเสี่ยง ฯลฯ",
    },
]


# ──────────────────────────────────────────────────────────────────────────────
#  App Initialization
# ──────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="PPP Intelligence Platform for Thailand Datastore API ",
    version="1.0.0",
    description="""
## OC4IDS Datastore API


API สำหรับจัดการข้อมูลโครงการร่วมลงทุนระหว่างรัฐและเอกชน (PPP) 
ตามมาตรฐาน **OC4IDS** (Open Contracting for Infrastructure Data Standard)

###  ความสามารถหลัก

| Feature | Description |
|---------|-------------|
|  **Dashboard** | ดึงสถิติรวมสำหรับ Dashboard |
|  **Projects CRUD** | สร้าง ดู แก้ไข ลบโครงการ |
|  **File Upload** | Import ข้อมูลจาก JSON/CSV |
|  **Search & Filter** | ค้นหาและกรองตามหลายเงื่อนไข |
|  **Reference Data** | ข้อมูลอ้างอิงสำหรับ dropdown |
|  **Compare** | เปรียบเทียบโครงการหลายรายการ |

###  Base URL
```
/api/v1
```

###  Data Standard
[OC4IDS Documentation](https://standard.open-contracting.org/infrastructure/latest/en/)
""",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "OC4IDS Datastore Team",
    },
    license_info={
        "name": "MIT License",
    },
)

# Register Exception Handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Add Middleware
app.add_middleware(PerformanceMiddleware)


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS configuration
origins = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Router with Versioning
app.include_router(router, prefix="/api/v1")
