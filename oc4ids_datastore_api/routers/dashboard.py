"""Dashboard Router — Summary statistics for the dashboard."""

from typing import Any, Dict, List, Optional
import logging

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from oc4ids_datastore_api.database import get_session
from oc4ids_datastore_api.services.dashboard_service import get_dashboard_summary
from oc4ids_datastore_api.schemas.dashboard import DashboardSummaryResponse

logger = logging.getLogger(__name__)
router = APIRouter()


def _parse_ids(value: Optional[str]) -> Optional[List[int]]:
    """Parse a comma-separated string of integers."""
    if not value:
        return None
    return [int(x) for x in value.split(",") if x.strip().isdigit()]


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
- **projectScales** — การกระจายตามขนาดโครงการ
- **investmentByYear** — มูลค่าลงทุนรายปี
- **businessGroupStats** — สถิติตามกลุ่มธุรกิจ
""",
    response_description="ข้อมูลสรุปสำหรับ Dashboard",
    responses={200: {"description": "สำเร็จ"}},
)
def get_summary(
    search: Optional[str] = Query(None, description="ค้นหาตามชื่อโครงการ"),
    sector: Optional[str] = Query(None, description="กรองตาม sector (comma-separated IDs)"),
    businessGroup: Optional[str] = Query(None, description="กรองตามกลุ่มธุรกิจ (comma-separated IDs)"),
    ministry: Optional[str] = Query(None, description="กรองตามกระทรวง (comma-separated IDs)"),
    agency: Optional[str] = Query(None, description="กรองตามหน่วยงาน (comma-separated IDs)"),
    concessionForm: Optional[str] = Query(None, description="กรองตามรูปแบบสัมปทาน"),
    contractType: Optional[str] = Query(None, description="กรองตามประเภทสัญญา"),
    risk_category_id: Optional[str] = Query(None, description="กรองตามหมวดหมู่ความเสี่ยง"),
    risk_factor_id: Optional[str] = Query(None, description="กรองตามปัจจัยเสี่ยง"),
    startDate: Optional[str] = Query(None, description="วันที่เริ่มต้น (ISO 8601)"),
    endDate: Optional[str] = Query(None, description="วันที่สิ้นสุด (ISO 8601)"),
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    y_from = None
    y_to = None
    if startDate:
        try:
            y_from = int(startDate[:4])
        except Exception:
            pass
    if endDate:
        try:
            y_to = int(endDate[:4])
        except Exception:
            pass

    s_ids = _parse_ids(businessGroup) or _parse_ids(sector)
    logger.info(f"Dashboard Summary Request: search={search}, sector_ids={s_ids}, ministry={ministry}")

    result = get_dashboard_summary(
        session,
        search=search,
        sector_id=s_ids,
        ministry_id=_parse_ids(ministry),
        agency_id=_parse_ids(agency),
        concession_form_id=_parse_ids(concessionForm),
        contract_type_id=_parse_ids(contractType),
        risk_category_id=_parse_ids(risk_category_id),
        risk_factor_id=_parse_ids(risk_factor_id),
        year_from=y_from,
        year_to=y_to,
    )
    logger.info(f"Dashboard Summary Result: Total Projects = {result.get('summary', {}).get('totalProjects')}")
    return result
