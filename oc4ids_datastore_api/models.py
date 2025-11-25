from sqlmodel import SQLModel, Field
from sqlalchemy import Column, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional
from datetime import datetime

class ProjectSQLModel(SQLModel, table=True):
    __tablename__ = "projects"

    id: str = Field(primary_key=True)

    identifiers: Optional[dict] = Field(default=None, sa_column=Column("identifiers", JSONB))
    updated: Optional[datetime] = Field(default=None, sa_column=Column("updated", TIMESTAMP))
    title: Optional[str] = Field(default=None, sa_column=Column("title"))
    description: Optional[str] = Field(default=None, sa_column=Column("description"))

    status: Optional[str] = Field(default=None, sa_column=Column("status"))

    period: Optional[dict] = Field(default=None, sa_column=Column("period", JSONB))
    identificationPeriod: Optional[dict] = Field(default=None, sa_column=Column("identificationperiod", JSONB))
    preparationPeriod: Optional[dict] = Field(default=None, sa_column=Column("preparationperiod", JSONB))
    implementationPeriod: Optional[dict] = Field(default=None, sa_column=Column("implementationperiod", JSONB))
    completionPeriod: Optional[dict] = Field(default=None, sa_column=Column("completionperiod", JSONB))
    maintenancePeriod: Optional[dict] = Field(default=None, sa_column=Column("maintenanceperiod", JSONB))
    decommissioningPeriod: Optional[dict] = Field(default=None, sa_column=Column("decommissioningperiod", JSONB))

    sector: Optional[dict] = Field(default=None, sa_column=Column("sector", JSONB))
    purpose: Optional[str] = Field(default=None, sa_column=Column("purpose"))
    additionalClassifications: Optional[dict] = Field(default=None, sa_column=Column("additionalclassifications", JSONB))
    type: Optional[dict] = Field(default=None, sa_column=Column("type", JSONB))
    relatedProjects: Optional[dict] = Field(default=None, sa_column=Column("relatedprojects", JSONB))

    assetLifetime: Optional[dict] = Field(default=None, sa_column=Column("assetlifetime", JSONB))
    locations: Optional[dict] = Field(default=None, sa_column=Column("locations", JSONB))
    budget: Optional[dict] = Field(default=None, sa_column=Column("budget", JSONB))
    costMeasurements: Optional[dict] = Field(default=None, sa_column=Column("costmeasurements", JSONB))
    forecasts: Optional[dict] = Field(default=None, sa_column=Column("forecasts", JSONB))

    parties: Optional[dict] = Field(default=None, sa_column=Column("parties", JSONB))
    publicAuthority: Optional[dict] = Field(default=None, sa_column=Column("publicauthority", JSONB))
    documents: Optional[dict] = Field(default=None, sa_column=Column("documents", JSONB))
    contractingProcesses: Optional[dict] = Field(default=None, sa_column=Column("contractingprocesses", JSONB))

    metrics: Optional[dict] = Field(default=None, sa_column=Column("metrics", JSONB))
    transactions: Optional[dict] = Field(default=None, sa_column=Column("transactions", JSONB))
    milestones: Optional[dict] = Field(default=None, sa_column=Column("milestones", JSONB))
    completion: Optional[dict] = Field(default=None, sa_column=Column("completion", JSONB))
    lobbyingMeetings: Optional[dict] = Field(default=None, sa_column=Column("lobbyingmeetings", JSONB))

    social: Optional[dict] = Field(default=None, sa_column=Column("social", JSONB))
    environment: Optional[dict] = Field(default=None, sa_column=Column("environment", JSONB))
    benefits: Optional[dict] = Field(default=None, sa_column=Column("benefits", JSONB))
    policyAlignment: Optional[dict] = Field(default=None, sa_column=Column("policyalignment", JSONB))
