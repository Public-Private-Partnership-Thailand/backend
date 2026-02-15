from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON, Date, String, Float, Integer
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
    start_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    end_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    max_extent_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
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
    gazetteer: Optional["LocationGazetteer"] = Relationship(back_populates="location", sa_relationship_kwargs={"uselist": False}) # Link to gazetteer table (1-to-1 usually)

class ProjectDocument(SQLModel, table=True):
    __tablename__ = "project_documents"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    local_id: str
    document_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    date_published: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    date_modified: Optional[datetime] = Field(default=None, sa_column=Column(Date))
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
    project_id: uuid.UUID = Field(foreign_key="projects.id") # Unique in SQL
    description: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    request_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    approval_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    
    project: "Project" = Relationship(back_populates="budget", sa_relationship_kwargs={"uselist": False})
    breakdowns: List["BudgetBreakdown"] = Relationship(back_populates="budget")
    finances: List["ProjectFinance"] = Relationship(back_populates="budget")

class BudgetBreakdown(SQLModel, table=True):
    __tablename__ = "budget_breakdowns"
    id: Optional[int] = Field(default=None, primary_key=True)
    budget_id: int = Field(foreign_key="project_budgets.id")
    local_id: str
    description: Optional[str] = None
    
    budget: "ProjectBudget" = Relationship(back_populates="breakdowns")
    items: List["BudgetBreakdownItem"] = Relationship(back_populates="breakdown")

class BudgetBreakdownItem(SQLModel, table=True):
    __tablename__ = "budget_breakdown_items"
    id: Optional[int] = Field(default=None, primary_key=True)
    breakdown_id: int = Field(foreign_key="budget_breakdowns.id")
    local_id: str
    description: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    uri: Optional[str] = None
    period_start_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    period_end_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    period_max_extent_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    period_duration_days: Optional[int] = None
    source_party_id: Optional[str] = None
    source_party_name: Optional[str] = None
    
    breakdown: "BudgetBreakdown" = Relationship(back_populates="items")

class ProjectFinance(SQLModel, table=True):
    __tablename__ = "project_finance"
    id: Optional[int] = Field(default=None, primary_key=True)
    budget_id: int = Field(foreign_key="project_budgets.id")
    local_id: str
    asset_class: Optional[str] = None
    type: Optional[str] = None
    concessional: Optional[bool] = None
    value_amount: Optional[float] = None
    value_currency: Optional[str] = None
    source: Optional[str] = None
    financing_party_id: Optional[str] = None
    financing_party_name: Optional[str] = None
    period_start_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    period_end_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    payment_period_start_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    payment_period_end_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    interest_rate_margin: Optional[float] = None
    description: Optional[str] = None
    
    budget: "ProjectBudget" = Relationship(back_populates="finances")

class ProjectParty(SQLModel, table=True):
    __tablename__ = "project_parties"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    local_id: str
    name: Optional[str] = None
    identifier_scheme: Optional[str] = None
    identifier_value: Optional[str] = None
    identifier_legal_name_id: Optional[int] = Field(default=None, foreign_key="agency.id")
    agency: Optional["Agency"] = Relationship()
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
    roles: List["PartyRole"] = Relationship() # No back_populate needed for simple link table usually
    people: List["PartyPerson"] = Relationship()
    beneficial_owners: List["PartyBeneficialOwner"] = Relationship()
    classifications: List["PartyClassification"] = Relationship()

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

class PartyPerson(SQLModel, table=True):
    __tablename__ = "party_people"
    id: Optional[int] = Field(default=None, primary_key=True)
    party_id: int = Field(foreign_key="project_parties.id")
    local_id: str
    name: Optional[str] = None
    job_title: Optional[str] = None

class PartyBeneficialOwner(SQLModel, table=True):
    __tablename__ = "party_beneficial_owners"
    id: Optional[int] = Field(default=None, primary_key=True)
    party_id: int = Field(foreign_key="project_parties.id")
    local_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    fax_number: Optional[str] = None
    identifier_scheme: Optional[str] = None
    identifier_value: Optional[str] = None
    street_address: Optional[str] = None
    locality: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country_name: Optional[str] = None
    
    nationalities: List["BeneficialOwnerNationality"] = Relationship(back_populates="owner")

