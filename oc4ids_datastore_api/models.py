from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from sqlalchemy.dialects.postgresql import JSONB

# ===================================
# REFERENCE TABLES
# ===================================

class ProjectType(SQLModel, table=True):
    __tablename__ = "project_type"
    id: Optional[int] = Field(default=None, primary_key=True)
    scheme: Optional[str] = None
    code: str
    name_th: Optional[str] = None
    name_en: Optional[str] = None
    description: Optional[str] = None

class Ministry(SQLModel, table=True):
    __tablename__ = "ministry"
    id: Optional[int] = Field(default=None, primary_key=True)
    name_th: str
    name_en: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class Agency(SQLModel, table=True):
    __tablename__ = "agency"
    id: Optional[int] = Field(default=None, primary_key=True)
    name_th: str
    name_en: Optional[str] = None
    ministry_id: Optional[int] = Field(default=None, foreign_key="ministry.id")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class PeriodType(SQLModel, table=True):
    __tablename__ = "period_types"
    code: str = Field(primary_key=True)
    name_en: str
    name_th: Optional[str] = None
    description: Optional[str] = None
    sequence: Optional[int] = None
    is_active: bool = Field(default=True)

class Sector(SQLModel, table=True):
    __tablename__ = "sector"
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="sector.id")
    name_th: str
    name_en: Optional[str] = None
    category: str
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class Currency(SQLModel, table=True):
    __tablename__ = "currencies"
    code: str = Field(primary_key=True, max_length=3)
    name: str
    symbol: Optional[str] = None
    is_active: bool = Field(default=True)

class AdditionalClassification(SQLModel, table=True):
    __tablename__ = "additional_classifications"
    id: Optional[int] = Field(default=None, primary_key=True) # BigSerial in SQL -> int in Python
    scheme: str
    code: str
    description: Optional[str] = None
    uri: Optional[str] = None

# ===================================
# LINK TABLES
# ===================================

class ProjectSectorLink(SQLModel, table=True):
    __tablename__ = "project_sector"
    project_id: uuid.UUID = Field(foreign_key="projects.id", primary_key=True)
    sector_id: int = Field(foreign_key="sector.id", primary_key=True)

class ProjectAdditionalClassificationLink(SQLModel, table=True):
    __tablename__ = "project_additional_classifications"
    project_id: uuid.UUID = Field(foreign_key="projects.id", primary_key=True)
    classification_id: int = Field(foreign_key="additional_classifications.id", primary_key=True)

# ===================================
# CHILD TABLES
# ===================================

class ProjectIdentifier(SQLModel, table=True):
    __tablename__ = "project_identifiers"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    identifier_value: str
    scheme: Optional[str] = None
    project: "Project" = Relationship(back_populates="identifiers_list")

class ProjectPeriod(SQLModel, table=True):
    __tablename__ = "project_periods"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    period_type: str = Field(foreign_key="period_types.code")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    max_extent_date: Optional[date] = None
    duration_days: Optional[int] = None
    project: "Project" = Relationship(back_populates="periods")

class ProjectLocation(SQLModel, table=True):
    __tablename__ = "project_locations"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    description: Optional[str] = None
    uri: Optional[str] = None
    geometry_type: Optional[str] = None
    geometry_coordinates: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    street_address: Optional[str] = None
    locality: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country_name: Optional[str] = None
    project: "Project" = Relationship(back_populates="locations_list")

class ProjectDocument(SQLModel, table=True):
    __tablename__ = "project_documents"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    local_id: str
    document_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    date_published: Optional[date] = None
    date_modified: Optional[date] = None
    format: Optional[str] = None
    language: Optional[str] = None
    page_start: Optional[str] = None
    page_end: Optional[str] = None
    access_details: Optional[str] = None
    author: Optional[str] = None
    project: "Project" = Relationship(back_populates="documents_list")

class ProjectBudget(SQLModel, table=True):
    __tablename__ = "project_budgets"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    description: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    request_date: Optional[date] = None
    approval_date: Optional[date] = None
    project: "Project" = Relationship(back_populates="budgets_list")

