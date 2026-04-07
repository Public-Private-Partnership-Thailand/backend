from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Body, Query, Path
from sqlmodel import Session
from typing import Dict, Any, List, Optional
import json
import pandas as pd
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

from oc4ids_datastore_api.database import get_session
from oc4ids_datastore_api.services import (
    get_all_projects,
    get_project_by_id,
    create_project_data,
    update_project_data,
    delete_project_data,
    get_reference_info,
    get_dashboard_summary,
    get_projects_comparison,
    get_risk_analysis
)
from oc4ids_datastore_api.dtos import (
    ProjectListResponse,
    ProjectDetailResponse,
    CreateProjectResponse,
    UpdateProjectResponse,
    DeleteProjectResponse,
    UploadResponse,
    DashboardSummaryResponse,
    ReferenceInfoResponse,
    RiskAnalysisResponse,
    ErrorDetail,
)

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────────────
#  GET /projects — รายการโครงการทั้งหมด (Paginated)
# ──────────────────────────────────────────────────────────────────────────────
@router.get(
    "/projects",
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
| `sector_id` | list[int] | กรองตามกลุ่มธุรกิจ (รองรับหลาย ID) |
| `ministry_id` | list[int] | กรองตามกระทรวง |
| `concession_form_id` | list[int] | กรองตามรูปแบบสัมปทาน |
| `contract_type_id` | list[int] | กรองตามประเภทสัญญา |
| `risk_category_id` | list[int] | กรองตามหมวดหมู่ความเสี่ยง |
| `risk_factor_id` | list[int] | กรองตามปัจจัยเสี่ยง |
| `year_from` | int | ปีเริ่มต้น |
| `year_to` | int | ปีสิ้นสุด |

### Response
คืนค่ารายการโครงการแบบสรุป พร้อม pagination metadata
""",
    response_description="รายการโครงการพร้อม pagination",
    responses={
        200: {"description": "สำเร็จ — ส่งคืนรายการโครงการ"},
    },
    tags=["Projects"],
)
def read_projects(
    page: int = Query(1, ge=1, description="หมายเลขหน้า (เริ่มจาก 1)"),
    page_size: int = Query(20, ge=1, le=100, description="จำนวนรายการต่อหน้า (1-100)"),
    title: Optional[str] = Query(None, description="ค้นหาตามชื่อโครงการ"),
    sector_id: Optional[List[int]] = Query(None, description="กรองตามกลุ่มธุรกิจ (sector ID)"),
    ministry_id: Optional[List[int]] = Query(None, description="กรองตามกระทรวง (ministry ID)"),
    concession_form_id: Optional[List[int]] = Query(None, description="กรองตามรูปแบบสัมปทาน"),
    contract_type_id: Optional[List[int]] = Query(None, description="กรองตามประเภทสัญญา"),
    risk_category_id: Optional[List[int]] = Query(None, description="กรองตามหมวดหมู่ความเสี่ยง"),
    risk_factor_id: Optional[List[int]] = Query(None, description="กรองตามปัจจัยเสี่ยง"),
    year_from: Optional[int] = Query(None, description="ปีเริ่มต้น (พ.ศ. หรือ ค.ศ.)"),
    year_to: Optional[int] = Query(None, description="ปีสิ้นสุด (พ.ศ. หรือ ค.ศ.)"),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    return get_all_projects(
        session, 
        page, 
        page_size,
        title=title,
        sector_id=sector_id,
        ministry_id=ministry_id,
        concession_form_id=concession_form_id,
        contract_type_id=contract_type_id,
        risk_category_id=risk_category_id,
        risk_factor_id=risk_factor_id,
        year_from=year_from,
        year_to=year_to
    )


# ──────────────────────────────────────────────────────────────────────────────
#  GET /projects/{project_id} — ดึงโครงการรายตัว
# ──────────────────────────────────────────────────────────────────────────────
@router.get(
    "/projects/{project_id}",
    response_model=ProjectDetailResponse,
    summary="ดึงข้อมูลโครงการตาม ID",
    description="""
ดึงรายละเอียดโครงการทั้งหมดในรูปแบบ **OC4IDS** (Open Contracting for Infrastructure Data Standard)

รวมถึง:
- ข้อมูลพื้นฐาน (title, description, status)
- หน่วยงานที่เกี่ยวข้อง (parties)
- งบประมาณ (budget) และแหล่งเงินทุน (finance)
- กระบวนการจัดซื้อจัดจ้าง (contracting processes)
- ที่ตั้งโครงการ (locations)
- ความเสี่ยง (risks) และการบรรเทา (mitigations)
- ตัวชี้วัด (metrics) และการคาดการณ์ (forecasts)
- ข้อมูลสังคมและสิ่งแวดล้อม
""",
    response_description="ข้อมูลโครงการเต็มรูปแบบ OC4IDS",
    responses={
        200: {"description": "สำเร็จ — ส่งคืนข้อมูลโครงการ"},
        404: {"description": "ไม่พบโครงการ", "model": ErrorDetail},
    },
    tags=["Projects"],
)
def read_project(
    project_id: str = Path(..., description="UUID ของโครงการ"),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    project = get_project_by_id(session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
    

# ──────────────────────────────────────────────────────────────────────────────
#  GET /compare — เปรียบเทียบโครงการ
# ──────────────────────────────────────────────────────────────────────────────
@router.get(
    "/compare",
    response_model=List[ProjectDetailResponse],
    summary="เปรียบเทียบโครงการหลายโครงการ",
    description="""
ดึงข้อมูลโครงการหลายโครงการพร้อมกันเพื่อนำไปเปรียบเทียบ

ส่ง `ids` เป็น query parameter หลายค่า เช่น:
```
GET /api/v1/compare?ids=uuid1&ids=uuid2&ids=uuid3
```

แต่ละโครงการจะถูกส่งคืนในรูปแบบ OC4IDS เต็มรูปแบบ
""",
    response_description="รายการโครงการแบบเต็มรูปแบบสำหรับเปรียบเทียบ",
    responses={
        200: {"description": "สำเร็จ — ส่งคืนรายการโครงการ"},
    },
    tags=["Projects"],
)
def compare_projects(
    ids: List[str] = Query(..., alias="ids", description="รายการ UUID ของโครงการที่ต้องการเปรียบเทียบ"),
    session: Session = Depends(get_session)
) -> List[Dict[str, Any]]:
    return get_projects_comparison(session, ids)


# ──────────────────────────────────────────────────────────────────────────────
#  POST /projects — สร้างโครงการใหม่
# ──────────────────────────────────────────────────────────────────────────────
@router.post(
    "/projects",
    response_model=CreateProjectResponse,
    status_code=200,
    summary="สร้างโครงการใหม่",
    description="""
สร้างโครงการใหม่จากข้อมูลในรูปแบบ OC4IDS JSON

### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `title` | string | ชื่อโครงการ |
| `type` | string | ประเภทโครงการ (e.g., `"construction"`) |
| `publicAuthority` | object | หน่วยงานรับผิดชอบ — ต้องมี `name` |
| `period` | object | ระยะเวลาโครงการ — ต้องมี `startDate`+`endDate` หรือ `durationInDays` |
| `parties` | array | ต้องมีอย่างน้อยหนึ่ง party ที่ `identifier.legalName` ไม่ว่าง (เอกชน) |

### Optional Fields
`sector`, `locations`, `budget`, `contractingProcesses`, `documents`, 
`risks`, `social`, `environment`, `benefits`, `forecasts`, `metrics`, ฯลฯ

ระบบจะ validate ข้อมูลก่อนบันทึก หากไม่ผ่านจะคืน HTTP 400
""",
    response_description="ข้อมูลโครงการที่สร้างสำเร็จ",
    responses={
        200: {"description": "สร้างโครงการสำเร็จ"},
        400: {"description": "ข้อมูลไม่ถูกต้อง / ขาด mandatory fields", "model": ErrorDetail},
    },
    tags=["Projects"],
)
def create_project(
    project_data: Dict[str, Any] = Body(
        ..., 
        openapi_examples={
            "minimal": {
                "summary": "ตัวอย่างขั้นต่ำ",
                "description": "ข้อมูลขั้นต่ำที่ต้องส่งเพื่อสร้างโครงการ",
                "value": {
                    "title": "โครงการทางด่วนสายใหม่",
                    "type": "construction",
                    "status": "implementation",
                    "publicAuthority": {
                        "name": "กรมทางหลวง"
                    },
                    "period": {
                        "startDate": "2024-01-01",
                        "endDate": "2029-12-31"
                    },
                    "parties": [
                        {
                            "name": "บริษัท ก่อสร้าง จำกัด",
                            "roles": ["privateParty"],
                            "identifier": {
                                "legalName": "บริษัท ก่อสร้าง จำกัด"
                            }
                        }
                    ]
                }
            }
        }
    ), 
    session: Session = Depends(get_session)
):
    return create_project_data(project_data, session)


# ──────────────────────────────────────────────────────────────────────────────
#  PUT /projects/{project_id} — อัปเดตโครงการ
# ──────────────────────────────────────────────────────────────────────────────
@router.put(
    "/projects/{project_id}",
    response_model=UpdateProjectResponse,
    summary="อัปเดตโครงการ",
    description="""
อัปเดตโครงการที่มีอยู่แล้วโดยการส่งข้อมูล OC4IDS JSON ใหม่ทั้งหมด

**กลไกการทำงาน:** ระบบจะลบข้อมูลเดิมและสร้างใหม่ทั้งหมดใน transaction เดียว
— หากเกิด error ระหว่างสร้างใหม่ ข้อมูลเดิมจะถูก rollback กลับมาปลอดภัย

⚠️ **สำคัญ:** ต้องส่งข้อมูลครบทุก field ที่ต้องการเก็บ (full replacement)
""",
    response_description="ข้อมูลโครงการที่อัปเดตสำเร็จ",
    responses={
        200: {"description": "อัปเดตสำเร็จ"},
        404: {"description": "ไม่พบโครงการ", "model": ErrorDetail},
        400: {"description": "ข้อมูลไม่ถูกต้อง", "model": ErrorDetail},
    },
    tags=["Projects"],
)
def update_project(
    project_id: str,
    project_data: Dict[str, Any] = Body(..., description="ข้อมูลโครงการใหม่ทั้งหมด (OC4IDS JSON)"),
    session: Session = Depends(get_session)
):
    return update_project_data(project_id, project_data, session)


# ──────────────────────────────────────────────────────────────────────────────
#  DELETE /projects/{project_id} — ลบโครงการ
# ──────────────────────────────────────────────────────────────────────────────
@router.delete(
    "/projects/{project_id}",
    response_model=DeleteProjectResponse,
    summary="ลบโครงการ (Soft Delete)",
    description="""
ลบโครงการออกจากระบบแบบ **Soft Delete** — ข้อมูลจะถูกทำเครื่องหมายว่าลบแล้ว (`deleted_at` timestamp) 
แต่ยังคงเก็บอยู่ในฐานข้อมูล

- โครงการที่ถูกลบจะ **ไม่แสดง** ในรายการและ Dashboard
- ข้อมูลยังคงอยู่ในฐานข้อมูล สามารถกู้คืนได้ในอนาคต
""",
    response_description="ข้อความยืนยันการลบ",
    responses={
        200: {"description": "ลบสำเร็จ"},
        404: {"description": "ไม่พบโครงการ", "model": ErrorDetail},
    },
    tags=["Projects"],
)
def delete_project(
    project_id: str, 
    session: Session = Depends(get_session)
):
    return delete_project_data(project_id, session)


# ──────────────────────────────────────────────────────────────────────────────
#  POST /upload — อัปโหลดไฟล์
# ──────────────────────────────────────────────────────────────────────────────
@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="อัปโหลดไฟล์โครงการ (JSON/CSV)",
    description="""
อัปโหลดไฟล์ข้อมูลโครงการ รองรับ 2 รูปแบบ:

### JSON File
- **Single project:** ไฟล์ JSON ที่มีข้อมูลโครงการ 1 โครงการ
- **OC4IDS Package:** ไฟล์ JSON ที่มี key `"projects"` เป็น array ของโครงการหลายรายการ
  — ระบบจะ import ทีละโครงการ พร้อมรายงานผลแต่ละรายการ

### CSV File
- คืนค่า parsed data เป็น JSON (ยังไม่บันทึกลง database)

### Response Status
| Status | หมายถึง |
|--------|---------|
| `success` | ทุกโครงการ import สำเร็จ |
| `partial_success` | บางโครงการ import สำเร็จ บางรายการ error |
| `error` | ทุกโครงการ import ไม่สำเร็จ |
""",
    response_description="ผลการ import ไฟล์",
    responses={
        200: {"description": "อัปโหลดสำเร็จ"},
        400: {"description": "ไฟล์ไม่ถูกต้อง หรือ format ไม่รองรับ", "model": ErrorDetail},
    },
    tags=["Upload"],
)
async def upload_file(
    file: UploadFile = File(..., description="ไฟล์ JSON หรือ CSV ที่ต้องการ import"),
    session: Session = Depends(get_session)
):
    filename = file.filename
    ext = filename.split(".")[-1].lower()

    try:
        if ext == "json":
            contents = await file.read()
            data = json.loads(contents)
            
            # Handle OC4IDS Package format (has 'projects' list)
            if "projects" in data and isinstance(data["projects"], list):
                results = []
                for p_data in data["projects"]:
                    # Basic error handling for each project
                    try:
                        res = create_project_data(p_data, session)
                        results.append(res)
                    except Exception as e:
                        results.append({"error": str(e), "project_title": p_data.get("title")})
                has_errors = any("error" in r for r in results)
                status = "partial_success" if has_errors else "success"
                
                # If everything failed, might want "error"
                if has_errors and all("error" in r for r in results):
                    status = "error"
                    
                return {"status": status, "results": results}
            
            # Helper for single project file
            return create_project_data(data, session)

        elif ext == "csv":
            contents = await file.read()
            df = pd.read_csv(BytesIO(contents))
            return {"status": "success", "data": df.to_dict(orient="records")}

        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────────
#  GET /summary — Dashboard Summary
# ──────────────────────────────────────────────────────────────────────────────
@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="ดึงข้อมูลสรุปสำหรับ Dashboard",
    description="""
ดึงข้อมูลสถิติรวมสำหรับหน้า Dashboard พร้อมรองรับ filter

### ข้อมูลที่ส่งคืน
- **summary** — สถิติรวม (จำนวนโครงการ, มูลค่ารวม, ผู้รับเหมา)
- **ministryStats** — Top 10 กระทรวงตามจำนวนโครงการ
- **ministryInvestments** — Top 10 กระทรวงตามมูลค่าลงทุน
- **latestProjects** — 5 โครงการล่าสุด
- **projectScales** — การกระจายตามขนาดโครงการ (เล็ก/กลาง/ใหญ่)
- **investmentByYear** — มูลค่าลงทุนรายปี
- **businessGroupStats** — สถิติตามกลุ่มธุรกิจ
- **heatmapRisk** — ข้อมูล heatmap ความเสี่ยง

### Filter Parameters
ส่งเป็นค่าเดี่ยว (comma-separated IDs) เช่น `sector=1,2,3`
""",
    response_description="ข้อมูลสรุปสำหรับ Dashboard",
    responses={
        200: {"description": "สำเร็จ"},
    },
    tags=["Dashboard"],
)
def get_summary(
    search: Optional[str] = Query(None, description="ค้นหาตามชื่อโครงการ"),
    sector: Optional[str] = Query(None, description="กรองตาม sector (comma-separated IDs)"), 
    sector_id: Optional[str] = Query(None, alias="sector", description="(alias) กรองตาม sector"), 
    businessGroup: Optional[str] = Query(None, description="กรองตามกลุ่มธุรกิจ (comma-separated IDs)"),
    ministry: Optional[str] = Query(None, description="กรองตามกระทรวง (comma-separated IDs)"),
    agency: Optional[str] = Query(None, description="กรองตามหน่วยงาน (comma-separated IDs)"),
    concessionForm: Optional[str] = Query(None, description="กรองตามรูปแบบสัมปทาน"), 
    contractType: Optional[str] = Query(None, description="กรองตามประเภทสัญญา"),
    risk_category_id: Optional[str] = Query(None, description="กรองตามหมวดหมู่ความเสี่ยง"),
    risk_factor_id: Optional[str] = Query(None, description="กรองตามปัจจัยเสี่ยง"),
    startDate: Optional[str] = Query(None, description="วันที่เริ่มต้น (ISO 8601)"),
    endDate: Optional[str] = Query(None, description="วันที่สิ้นสุด (ISO 8601)"),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    
    # Helper to parse comma-separated IDs
    def parse_ids(value: Optional[str]) -> Optional[List[int]]:
        if not value:
            return None
        return [int(x) for x in value.split(',') if x.strip().isdigit()]
    
    # Parse dates
    y_from = None
    y_to = None
    if startDate:
         try:
             y_from = int(startDate[:4])
         except: pass
    if endDate:
         try:
             y_to = int(endDate[:4])
         except: pass

    # Sector mapping: businessGroup or sector param
    # useSummary sends 'businessGroup' -> maps to sector IDs
    s_ids = parse_ids(businessGroup) or parse_ids(sector_id) or parse_ids(sector)
    
    logger.info(f"Dashboard Summary Request: search={search}, sector_ids={s_ids}, ministry={ministry}")

    result = get_dashboard_summary(
        session,
        search=search,
        sector_id=s_ids,
        ministry_id=parse_ids(ministry),
        agency_id=parse_ids(agency),
        concession_form_id=parse_ids(concessionForm),
        contract_type_id=parse_ids(contractType),
        risk_category_id=parse_ids(risk_category_id),
        risk_factor_id=parse_ids(risk_factor_id),
        year_from=y_from,
        year_to=y_to
    )
    
    logger.info(f"Dashboard Summary Result: Total Projects = {result.get('summary', {}).get('totalProjects')}")
    return result


# ──────────────────────────────────────────────────────────────────────────────
#  GET /info — Reference Data (Dropdowns)
# ──────────────────────────────────────────────────────────────────────────────
@router.get(
    "/info",
    response_model=ReferenceInfoResponse,
    summary="ดึงข้อมูลอ้างอิงสำหรับ dropdown",
    description="""
ดึงข้อมูล reference/lookup ทั้งหมดสำหรับใช้แสดงใน dropdown, filter, และ form ต่าง ๆ

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

แต่ละ item จะมี `id` (ใช้สำหรับ filter) และ `value` (ใช้แสดงผล)
""",
    response_description="ข้อมูล reference ทั้งหมด",
    responses={
        200: {"description": "สำเร็จ"},
    },
    tags=["Reference Data"],
)
def get_info(
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    return get_reference_info(session)


# ──────────────────────────────────────────────────────────────────────────────
#  GET /risk — Risk Analysis
# ──────────────────────────────────────────────────────────────────────────────
@router.get(
    "/risk",
    response_model=RiskAnalysisResponse,
    summary="ดึงข้อมูลวิเคราะห์ความเสี่ยง",
    description="""
ดึงข้อมูลวิเคราะห์ความเสี่ยงสำหรับหน้า Risk Analysis

### ข้อมูลที่ส่งคืน
| Key | Description |
|-----|-------------|
| `heatmapRiskPhase` | Risk Pattern จัดกลุ่มตาม Category Code และ Factor Name พร้อม Phase และ Source |
| `sectorMinistryHeatmap` | จำนวนความเสี่ยงแยกตาม Sector และ Risk Category |
""",
    response_description="ข้อมูลวิเคราะห์ความเสี่ยงทั้งหมด",
    responses={
        200: {"description": "สำเร็จ"},
    },
    tags=["Risk Analysis"],
)
def get_risk(
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    return get_risk_analysis(session)


# ──────────────────────────────────────────────────────────────────────────────
#  GET /risk-sources/{rs_id}/reference — ดาวน์โหลดไฟล์ Reference ของ Risk Source
# ──────────────────────────────────────────────────────────────────────────────
@router.get(
    "/risk-sources/{rs_id}/reference",
    summary="ดาวน์โหลดไฟล์ reference ของ Risk Source",
    description="""
ดาวน์โหลดไฟล์เอกสารอ้างอิง (reference) ของแหล่งที่มาของความเสี่ยง (Risk Source) ตาม ID

หากไม่พบไฟล์หรือ Risk Source ไม่มี reference จะคืน HTTP 404
""",
    response_description="ไฟล์ reference สำหรับดาวน์โหลด",
    responses={
        200: {"description": "สำเร็จ — ส่งไฟล์สำหรับดาวน์โหลด"},
        404: {"description": "ไม่พบ Risk Source หรือไม่มีไฟล์ reference", "model": ErrorDetail},
    },
    tags=["Reference Data"],
)
def download_risk_source_reference(
    rs_id: int = Path(..., description="ID ของ Risk Source"),
    session: Session = Depends(get_session)
):
    import os
    from fastapi.responses import FileResponse
    from oc4ids_datastore_api.models import RiskSource

    risk_source = session.get(RiskSource, rs_id)
    if not risk_source:
        raise HTTPException(status_code=404, detail=f"Risk Source ID {rs_id} not found")

    if not risk_source.reference_file:
        raise HTTPException(status_code=404, detail=f"Risk Source ID {rs_id} has no reference file")

    # ไฟล์เก็บอยู่ใน static/risk_source_references/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "static", "risk_source_references", risk_source.reference_file)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail=f"Reference file not found on server: {risk_source.reference_file}")

    return FileResponse(
        path=file_path,
        filename=risk_source.reference_file,
        media_type="application/octet-stream",
    )