class BeneficialOwnerNationality(SQLModel, table=True):
    __tablename__ = "beneficial_owner_nationalities"
    owner_id: int = Field(foreign_key="party_beneficial_owners.id", primary_key=True)
    nationality: str = Field(primary_key=True)
    
    owner: "PartyBeneficialOwner" = Relationship(back_populates="nationalities")

class PartyClassification(SQLModel, table=True):
    __tablename__ = "party_classifications"
    party_id: int = Field(foreign_key="project_parties.id", primary_key=True)
    scheme: str = Field(primary_key=True)
    classification_id: str = Field(primary_key=True)

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
    period_start_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    period_end_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    period_max_extent_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    period_duration_days: Optional[int] = None
    
    project: "Project" = Relationship(back_populates="contracting_processes")
    
    # Children
    milestones: List["ContractingProcessMilestone"] = Relationship(back_populates="contracting_process")
    transactions: List["ContractingProcessTransaction"] = Relationship(back_populates="contracting_process")
    modifications: List["ContractingProcessModification"] = Relationship(back_populates="contracting_process")
    documents: List["ContractingProcessDocument"] = Relationship(back_populates="contracting_process")
    
    tender: Optional["ContractingTender"] = Relationship(back_populates="contracting_process", sa_relationship_kwargs={"uselist": False})
    suppliers: List["ContractingSupplier"] = Relationship(back_populates="contracting_process")
    social: Optional["ContractingSocial"] = Relationship(back_populates="contracting_process", sa_relationship_kwargs={"uselist": False})
    releases: List["ContractingRelease"] = Relationship(back_populates="contracting_process")

class ContractingProcessMilestone(SQLModel, table=True):
    __tablename__ = "contracting_milestones" # Corrected table name from SQL
    id: Optional[int] = Field(default=None, primary_key=True)
    process_id: int = Field(foreign_key="project_contracting_processes.id") # SQL uses process_id
    local_id: str
    title: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    due_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    date_met: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    date_modified: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    status: Optional[str] = None
    value_amount: Optional[float] = None
    value_currency: Optional[str] = None
    
    contracting_process: "ProjectContractingProcess" = Relationship(back_populates="milestones")

class ContractingTender(SQLModel, table=True):
    __tablename__ = "contracting_tenders"
    process_id: int = Field(foreign_key="project_contracting_processes.id", primary_key=True)
    procurement_method: Optional[str] = None
    procurement_method_details: Optional[str] = None
    date_published: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    cost_estimate_amount: Optional[float] = None
    cost_estimate_currency: Optional[str] = None
    number_of_tenderers: Optional[int] = None
    
    contracting_process: "ProjectContractingProcess" = Relationship(back_populates="tender")
    tenderers: List["ContractingTenderTenderer"] = Relationship(back_populates="tender")
    tender_entities: List["ContractingTenderEntity"] = Relationship(back_populates="tender")
    sustainability: List["ContractingTenderSustainability"] = Relationship(back_populates="tender")

class ContractingTenderTenderer(SQLModel, table=True):
    __tablename__ = "contracting_tender_tenderers"
    id: Optional[int] = Field(default=None, primary_key=True)
    process_id: int = Field(foreign_key="contracting_tenders.process_id")
    local_id: str
    name: Optional[str] = None
    
    tender: "ContractingTender" = Relationship(back_populates="tenderers")

class ContractingTenderEntity(SQLModel, table=True):
    __tablename__ = "contracting_tender_entities"
    id: Optional[int] = Field(default=None, primary_key=True)
    process_id: int = Field(foreign_key="contracting_tenders.process_id")
    role: Optional[str] = None
    name: Optional[str] = None
    
    tender: "ContractingTender" = Relationship(back_populates="tender_entities")

class ContractingTenderSustainability(SQLModel, table=True):
    __tablename__ = "contracting_tender_sustainability"
    id: Optional[int] = Field(default=None, primary_key=True)
    process_id: int = Field(foreign_key="contracting_tenders.process_id")
    strategies: Optional[List[dict]] = Field(default=None, sa_column=Column(JSONB))
    
    tender: "ContractingTender" = Relationship(back_populates="sustainability")

