"""Reference/Lookup Schemas (DTOs)"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReferenceItem(BaseModel):
    """A single reference/lookup item"""
    id: int = Field(..., description="Reference item ID")
    value: Optional[str] = Field(None, description="Display value")


class RiskCategoryItem(BaseModel):
    """Risk category reference item"""
    id: int = Field(..., description="Risk category ID")
    code: str = Field(..., description="Category code")
    value: str = Field(..., description="Category name")
    description_en: Optional[str] = None
    description_th: Optional[str] = None


class RiskFactorItem(BaseModel):
    """Risk factor reference item"""
    id: int = Field(..., description="Risk factor ID")
    value: str = Field(..., description="Factor name")
    description_th: Optional[str] = None


class RiskSourceItem(BaseModel):
    """A single risk source item with reference info"""
    id: int = Field(..., description="Reference item ID")
    value: Optional[str] = Field(None, description="Display value/meaning")
    reference: Optional[str] = Field(None, description="Detailed text citation")
    referenceFile: Optional[str] = Field(None, description="Downloadable file name")
    referenceFileUrl: Optional[str] = Field(None, description="URL endpoint to download the file")
    referenceUrl: Optional[str] = Field(None, description="External URL for the reference")


# RiskSourceResponse is a dynamic dictionary where keys are country names
RiskSourceResponse = Dict[str, List[RiskSourceItem]]


class ReferenceInfoResponse(BaseModel):
    """All reference/lookup data for dropdowns and filters"""
    sector: List[ReferenceItem] = Field(..., description="Available sectors")
    ministry: List[ReferenceItem] = Field(..., description="Available ministries")
    projectType: List[ReferenceItem] = Field(..., description="Available project types")
    concessionForm: List[ReferenceItem] = Field(..., description="Available concession forms")
    contractType: List[ReferenceItem] = Field(..., description="Available contract types")
    riskCategory: List[RiskCategoryItem] = Field(..., description="Available risk categories")
    riskPhase: List[ReferenceItem] = Field(..., description="Risk phases")
    riskFactor: List[RiskFactorItem] = Field(..., description="Available risk factors")
    riskSource: RiskSourceResponse = Field(..., description="Available risk sources")
