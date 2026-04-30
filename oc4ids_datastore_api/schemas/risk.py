"""Risk Analysis Schemas (DTOs)"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SectorMinistryHeatmapItem(BaseModel):
    """Risk count heatmap: sector vs risk category"""
    sector: str
    ministryList: List[Dict[str, Any]]


class RiskProjectItem(BaseModel):
    """Project risk details for sector-grouped data"""
    projectId: str
    projectName: str
    problem: str
    riskImpact: Optional[str] = None
    riskResponse: Optional[str] = None
    phase: Optional[str] = None
    riskCategoryId: int
    riskFactorId: int


class RiskSectorWithProjectItem(BaseModel):
    """Projects grouped by sector with risk info"""
    sector: str
    riskCount: int
    projects: List[RiskProjectItem]


class RiskAnalysisResponse(BaseModel):
    """Complete risk analysis response"""
    heatmapRiskPhase: Dict[str, Any] = Field(
        ..., description="Risk pattern heatmap grouped by category and factor"
    )
    sectorMinistryHeatmap: List[SectorMinistryHeatmapItem] = Field(
        ..., description="Risk count per sector per risk category"
    )
    riskSectorWithProject: List[RiskSectorWithProjectItem] = Field(
        default_factory=list, description="Projects grouped by sector with risk info"
    )