class ContractingSupplier(SQLModel, table=True):
    __tablename__ = "contracting_suppliers"
    id: Optional[int] = Field(default=None, primary_key=True)
    process_id: int = Field(foreign_key="project_contracting_processes.id")
    local_id: str
    name: Optional[str] = None
    
    contracting_process: "ProjectContractingProcess" = Relationship(back_populates="suppliers")

class ContractingSocial(SQLModel, table=True):
    __tablename__ = "contracting_social"
    process_id: int = Field(foreign_key="project_contracting_processes.id", primary_key=True)
    labor_budget_amount: Optional[float] = None
    labor_budget_currency: Optional[str] = None
    labor_obligations: Optional[List[dict]] = Field(default=None, sa_column=Column(JSONB))
    labor_description: Optional[str] = None
    
    contracting_process: "ProjectContractingProcess" = Relationship(back_populates="social")

class ContractingRelease(SQLModel, table=True):
    __tablename__ = "contracting_releases"
    id: Optional[int] = Field(default=None, primary_key=True)
    process_id: int = Field(foreign_key="project_contracting_processes.id")
    local_id: str
    tag: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    url: Optional[str] = None
    
    contracting_process: "ProjectContractingProcess" = Relationship(back_populates="releases")

class ContractingProcessTransaction(SQLModel, table=True):
    __tablename__ = "contracting_transactions" # Corrected table name
    id: Optional[int] = Field(default=None, primary_key=True)
    process_id: int = Field(foreign_key="project_contracting_processes.id")
    local_id: str
    source: Optional[str] = None
    date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    amount: Optional[float] = None
    currency: Optional[str] = None
    payer_name: Optional[str] = None
    payee_name: Optional[str] = None
    uri: Optional[str] = None
    
    contracting_process: "ProjectContractingProcess" = Relationship(back_populates="transactions")

class ContractingProcessModification(SQLModel, table=True):
    __tablename__ = "contracting_modifications"
    id: Optional[int] = Field(default=None, primary_key=True)
    process_id: int = Field(foreign_key="project_contracting_processes.id")
    local_id: str
    date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    description: Optional[str] = None
    rationale: Optional[str] = None
    type: Optional[str] = None
    release_id: Optional[str] = None
    old_amount: Optional[float] = None
    old_currency: Optional[str] = None
    new_amount: Optional[float] = None
    new_currency: Optional[str] = None
    old_start_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    old_end_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    new_start_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    new_end_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))

    contracting_process: "ProjectContractingProcess" = Relationship(back_populates="modifications")

class ContractingProcessDocument(SQLModel, table=True):
    __tablename__ = "contracting_documents" # Corrected table name
    id: Optional[int] = Field(default=None, primary_key=True)
    process_id: int = Field(foreign_key="project_contracting_processes.id")
    local_id: str
    document_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    date_published: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    date_modified: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    format: Optional[str] = None
    language: Optional[str] = None
    page_start: Optional[str] = None
    page_end: Optional[str] = None
    access_details: Optional[str] = None
    author: Optional[str] = None
    
    contracting_process: "ProjectContractingProcess" = Relationship(back_populates="documents")

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

class ProjectCostMeasurement(SQLModel, table=True):
    __tablename__ = "project_cost_measurements"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    local_id: str
    measurement_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    lifecycle_cost_amount: Optional[float] = None
    lifecycle_cost_currency: Optional[str] = None
    
    project: "Project" = Relationship(back_populates="cost_measurements")
    cost_groups: List["CostGroup"] = Relationship(back_populates="cost_measurement")

class CostGroup(SQLModel, table=True):
    __tablename__ = "cost_groups"
    id: Optional[int] = Field(default=None, primary_key=True)
    cost_measurement_id: int = Field(foreign_key="project_cost_measurements.id")
    local_id: str
    category: Optional[str] = None
    
    cost_measurement: "ProjectCostMeasurement" = Relationship(back_populates="cost_groups")
    cost_items: List["CostItem"] = Relationship(back_populates="cost_group")

