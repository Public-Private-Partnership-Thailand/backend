"""Reference Data Router — Dropdown/lookup data endpoints."""

import os
from typing import Any, Dict
import logging

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import FileResponse
from sqlmodel import Session

from oc4ids_datastore_api.database import get_session
from oc4ids_datastore_api.services.reference_service import get_reference_info
from oc4ids_datastore_api.schemas.reference import ReferenceInfoResponse
from oc4ids_datastore_api.schemas.common import ErrorDetail

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/info",
    response_model=ReferenceInfoResponse,
    summary="ดึงข้อมูลอ้างอิงสำหรับ dropdown",
    description="""
ดึงข้อมูล reference/lookup ทั้งหมดสำหรับใช้แสดงใน dropdown, filter, และ form

### ข้อมูลที่ส่งคืน
| Key | Description |
|-----|-------------|
| `sector` | กลุ่มธุรกิจ / ภาคส่วน |
| `ministry` | กระทรวง |
| `projectType` | ประเภทโครงการ |
| `concessionForm` | รูปแบบสัมปทาน |
| `contractType` | ประเภทสัญญา |
| `riskCategory` | หมวดหมู่ความเสี่ยง |
| `riskPhase` | ระยะของความเสี่ยง |
| `riskFactor` | ปัจจัยเสี่ยง |
""",
    response_description="ข้อมูล reference ทั้งหมด",
    responses={200: {"description": "สำเร็จ"}},
)
def get_info(session: Session = Depends(get_session)) -> Dict[str, Any]:
    return get_reference_info(session)


@router.get(
    "/risk-sources/{rs_id}/reference",
    summary="ดาวน์โหลดไฟล์ reference ของ Risk Source",
    description="ดาวน์โหลดไฟล์เอกสารอ้างอิง (reference) ของแหล่งที่มาของความเสี่ยง (Risk Source) ตาม ID",
    response_description="ไฟล์ reference สำหรับดาวน์โหลด",
    responses={
        200: {"description": "สำเร็จ — ส่งไฟล์สำหรับดาวน์โหลด"},
        404: {"description": "ไม่พบ Risk Source หรือไม่มีไฟล์ reference", "model": ErrorDetail},
    },
)
def download_risk_source_reference(
    rs_id: int = Path(..., description="ID ของ Risk Source"),
    session: Session = Depends(get_session),
):
    from oc4ids_datastore_api.models import RiskSource

    risk_source = session.get(RiskSource, rs_id)
    if not risk_source:
        raise HTTPException(status_code=404, detail=f"Risk Source ID {rs_id} not found")
    if not risk_source.reference_file:
        raise HTTPException(status_code=404, detail=f"Risk Source ID {rs_id} has no reference file")

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_dir, "static", "risk_source_references", risk_source.reference_file)

    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"Reference file not found on server: {risk_source.reference_file}",
        )

    return FileResponse(
        path=file_path,
        filename=risk_source.reference_file,
        media_type="application/octet-stream",
    )
