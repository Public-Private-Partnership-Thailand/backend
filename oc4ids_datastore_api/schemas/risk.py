"""Risk Analysis Schemas (DTOs)"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class SectorMinistryHeatmapItem(BaseModel):
    """Risk count heatmap: sector vs risk category"""
    sector: str
    ministryList: List[Dict[str, Any]]


class RiskAnalysisResponse(BaseModel):
    """Complete risk analysis response"""
    heatmapRiskPhase: Dict[str, Any] = Field(
        ..., description="Risk pattern heatmap grouped by category and factor"
    )
    sectorMinistryHeatmap: List[SectorMinistryHeatmapItem] = Field(
        ..., description="Risk count per sector per risk category"
    )