class CostItem(SQLModel, table=True):
    __tablename__ = "cost_items"
    id: Optional[int] = Field(default=None, primary_key=True)
    cost_group_id: int = Field(foreign_key="cost_groups.id")
    local_id: str
    amount: Optional[float] = None
    currency: Optional[str] = None
    classification_id: Optional[str] = None
    classification_scheme: Optional[str] = None
    classification_description: Optional[str] = None

    cost_group: "CostGroup" = Relationship(back_populates="cost_items")

class ProjectForecast(SQLModel, table=True):
    __tablename__ = "project_forecasts"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    local_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    
    project: "Project" = Relationship(back_populates="forecasts")
    observations: List["ForecastObservation"] = Relationship(back_populates="forecast")

class ForecastObservation(SQLModel, table=True):
    __tablename__ = "forecast_observations"
    id: Optional[int] = Field(default=None, primary_key=True)
    forecast_id: int = Field(foreign_key="project_forecasts.id")
    local_id: str
    measure: Optional[str] = None
    notes: Optional[str] = None
    value_amount: Optional[float] = None
    value_currency: Optional[str] = None
    period_start_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    period_end_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    period_max_extent_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    period_duration_days: Optional[int] = None
    unit_name: Optional[str] = None
    unit_scheme: Optional[str] = None
    unit_id: Optional[str] = None
    unit_uri: Optional[str] = None
    dimensions: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    
    forecast: "ProjectForecast" = Relationship(back_populates="observations")

class ProjectMetric(SQLModel, table=True):
    __tablename__ = "project_metrics"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    local_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    
    project: "Project" = Relationship(back_populates="metrics")
    observations: List["MetricObservation"] = Relationship(back_populates="metric")

class MetricObservation(SQLModel, table=True):
    __tablename__ = "metric_observations"
    id: Optional[int] = Field(default=None, primary_key=True)
    metric_id: int = Field(foreign_key="project_metrics.id")
    local_id: str
    measure: Optional[str] = None
    notes: Optional[str] = None
    value_amount: Optional[float] = None
    value_currency: Optional[str] = None
    period_start_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    period_end_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    period_max_extent_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    period_duration_days: Optional[int] = None
    unit_name: Optional[str] = None
    unit_scheme: Optional[str] = None
    unit_id: Optional[str] = None
    unit_uri: Optional[str] = None
    dimensions: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    
    metric: "ProjectMetric" = Relationship(back_populates="observations")

class LocationGazetteer(SQLModel, table=True):
    __tablename__ = "location_gazetteers"
    id: Optional[int] = Field(default=None, primary_key=True)
    location_id: uuid.UUID = Field(foreign_key="project_locations.id")
    scheme: str 
    
    identifiers: List["LocationGazetteerIdentifier"] = Relationship(back_populates="gazetteer")
    location: "ProjectLocation" = Relationship(back_populates="gazetteer")

class LocationGazetteerIdentifier(SQLModel, table=True):
    __tablename__ = "location_gazetteer_identifiers"
    id: Optional[int] = Field(default=None, primary_key=True)
    gazetteer_id: int = Field(foreign_key="location_gazetteers.id")
    identifier: str
    
    gazetteer: "LocationGazetteer" = Relationship(back_populates="identifiers")

class ProjectLobbyingMeeting(SQLModel, table=True):
    __tablename__ = "project_lobbying_meetings"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    local_id: str
    meeting_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    number_of_participants: Optional[int] = None
    
    street_address: Optional[str] = None
    locality: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country_name: Optional[str] = None
    
    public_office_job_title: Optional[str] = None
    public_office_person_name: Optional[str] = None
    public_office_org_id: Optional[str] = None
    public_office_org_name: Optional[str] = None
    
    project: "Project" = Relationship(back_populates="lobbying_meetings")

class ProjectPolicyAlignment(SQLModel, table=True):
    __tablename__ = "project_policy_alignment"
    project_id: uuid.UUID = Field(foreign_key="projects.id", primary_key=True)
    description: Optional[str] = None
    
    project: "Project" = Relationship(back_populates="policy_alignment")
    policies: List["ProjectPolicyAlignmentPolicy"] = Relationship(back_populates="policy_alignment")

