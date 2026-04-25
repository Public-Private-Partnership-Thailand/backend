"""Upload Router — File-based project import endpoints."""

import json
import pandas as pd
from io import BytesIO
import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session

from oc4ids_datastore_api.database import get_session
from oc4ids_datastore_api.services.project_service import create_project_data
from oc4ids_datastore_api.schemas.project import UploadResponse
from oc4ids_datastore_api.schemas.common import ErrorDetail

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="อัปโหลดไฟล์โครงการ (JSON/CSV)",
    description="""
อัปโหลดไฟล์ข้อมูลโครงการ รองรับ 2 รูปแบบ:

### JSON File
- **Single project:** ไฟล์ JSON ที่มีข้อมูลโครงการ 1 โครงการ
- **OC4IDS Package:** ไฟล์ JSON ที่มี key `"projects"` เป็น array ของโครงการหลายรายการ

### CSV File
- คืนค่า parsed data เป็น JSON (ยังไม่บันทึกลง database)

### Response Status
| Status | หมายถึง |
|--------|---------| 
| `success` | ทุกโครงการ import สำเร็จ |
| `partial_success` | บางโครงการ import สำเร็จ |
| `error` | ทุกโครงการ import ไม่สำเร็จ |
""",
    response_description="ผลการ import ไฟล์",
    responses={
        200: {"description": "อัปโหลดสำเร็จ"},
        400: {"description": "ไฟล์ไม่ถูกต้อง หรือ format ไม่รองรับ", "model": ErrorDetail},
    },
)
async def upload_file(
    file: UploadFile = File(..., description="ไฟล์ JSON หรือ CSV ที่ต้องการ import"),
    session: Session = Depends(get_session),
):
    filename = file.filename
    ext = filename.split(".")[-1].lower()

    try:
        if ext == "json":
            contents = await file.read()
            data = json.loads(contents)

            # Handle OC4IDS Package format
            if "projects" in data and isinstance(data["projects"], list):
                results = []
                for p_data in data["projects"]:
                    try:
                        res = create_project_data(p_data, session)
                        results.append(res)
                    except Exception as e:
                        results.append({"error": str(e), "project_title": p_data.get("title")})
                has_errors = any("error" in r for r in results)
                all_errors = has_errors and all("error" in r for r in results)
                status = "error" if all_errors else ("partial_success" if has_errors else "success")
                return {"status": status, "results": results}

            # Single project
            return create_project_data(data, session)

        elif ext == "csv":
            contents = await file.read()
            df = pd.read_csv(BytesIO(contents))
            return {"status": "success", "data": df.to_dict(orient="records")}

        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