class ProjectParty(SQLModel, table=True):
    __tablename__ = "project_parties"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    local_id: str
    name: Optional[str] = None
    identifier_scheme: Optional[str] = None
    identifier_value: Optional[str] = None
    identifier_legal_name_id: Optional[int] = Field(default=None, foreign_key="ministry.id")
    ministry: Optional["Ministry"] = Relationship()
    identifier_uri: Optional[str] = None
    
    # Address (Embedded)
    street_address: Optional[str] = None
    locality: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country_name: Optional[str] = None
    
    # Contact (Embedded)
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_telephone: Optional[str] = None
    contact_fax: Optional[str] = None
    contact_url: Optional[str] = None

    project: "Project" = Relationship(back_populates="parties_list")
    additional_identifiers: List["PartyAdditionalIdentifier"] = Relationship(back_populates="party")

class PartyAdditionalIdentifier(SQLModel, table=True):
    __tablename__ = "party_additional_identifiers"
    id: Optional[int] = Field(default=None, primary_key=True)
    party_id: int = Field(foreign_key="project_parties.id")
    scheme: Optional[str] = None
    identifier: Optional[str] = None
    legal_name_id: Optional[int] = Field(default=None, foreign_key="ministry.id")
    uri: Optional[str] = None
    
    party: "ProjectParty" = Relationship(back_populates="additional_identifiers")
    ministry: Optional["Ministry"] = Relationship()

class PartyRole(SQLModel, table=True):
    __tablename__ = "party_roles"
    party_id: int = Field(foreign_key="project_parties.id", primary_key=True)
    role: str = Field(primary_key=True)

class ProjectContractingProcess(SQLModel, table=True):
    __tablename__ = "project_contracting_processes"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    local_id: str
    
    # Summary
    ocid: Optional[str] = None
    external_reference: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    nature: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    
    # Values
    contract_amount: Optional[float] = None
    contract_currency: Optional[str] = None
    final_amount: Optional[float] = None
    final_currency: Optional[str] = None
    
    # Periods
    period_start_date: Optional[date] = None
    period_end_date: Optional[date] = None
    period_max_extent_date: Optional[date] = None
    period_duration_days: Optional[int] = None
    
    project: "Project" = Relationship(back_populates="contracting_processes")

class ProjectRelatedProject(SQLModel, table=True):
    __tablename__ = "project_related_projects"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    relationship_id: str
    scheme: Optional[str] = None
    identifier: str
    relationship: str
    title: Optional[str] = None
    uri: Optional[str] = None
    project: "Project" = Relationship(back_populates="related_projects")

# ===================================
# MAIN PROJECT MODEL
# ===================================

class Project(SQLModel, table=True):
    __tablename__ = "projects"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    purpose: Optional[str] = None
    
    project_type_id: Optional[int] = Field(default=None, foreign_key="project_type.id")
    public_authority_id: Optional[int] = Field(default=None, foreign_key="agency.id")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[uuid.UUID] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[uuid.UUID] = None
    deleted_at: Optional[datetime] = None
    
    # Relationships
    project_type: Optional["ProjectType"] = Relationship()
    public_authority: Optional["Agency"] = Relationship()
    
    # Children
    identifiers_list: List["ProjectIdentifier"] = Relationship(back_populates="project")
    periods: List["ProjectPeriod"] = Relationship(back_populates="project")
    locations_list: List["ProjectLocation"] = Relationship(back_populates="project")
    documents_list: List["ProjectDocument"] = Relationship(back_populates="project")
    budgets_list: List["ProjectBudget"] = Relationship(back_populates="project")
    parties_list: List["ProjectParty"] = Relationship(back_populates="project")
    contracting_processes: List["ProjectContractingProcess"] = Relationship(back_populates="project")
    related_projects: List["ProjectRelatedProject"] = Relationship(back_populates="project")
    
    # Many-to-Many
    sectors: List["Sector"] = Relationship(link_model=ProjectSectorLink)
    additional_classifications: List["AdditionalClassification"] = Relationship(link_model=ProjectAdditionalClassificationLink)