class ProjectPolicyAlignmentPolicy(SQLModel, table=True):
    __tablename__ = "project_policy_alignment_policies"
    project_id: uuid.UUID = Field(foreign_key="project_policy_alignment.project_id", primary_key=True)
    policy: str = Field(primary_key=True)
    
    policy_alignment: "ProjectPolicyAlignment" = Relationship(back_populates="policies")

class ProjectAssetLifetime(SQLModel, table=True):
    __tablename__ = "project_asset_lifetime"
    project_id: uuid.UUID = Field(foreign_key="projects.id", primary_key=True)
    period_start_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    period_end_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    period_max_extent_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    period_duration_days: Optional[int] = None
    
    project: "Project" = Relationship(back_populates="asset_lifetime")

# ===================================
# SOCIAL & ENVIRONMENT & BENEFITS
# ===================================

class ProjectSocial(SQLModel, table=True):
    __tablename__ = "project_social"
    project_id: uuid.UUID = Field(foreign_key="projects.id", primary_key=True)
    in_indigenous_land: Optional[bool] = None
    land_compensation_amount: Optional[float] = None
    land_compensation_currency: Optional[str] = None
    health_safety_material_test_description: Optional[str] = None
    
    project: "Project" = Relationship(back_populates="social")
    health_safety_tests: List["SocialHealthSafetyMaterialTest"] = Relationship(back_populates="social")
    consultation_meetings: List["SocialConsultationMeeting"] = Relationship(back_populates="social")

class SocialConsultationMeeting(SQLModel, table=True):
    __tablename__ = "social_consultation_meetings"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project_social.project_id")
    local_id: str
    date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    number_of_participants: Optional[int] = None
    
    # Address
    street_address: Optional[str] = None
    locality: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country_name: Optional[str] = None
    
    # Public Office / Person
    person_name: Optional[str] = None
    organization_name: Optional[str] = None
    organization_id: Optional[str] = None
    job_title: Optional[str] = None
    
    social: "ProjectSocial" = Relationship(back_populates="consultation_meetings")

class SocialHealthSafetyMaterialTest(SQLModel, table=True):
    __tablename__ = "social_health_safety_material_tests"
    project_id: uuid.UUID = Field(foreign_key="project_social.project_id", primary_key=True)
    test: str = Field(primary_key=True)
    
    social: "ProjectSocial" = Relationship(back_populates="health_safety_tests")

class ProjectEnvironment(SQLModel, table=True):
    __tablename__ = "project_environment"
    project_id: uuid.UUID = Field(foreign_key="projects.id", primary_key=True)
    has_impact_assessment: Optional[bool] = None
    in_protected_area: Optional[bool] = None
    abatement_cost_amount: Optional[float] = None
    abatement_cost_currency: Optional[str] = None
    
    project: "Project" = Relationship(back_populates="environment")
    goals: List["EnvironmentGoal"] = Relationship(back_populates="environment")
    climate_oversight_types: List["EnvironmentClimateOversightType"] = Relationship(back_populates="environment")
    conservation_measures: List["EnvironmentConservationMeasure"] = Relationship(back_populates="environment")
    environmental_measures: List["EnvironmentEnvironmentalMeasure"] = Relationship(back_populates="environment")
    climate_measures: List["EnvironmentClimateMeasure"] = Relationship(back_populates="environment")
    impact_categories: List["EnvironmentImpactCategory"] = Relationship(back_populates="environment")

class EnvironmentGoal(SQLModel, table=True):
    __tablename__ = "environment_goals"
    project_id: uuid.UUID = Field(foreign_key="project_environment.project_id", primary_key=True)
    goal: str = Field(primary_key=True)
    environment: "ProjectEnvironment" = Relationship(back_populates="goals")

class EnvironmentClimateOversightType(SQLModel, table=True):
    __tablename__ = "environment_climate_oversight_types"
    project_id: uuid.UUID = Field(foreign_key="project_environment.project_id", primary_key=True)
    oversight_type: str = Field(primary_key=True)
    environment: "ProjectEnvironment" = Relationship(back_populates="climate_oversight_types")

class EnvironmentConservationMeasure(SQLModel, table=True):
    __tablename__ = "environment_conservation_measures"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project_environment.project_id")
    type: Optional[str] = None
    description: Optional[str] = None
    environment: "ProjectEnvironment" = Relationship(back_populates="conservation_measures")

