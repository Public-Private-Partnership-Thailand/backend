"""
OC4IDS Datastore API - Data Transfer Objects (DTOs)

Pydantic models for request validation and response serialization.
These models drive the auto-generated Swagger/ReDoc documentation.
"""
import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ============================================================================
#  Common / Shared Sub-models
# ============================================================================

class AmountResponse(BaseModel):
    """Represents a monetary amount with currency"""
    amount: Optional[float] = Field(None, description="Monetary amount", examples=[1500000000.0])
    currency: Optional[str] = Field(None, description="ISO 4217 currency code", examples=["THB"])

class AmountFormattedResponse(AmountResponse):
    """Monetary amount with a Thai-formatted string"""
    amountFormatted: Optional[str] = Field(None, description="Human-readable formatted amount (Thai)", examples=["1,500,000,000.00"])

class PeriodResponse(BaseModel):
    """A date period"""
    startDate: Optional[str] = Field(None, description="Start date (ISO 8601)", examples=["2023-01-01"])
    endDate: Optional[str] = Field(None, description="End date (ISO 8601)", examples=["2028-12-31"])
    durationInDays: Optional[int] = Field(None, description="Duration in days", examples=[2190])
    maxExtentDate: Optional[str] = Field(None, description="Maximum extent date (ISO 8601)")

class AddressResponse(BaseModel):
    """Physical address"""
    streetAddress: Optional[str] = None
    locality: Optional[str] = None
    region: Optional[str] = None
    postalCode: Optional[str] = None
    countryName: Optional[str] = None

class IdentifierResponse(BaseModel):
    """Organization identifier"""
    scheme: Optional[str] = None
    id: Optional[str] = None
    legalName: Optional[str] = None
    uri: Optional[str] = None

class ContactPointResponse(BaseModel):
    """Contact information"""
    name: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    fax: Optional[str] = None
    url: Optional[str] = None

class Publisher(BaseModel):
    name: str
    country: Optional[str] = None

