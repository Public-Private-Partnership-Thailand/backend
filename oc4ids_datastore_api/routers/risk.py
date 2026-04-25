"""Risk Analysis Router — Risk heatmap endpoints."""

from typing import Any, Dict
import logging

from fastapi import APIRouter, Depends
from sqlmodel import Session

from oc4ids_datastore_api.database import get_session
from oc4ids_datastore_api.services.risk_service import get_risk_analysis
from oc4ids_datastore_api.schemas.risk import RiskAnalysisResponse

logger = logging.getLogger(__name__)
router = APIRouter()


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
    responses={200: {"description": "สำเร็จ"}},
)
def get_risk(session: Session = Depends(get_session)) -> Dict[str, Any]:
    return get_risk_analysis(session)
