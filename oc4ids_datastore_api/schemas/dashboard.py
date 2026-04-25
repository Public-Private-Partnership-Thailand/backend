"""Dashboard Schemas (DTOs)"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SummaryStatsResponse(BaseModel):
    """High-level aggregated statistics"""
    totalProjects: int = Field(..., description="Total number of projects", examples=[150])
    uniqueContractors: int = Field(..., description="Number of unique contractors", examples=[42])
    uniquePublicAuthority: int = Field(..., description="Number of unique public authorities", examples=[10])
    totalInvestment: str = Field(..., description="Total investment (Thai formatted)", examples=["1,500,000,000.00"])
    maxBudget: str = Field(..., description="Maximum single project budget (Thai formatted)")
    inprogressProjects: int = Field(..., description="Number of projects currently in progress")


class MinistryStatResponse(BaseModel):
    """Ministry-level statistics"""
    ministry: str = Field(..., description="Ministry name")
    projectCount: int = Field(..., description="Number of projects under this ministry")
    totalInvestment: float = Field(..., description="Total investment amount")
    rank: int = Field(..., description="Ranking position")


class LatestProjectResponse(BaseModel):
    """Summarised project for dashboard"""
    id: str = Field(..., description="Project UUID")
    title: Optional[str] = None
    ministry: Optional[List[str]] = None
    public_authority: Optional[str] = None
    budget: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    type: Optional[str] = None
    updated: Optional[str] = None


class OtherMinistriesResponse(BaseModel):
    """Aggregated data for ministries outside the top 10"""
    projectCount: int = 0
    totalInvestment: float = 0


class ProjectScaleResponse(BaseModel):
    """Project scale distribution"""
    small: Optional[int] = Field(None, description="Projects with budget < threshold")
    medium: Optional[int] = Field(None, description="Projects with budget in mid range")
    big: Optional[int] = Field(None, description="Projects with budget > threshold")


class InvestmentByYearResponse(BaseModel):
    """Yearly investment aggregation"""
    year: int = Field(..., description="Calendar year")
    investment: float = Field(..., description="Total investment in that year")
    projectCount: int = Field(..., description="Number of projects in that year")


class BusinessGroupStatResponse(BaseModel):
    """Statistics grouped by business sector"""
    groupName: str
    displayName: str
    total: Optional[Dict[str, Any]] = None
    small: Optional[Dict[str, Any]] = None
    medium: Optional[Dict[str, Any]] = None
    big: Optional[Dict[str, Any]] = None


class PublicAuthorityCountResponse(BaseModel):
    """Summary of projects per public authority"""
    publicAuthorityName: str
    projectCount: int


class SectorBubbleResponse(BaseModel):
    """Summary of project metrics per sector for bubble chart"""
    sector: str
    projectCount: int
    totalValue: float
    authorityCount: int


class DashboardSummaryResponse(BaseModel):
    """Complete dashboard summary response"""
    summary: SummaryStatsResponse
    ministryStats: List[MinistryStatResponse] = Field(..., description="Top ministries by project count")
    latestProjects: List[LatestProjectResponse] = Field(..., description="Most recent projects")
    otherMinistries: OtherMinistriesResponse = Field(..., description="Aggregated stats for non-top ministries")
    ministryInvestments: List[MinistryStatResponse] = Field(..., description="Top ministries by investment")
    otherMinistriesInvestment: OtherMinistriesResponse
    projectScales: Optional[Dict[str, Any]] = Field(None, description="Project scale distribution")
    investmentByYear: List[InvestmentByYearResponse] = Field(..., description="Yearly investment chart data")
    businessGroupStats: List[BusinessGroupStatResponse] = Field(..., description="Stats by business sector")
    sectorCounts: Optional[Dict[str, int]] = Field(None, description="Project count per sector")
    countProjectGroupByPublicAuthority: List[PublicAuthorityCountResponse] = Field(
        ..., description="Project count per public authority"
    )
    sectorProjectValueBubble: List[SectorBubbleResponse] = Field(
        ..., description="Project metrics per sector for bubble chart"
    )
