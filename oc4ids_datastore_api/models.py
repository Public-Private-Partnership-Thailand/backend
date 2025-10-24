import datetime

from sqlmodel import SQLModel, Field,Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, Any, Dict
import datetime

class ProjectSQLModel(SQLModel, table=True):
    __tablename__ = "projects"

    id: str = Field(primary_key=True)
    identifiers: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    updated: Optional[datetime.datetime] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    period: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    identification_period: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    preparation_period: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    implementation_period: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    completion_period: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    maintenance_period: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    decommissioning_period: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    sector: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    additional_classifications: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    related_projects: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    asset_lifetime: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    locations: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    budget: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    cost_measurements: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    parties: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    public_authority: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    documents: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    forecasts: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    metrics: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    contracting_processes: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    milestones: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    transactions: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    completion: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    lobbying_meetings: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    social: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    environment: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    policy_alignment: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    benefits: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB))
    type: Optional[str] = None
    purpose: Optional[str] = None
    language: Optional[str] = None