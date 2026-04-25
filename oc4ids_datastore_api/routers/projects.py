"""Projects Router — CRUD endpoints for Project resource."""

from typing import Any, Dict, List, Optional
import json
import pandas as pd
from io import BytesIO
import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body, Query, Path
from sqlmodel import Session

from oc4ids_datastore_api.database import get_session
from oc4ids_datastore_api.services.project_service import (
    get_all_projects,
    get_project_by_id,
    get_projects_comparison,
    create_project_data,
    update_project_data,
    delete_project_data,
)
from oc4ids_datastore_api.schemas.project import (
    ProjectListResponse,
    ProjectDetailResponse,
    CreateProjectResponse,
    UpdateProjectResponse,
    DeleteProjectResponse,
)
from oc4ids_datastore_api.schemas.common import ErrorDetail

logger = logging.getLogger(__name__)
router = APIRouter()


# ──────────────────────────────────────────────────────────────────────────────
#  GET /projects — รายการโครงการทั้งหมด (Paginated)
# ──────────────────────────────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=ProjectListResponse,
    summary="ดึงรายการโครงการทั้งหมด",
    description="""
ดึงรายการโครงการแบบแบ่งหน้า (pagination) พร้อมรองรับ filter หลายรูปแบบ

### Query Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | หน้าที่ต้องการ (default: 1) |
| `page_size` | int | จำนวนรายการต่อหน้า (default: 20) |
| `title` | str | ค้นหาตามชื่อโครงการ |
| `sector_id` | list[int] | กรองตามกลุ่มธุรกิจ |
| `ministry_id` | list[int] | กรองตามกระทรวง |
| `concession_form_id` | list[int] | กรองตามรูปแบบสัมปทาน |
| `contract_type_id` | list[int] | กรองตามประเภทสัญญา |
| `risk_category_id` | list[int] | กรองตามหมวดหมู่ความเสี่ยง |
| `risk_factor_id` | list[int] | กรองตามปัจจัยเสี่ยง |
| `year_from` | int | ปีเริ่มต้น |
| `year_to` | int | ปีสิ้นสุด |
""",
    response_description="รายการโครงการพร้อม pagination",
    responses={200: {"description": "สำเร็จ — ส่งคืนรายการโครงการ"}},
)
def read_projects(
    page: int = Query(1, ge=1, description="หมายเลขหน้า (เริ่มจาก 1)"),
    page_size: int = Query(20, ge=1, le=100, description="จำนวนรายการต่อหน้า (1-100)"),
    title: Optional[str] = Query(None, description="ค้นหาตามชื่อโครงการ"),
    sector_id: Optional[List[int]] = Query(None, description="กรองตามกลุ่มธุรกิจ"),
    ministry_id: Optional[List[int]] = Query(None, description="กรองตามกระทรวง"),
    concession_form_id: Optional[List[int]] = Query(None, description="กรองตามรูปแบบสัมปทาน"),
    contract_type_id: Optional[List[int]] = Query(None, description="กรองตามประเภทสัญญา"),
    risk_category_id: Optional[List[int]] = Query(None, description="กรองตามหมวดหมู่ความเสี่ยง"),
    risk_factor_id: Optional[List[int]] = Query(None, description="กรองตามปัจจัยเสี่ยง"),
    year_from: Optional[int] = Query(None, description="ปีเริ่มต้น"),
    year_to: Optional[int] = Query(None, description="ปีสิ้นสุด"),
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    return get_all_projects(
        session, page, page_size,
        title=title, sector_id=sector_id, ministry_id=ministry_id,
        concession_form_id=concession_form_id, contract_type_id=contract_type_id,
        risk_category_id=risk_category_id, risk_factor_id=risk_factor_id,
        year_from=year_from, year_to=year_to,
    )


# ──────────────────────────────────────────────────────────────────────────────
#  GET /compare — เปรียบเทียบโครงการ
# ──────────────────────────────────────────────────────────────────────────────
@router.get(
    "/compare",
    response_model=List[ProjectDetailResponse],
    summary="เปรียบเทียบโครงการหลายโครงการ",
    description="ดึงข้อมูลโครงการหลายโครงการสำหรับเปรียบเทียบ",
    response_description="รายการโครงการแบบเต็มรูปแบบสำหรับเปรียบเทียบ",
)
def compare_projects(
    ids: List[str] = Query(..., alias="ids", description="รายการ UUID ของโครงการ"),
    session: Session = Depends(get_session),
) -> List[Dict[str, Any]]:
    return get_projects_comparison(session, ids)


# ──────────────────────────────────────────────────────────────────────────────
#  GET /projects/{project_id} — ดึงโครงการรายตัว
# ──────────────────────────────────────────────────────────────────────────────
@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    summary="ดึงข้อมูลโครงการตาม ID",
    description="ดึงรายละเอียดโครงการทั้งหมดในรูปแบบ **OC4IDS**",
    response_description="ข้อมูลโครงการเต็มรูปแบบ OC4IDS",
    responses={
        200: {"description": "สำเร็จ — ส่งคืนข้อมูลโครงการ"},
        404: {"description": "ไม่พบโครงการ", "model": ErrorDetail},
    },
)
def read_project(
    project_id: str = Path(..., description="UUID ของโครงการ"),
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    project = get_project_by_id(session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# ──────────────────────────────────────────────────────────────────────────────
#  POST /projects — สร้างโครงการใหม่
# ──────────────────────────────────────────────────────────────────────────────
@router.post(
    "/",
    response_model=CreateProjectResponse,
    status_code=200,
    summary="สร้างโครงการใหม่",
    description="สร้างโครงการใหม่จากข้อมูลในรูปแบบ OC4IDS JSON",
    response_description="ข้อมูลโครงการที่สร้างสำเร็จ",
    responses={
        200: {"description": "สร้างโครงการสำเร็จ"},
        400: {"description": "ข้อมูลไม่ถูกต้อง", "model": ErrorDetail},
    },
)
def create_project(
    project_data: Dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
):
    return create_project_data(project_data, session)


# ──────────────────────────────────────────────────────────────────────────────
#  PUT /projects/{project_id} — อัปเดตโครงการ
# ──────────────────────────────────────────────────────────────────────────────
@router.put(
    "/{project_id}",
    response_model=UpdateProjectResponse,
    summary="อัปเดตโครงการ",
    description="อัปเดตโครงการที่มีอยู่โดยส่งข้อมูล OC4IDS JSON ใหม่ทั้งหมด",
    response_description="ข้อมูลโครงการที่อัปเดตสำเร็จ",
    responses={
        200: {"description": "อัปเดตสำเร็จ"},
        404: {"description": "ไม่พบโครงการ", "model": ErrorDetail},
        400: {"description": "ข้อมูลไม่ถูกต้อง", "model": ErrorDetail},
    },
)
def update_project(
    project_id: str,
    project_data: Dict[str, Any] = Body(..., description="ข้อมูลโครงการใหม่ทั้งหมด (OC4IDS JSON)"),
    session: Session = Depends(get_session),
):
    return update_project_data(project_id, project_data, session)


# ──────────────────────────────────────────────────────────────────────────────
#  DELETE /projects/{project_id} — ลบโครงการ
# ──────────────────────────────────────────────────────────────────────────────
@router.delete(
    "/{project_id}",
    response_model=DeleteProjectResponse,
    summary="ลบโครงการ (Soft Delete)",
    description="ลบโครงการออกจากระบบแบบ Soft Delete",
    response_description="ข้อความยืนยันการลบ",
    responses={
        200: {"description": "ลบสำเร็จ"},
        404: {"description": "ไม่พบโครงการ", "model": ErrorDetail},
    },
)
def delete_project(
    project_id: str,
    session: Session = Depends(get_session),
):
    return delete_project_data(project_id, session)