class EnvironmentEnvironmentalMeasure(SQLModel, table=True):
    __tablename__ = "environment_environmental_measures"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project_environment.project_id")
    type: Optional[str] = None
    description: Optional[str] = None
    environment: "ProjectEnvironment" = Relationship(back_populates="environmental_measures")

class EnvironmentClimateMeasure(SQLModel, table=True):
    __tablename__ = "environment_climate_measures"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project_environment.project_id")
    type: Optional[str] = None
    description: Optional[str] = None
    environment: "ProjectEnvironment" = Relationship(back_populates="climate_measures")

class EnvironmentImpactCategory(SQLModel, table=True):
    __tablename__ = "environment_impact_categories"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project_environment.project_id")
    scheme: Optional[str] = None
    category_id: Optional[str] = None
    environment: "ProjectEnvironment" = Relationship(back_populates="impact_categories")

class ProjectBenefit(SQLModel, table=True):
    __tablename__ = "project_benefits"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    title: Optional[str] = None
    description: Optional[str] = None
    
    project: "Project" = Relationship(back_populates="benefits")
    beneficiaries: List["BenefitBeneficiary"] = Relationship(back_populates="benefit")

class BenefitBeneficiary(SQLModel, table=True):
    __tablename__ = "benefit_beneficiaries"
    id: Optional[int] = Field(default=None, primary_key=True)
    benefit_id: int = Field(foreign_key="project_benefits.id")
    description: Optional[str] = None
    number_of_people: Optional[int] = None
    location_id: Optional[uuid.UUID] = None # Not strictly linking to location table to avoid complexity for now
    
    benefit: "ProjectBenefit" = Relationship(back_populates="beneficiaries")

class ProjectCompletion(SQLModel, table=True):
    __tablename__ = "project_completion"
    project_id: uuid.UUID = Field(foreign_key="projects.id", primary_key=True)
    end_date: Optional[datetime] = Field(default=None, sa_column=Column(Date))
    end_date_details: Optional[str] = None
    final_scope: Optional[str] = None
    final_scope_details: Optional[str] = None
    final_value_amount: Optional[float] = None
    final_value_currency: Optional[str] = None
    
    project: "Project" = Relationship(back_populates="completion")


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
    budget: Optional["ProjectBudget"] = Relationship(back_populates="project")
    parties_list: List["ProjectParty"] = Relationship(back_populates="project")
    contracting_processes: List["ProjectContractingProcess"] = Relationship(back_populates="project")
    related_projects: List["ProjectRelatedProject"] = Relationship(back_populates="project")
    
    # New Children
    cost_measurements: List["ProjectCostMeasurement"] = Relationship(back_populates="project")
    forecasts: List["ProjectForecast"] = Relationship(back_populates="project")
    metrics: List["ProjectMetric"] = Relationship(back_populates="project")
    
    social: Optional["ProjectSocial"] = Relationship(back_populates="project")
    environment: Optional["ProjectEnvironment"] = Relationship(back_populates="project")
    benefits: List["ProjectBenefit"] = Relationship(back_populates="project")
    completion: Optional["ProjectCompletion"] = Relationship(back_populates="project")
    lobbying_meetings: List["ProjectLobbyingMeeting"] = Relationship(back_populates="project")
    policy_alignment: Optional["ProjectPolicyAlignment"] = Relationship(back_populates="project")
    asset_lifetime: Optional["ProjectAssetLifetime"] = Relationship(back_populates="project")

    # Many-to-Many
    sectors: List["Sector"] = Relationship(link_model=ProjectSectorLink)
    additional_classifications: List["AdditionalClassification"] = Relationship(link_model=ProjectAdditionalClassificationLink)

    def _format_amount(self, amount: float) -> str:
        """Format amount in Thai style with units"""
        from oc4ids_datastore_api.utils import format_thai_amount
        return format_thai_amount(amount)

    def to_oc4ids(self) -> Dict[str, Any]:
        """Convert the project and its children to OC4IDS JSON format"""
        from oc4ids_datastore_api.serializers import project_to_oc4ids
        return project_to_oc4ids(self)