class License(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    title_short: Optional[str] = None

class Portal(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None

class Download(BaseModel):
    format: str
    url: str

class Dataset(BaseModel):
    loaded_at: datetime.datetime
    source_url: str
    publisher: Publisher
    license: License
    portal: Portal
    downloads: List[Download]


# ============================================================================
#  Pagination
# ============================================================================

class PaginationResponse(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., description="Current page number", examples=[1])
    pageSize: int = Field(..., description="Number of items per page", examples=[20])
    total: int = Field(..., description="Total number of items", examples=[150])
    totalPages: int = Field(..., description="Total number of pages", examples=[8])


# ============================================================================
#  GET /projects  — List Projects
# ============================================================================

class ProjectListItem(BaseModel):
    """A summarised project in the list view"""
    id: str = Field(..., description="Project UUID", examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"])
    title: Optional[str] = Field(None, description="Project title")
    ministry: Optional[List[str]] = Field(None, description="List of associated ministries")
    public_authority: Optional[str] = Field(None, description="Public authority / agency name")
    private_parties: Optional[List[str]] = Field(None, description="Private parties involved")
    sector: Optional[List[str]] = Field(None, description="Sector names")
    concession: Optional[List[str]] = Field(None, description="Concession form names")
    start_date: Optional[Any] = Field(None, description="Project start date")

class ProjectListResponse(BaseModel):
    """Paginated list of projects"""
    data: List[ProjectListItem] = Field(..., description="Array of project summary items")
    pagination: PaginationResponse


# ============================================================================
#  GET /projects/{project_id}  — Single Project (OC4IDS format)
# ============================================================================

class PublicAuthorityResponse(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None

class AdditionalClassificationResponse(BaseModel):
    scheme: Optional[str] = None
    id: Optional[str] = None
    description: Optional[str] = None
    uri: Optional[str] = None

class GazetteerResponse(BaseModel):
    scheme: Optional[str] = None
    identifiers: Optional[List[str]] = None

class LocationResponse(BaseModel):
    geometry: Optional[Any] = None
    description: Optional[str] = None
    address: Optional[AddressResponse] = None
    gazetteers: Optional[List[GazetteerResponse]] = None

class PersonResponse(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    jobTitle: Optional[str] = None

class BeneficialOwnerResponse(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    faxNumber: Optional[str] = None
    identifier: Optional[IdentifierResponse] = None
    address: Optional[AddressResponse] = None
    nationalities: Optional[List[str]] = None

class PartyClassificationResponse(BaseModel):
    scheme: Optional[str] = None
    id: Optional[str] = None

class PartyResponse(BaseModel):
    """An organization/party involved in the project"""
    id: Optional[str] = None
    name: Optional[str] = None
    roles: Optional[List[str]] = None
    identifier: Optional[IdentifierResponse] = None
    address: Optional[AddressResponse] = None
    contactPoint: Optional[ContactPointResponse] = None
    additionalIdentifiers: Optional[List[IdentifierResponse]] = None
    persons: Optional[List[PersonResponse]] = None
    beneficialOwners: Optional[List[BeneficialOwnerResponse]] = None
    classifications: Optional[List[PartyClassificationResponse]] = None

class TendererResponse(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None

class ProcuringEntityResponse(BaseModel):
    name: Optional[str] = None

class TenderSustainabilityResponse(BaseModel):
    strategies: Optional[List[str]] = None

class TenderResponse(BaseModel):
    procurementMethod: Optional[str] = None
    procurementMethodDetails: Optional[str] = None
    datePublished: Optional[str] = None
    numberOfTenderers: Optional[int] = None
    value: Optional[AmountResponse] = None
    tenderers: Optional[List[TendererResponse]] = None
    procuringEntity: Optional[ProcuringEntityResponse] = None
    sustainability: Optional[List[Any]] = None

class SupplierResponse(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None

class ContractingSocialResponse(BaseModel):
    description: Optional[str] = None
    laborObligations: Optional[Any] = None
    laborBudget: Optional[AmountResponse] = None

class ReleaseResponse(BaseModel):
    id: Optional[str] = None
    date: Optional[str] = None
    tag: Optional[Any] = None
    url: Optional[str] = None

class MilestoneResponse(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    dueDate: Optional[str] = None
    dateMet: Optional[str] = None
    value: Optional[AmountResponse] = None

class TransactionResponse(BaseModel):
    id: Optional[str] = None
    source: Optional[str] = None
    date: Optional[str] = None
    value: Optional[AmountResponse] = None
    payer: Optional[Dict[str, Any]] = None
    payee: Optional[Dict[str, Any]] = None
    uri: Optional[str] = None

class ModificationContractValueResponse(BaseModel):
    originalAmount: Optional[AmountResponse] = None
    amount: Optional[AmountResponse] = None

class ModificationResponse(BaseModel):
    id: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    rationale: Optional[str] = None
    type: Optional[str] = None
    releaseID: Optional[str] = None
    contractValue: Optional[ModificationContractValueResponse] = None

class ContractingDocumentResponse(BaseModel):
    id: Optional[str] = None
    documentType: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    datePublished: Optional[str] = None
    format: Optional[str] = None
    language: Optional[str] = None

class ContractingSummaryResponse(BaseModel):
    ocid: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    nature: Optional[Any] = None
    contractValue: Optional[AmountResponse] = None
    contractPeriod: Optional[PeriodResponse] = None
    tender: Optional[TenderResponse] = None
    suppliers: Optional[List[SupplierResponse]] = None
    social: Optional[ContractingSocialResponse] = None
    releases: Optional[List[ReleaseResponse]] = None
    milestones: Optional[List[MilestoneResponse]] = None
    transactions: Optional[List[TransactionResponse]] = None
    modifications: Optional[List[ModificationResponse]] = None
    documents: Optional[List[ContractingDocumentResponse]] = None

class ContractingProcessResponse(BaseModel):
    id: Optional[str] = None
    summary: Optional[ContractingSummaryResponse] = None

class DocumentResponse(BaseModel):
    id: Optional[str] = None
    documentType: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    datePublished: Optional[str] = None
    format: Optional[str] = None
    author: Optional[str] = None

class BudgetBreakdownItemResponse(BaseModel):
    id: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[AmountResponse] = None
    period: Optional[PeriodResponse] = None
    sourceParty: Optional[Dict[str, Any]] = None

class BudgetBreakdownResponse(BaseModel):
    id: Optional[str] = None
    description: Optional[str] = None
    breakdown: Optional[List[BudgetBreakdownItemResponse]] = None

class FinanceResponse(BaseModel):
    id: Optional[str] = None
    description: Optional[str] = None
    assetClass: Optional[str] = None
    type: Optional[str] = None
    concessional: Optional[bool] = None
    value: Optional[AmountResponse] = None
    source: Optional[str] = None
    financingParty: Optional[Dict[str, Any]] = None
    interestRateMargin: Optional[float] = None
    period: Optional[PeriodResponse] = None
    paymentPeriod: Optional[PeriodResponse] = None

class BudgetResponse(BaseModel):
    count: Optional[int] = None
    amount: Optional[AmountFormattedResponse] = None
    approvalDate: Optional[str] = None
    breakdown: Optional[List[BudgetBreakdownResponse]] = None
    finance: Optional[List[FinanceResponse]] = None

class ProjectIdentifierResponse(BaseModel):
    scheme: Optional[str] = None
    id: Optional[str] = None

class RelatedProjectResponse(BaseModel):
    id: Optional[str] = None
    relationship: Optional[List[str]] = None
    title: Optional[str] = None
    scheme: Optional[str] = None
    uri: Optional[str] = None

class CostItemResponse(BaseModel):
    id: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[AmountResponse] = None

class CostGroupResponse(BaseModel):
    id: Optional[str] = None
    description: Optional[str] = None
    breakdown: Optional[List[CostItemResponse]] = None

class CostMeasurementResponse(BaseModel):
    id: Optional[str] = None
    date: Optional[str] = None
    lifeCycleCost: Optional[AmountResponse] = None
    costBreakdown: Optional[List[CostGroupResponse]] = None

class ObservationResponse(BaseModel):
    id: Optional[str] = None
    measure: Optional[str] = None
    value: Optional[AmountResponse] = None
    unit: Optional[Dict[str, Any]] = None
    period: Optional[PeriodResponse] = None

class ForecastResponse(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    observations: Optional[List[ObservationResponse]] = None

class MetricResponse(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    observations: Optional[List[ObservationResponse]] = None

class ConsultationMeetingResponse(BaseModel):
    id: Optional[str] = None
    date: Optional[str] = None
    numberOfParticipants: Optional[int] = None
    address: Optional[AddressResponse] = None
    publicOffice: Optional[Dict[str, Any]] = None

class SocialResponse(BaseModel):
    inIndigenousLand: Optional[bool] = None
    consultationMeetings: Optional[List[ConsultationMeetingResponse]] = None
    landCompensationBudget: Optional[AmountResponse] = None
    healthAndSafety: Optional[Dict[str, Any]] = None

class ConservationMeasureResponse(BaseModel):
    type: Optional[str] = None
    description: Optional[str] = None

class EnvironmentResponse(BaseModel):
    hasImpactAssessment: Optional[bool] = None
    inProtectedArea: Optional[bool] = None
    abatementCost: Optional[AmountResponse] = None
    goals: Optional[List[str]] = None
    climateOversightTypes: Optional[List[str]] = None
    conservationMeasures: Optional[List[ConservationMeasureResponse]] = None
    environmentalMeasures: Optional[List[ConservationMeasureResponse]] = None
    climateMeasures: Optional[List[Dict[str, Any]]] = None
    impactCategories: Optional[List[Dict[str, Any]]] = None

class BeneficiaryResponse(BaseModel):
    description: Optional[str] = None
    numberOfPeople: Optional[int] = None

class BenefitResponse(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    beneficiaries: Optional[List[BeneficiaryResponse]] = None

class CompletionResponse(BaseModel):
    endDate: Optional[str] = None
    finalScope: Optional[str] = None
    finalValue: Optional[AmountResponse] = None

class LobbyingMeetingResponse(BaseModel):
    id: Optional[str] = None
    date: Optional[str] = None
    numberOfParticipants: Optional[int] = None
    address: Optional[AddressResponse] = None
    publicOffice: Optional[Dict[str, Any]] = None

class PolicyAlignmentResponse(BaseModel):
    policies: Optional[List[str]] = None
    description: Optional[str] = None

class AssetLifetimeResponse(BaseModel):
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    maxExtentDate: Optional[str] = None
    durationInDays: Optional[int] = None

class RiskFactorDetailResponse(BaseModel):
    risk_factor_id: Optional[int] = None
    factor_name: Optional[str] = None

class CategoryDriverResponse(BaseModel):
    risk_category_id: Optional[str] = None
    risk_category_code: Optional[str] = None
    category_name: Optional[str] = None
    driven_by_risk_factors: Optional[List[RiskFactorDetailResponse]] = None

class MitigationHandlingResponse(BaseModel):
    action: Optional[str] = None
    status: Optional[str] = None

class RiskResponse(BaseModel):
    risk_id: Optional[int] = None
    title: Optional[str] = None
    phase: Optional[str] = None
    category_drivers: Optional[List[CategoryDriverResponse]] = None
    mitigation_handling: Optional[List[MitigationHandlingResponse]] = None
    impact_statement: Optional[List[str]] = None

class ProjectDetailResponse(BaseModel):
    """Full project detail in OC4IDS format"""
    id: str = Field(..., description="Project UUID")
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    purpose: Optional[str] = None
    updated: Optional[str] = None
    type: Optional[str] = None

    publicAuthority: Optional[PublicAuthorityResponse] = None
    sector: Optional[List[str]] = None
    additionalClassifications: Optional[List[AdditionalClassificationResponse]] = None
    locations: Optional[List[LocationResponse]] = None
    parties: Optional[List[PartyResponse]] = None
    contractingProcesses: Optional[List[ContractingProcessResponse]] = None
    documents: Optional[List[DocumentResponse]] = None
    budget: Optional[BudgetResponse] = None
    identifiers: Optional[List[ProjectIdentifierResponse]] = None
    relatedProjects: Optional[List[RelatedProjectResponse]] = None
    costMeasurements: Optional[List[CostMeasurementResponse]] = None
    forecasts: Optional[List[ForecastResponse]] = None
    metrics: Optional[List[MetricResponse]] = None
    social: Optional[SocialResponse] = None
    environment: Optional[EnvironmentResponse] = None
    benefits: Optional[List[BenefitResponse]] = None
    completion: Optional[CompletionResponse] = None
    lobbyingMeetings: Optional[List[LobbyingMeetingResponse]] = None
    policyAlignment: Optional[PolicyAlignmentResponse] = None
    assetLifetime: Optional[AssetLifetimeResponse] = None
    risks: Optional[List[RiskResponse]] = None

    # Period fields (dynamic from DB)
    period: Optional[PeriodResponse] = None
    identificationPeriod: Optional[PeriodResponse] = None
    preparationPeriod: Optional[PeriodResponse] = None
    implementationPeriod: Optional[PeriodResponse] = None
    completionPeriod: Optional[PeriodResponse] = None
    maintenancePeriod: Optional[PeriodResponse] = None
    decommissioningPeriod: Optional[PeriodResponse] = None

    model_config = {"extra": "allow"}


# ============================================================================
#  POST /projects  — Create Project
# ============================================================================

class CreateProjectResponse(BaseModel):
    """Response after successfully creating a project"""
    status: str = Field(..., description="Operation status", examples=["success"])
    project_id: Optional[str] = Field(None, description="UUID of the created project")
    title: Optional[str] = Field(None, description="Project title")
    message: Optional[str] = Field(None, description="Additional message")
    warnings: Optional[List[str]] = Field(None, description="Non-fatal validation warnings")

    model_config = {"extra": "allow"}


# ============================================================================
#  PUT /projects/{project_id}  — Update Project
# ============================================================================

class UpdateProjectResponse(CreateProjectResponse):
    """Response after updating a project (same shape as create)"""
    pass


# ============================================================================
#  DELETE /projects/{project_id}
# ============================================================================

class DeleteProjectResponse(BaseModel):
    """Response after deleting a project"""
    message: str = Field(..., description="Confirmation message", examples=["Project deleted successfully"])


# ============================================================================
#  POST /upload  — File Upload
# ============================================================================

class UploadResultItem(BaseModel):
    """Result of a single project within a batch upload"""
    status: Optional[str] = None
    project_id: Optional[str] = None
    title: Optional[str] = None
    error: Optional[str] = None
    project_title: Optional[str] = None

    model_config = {"extra": "allow"}

class UploadResponse(BaseModel):
    """Response from file upload endpoint"""
    status: str = Field(..., description="Overall status: success, partial_success, or error")
    results: Optional[List[UploadResultItem]] = Field(None, description="Per-project results (batch upload)")

    model_config = {"extra": "allow"}


# ============================================================================
#  GET /summary  — Dashboard Summary
# ============================================================================

class SummaryStatsResponse(BaseModel):
    """High-level aggregated statistics"""
    totalProjects: int = Field(..., description="Total number of projects", examples=[150])
    uniqueContractors: int = Field(..., description="Number of unique contractors", examples=[42])
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

class HeatmapRiskItem(BaseModel):
    """Risk heatmap cell data"""
    model_config = {"extra": "allow"}

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
    heatmapRisk: Optional[List[Any]] = Field(None, description="Risk heatmap data")


# ============================================================================
#  GET /info  — Reference Data (Dropdowns)
# ============================================================================

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

# RiskSourceResponse is now a dynamic dictionary where keys are country names (e.g., 'global', 'thailand')
RiskSourceResponse = Dict[str, List[ReferenceItem]]

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


# ============================================================================
#  GET /compare  — Compare Projects
# ============================================================================

# Uses List[ProjectDetailResponse] directly


# ============================================================================
#  GET /api/debug/reset-db
# ============================================================================

class DebugResetResponse(BaseModel):
    """Response from database reset"""
    status: str = Field(..., description="Operation status", examples=["success"])
    message: str = Field(..., description="Result message", examples=["Database reset successfully."])


# ============================================================================
#  Error Responses
# ============================================================================

class ErrorDetail(BaseModel):
    """Standard error detail"""
    detail: str = Field(..., description="Error description")

class ValidationErrorResponse(BaseModel):
    """422 Validation error response"""
    detail: List[Dict[str, Any]] = Field(..., description="List of validation errors")
