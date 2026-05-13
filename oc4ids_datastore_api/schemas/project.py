"""
Project Schemas (DTOs)

Request / Response models for project CRUD & upload endpoints.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from oc4ids_datastore_api.schemas.common import (
    AmountResponse,
    AmountFormattedResponse,
    PeriodResponse,
    AddressResponse,
    IdentifierResponse,
    ContactPointResponse,
    PaginationResponse,
)


# ---------------------------------------------------------------------------
# GET /projects — List
# ---------------------------------------------------------------------------

class ProjectListItem(BaseModel):
    """A summarised project in the list view"""
    id: str = Field(..., description="Project UUID", examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"])
    title: Optional[str] = Field(None, description="Project title")
    ministry: Optional[List[str]] = Field(None, description="List of associated ministries")
    public_authority: Optional[str] = Field(None, description="Public authority / agency name")
    private_parties: Optional[List[str]] = Field(None, description="Private parties involved")
    sector: Optional[List[str]] = Field(None, description="Sector names")
    concession: Optional[List[str]] = Field(None, description="Concession form names")
    contract_type: Optional[List[str]] = Field(None, description="Ownership arrangement types (รูปแบบการจัดสรรกรรมสิทธิ์)")
    start_date: Optional[Any] = Field(None, description="Project start date")


class ProjectListResponse(BaseModel):
    """Paginated list of projects"""
    data: List[ProjectListItem] = Field(..., description="Array of project summary items")
    pagination: PaginationResponse


# ---------------------------------------------------------------------------
# GET /projects/{project_id} — Detail (OC4IDS format)
# ---------------------------------------------------------------------------

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
    description: Optional[List[str]] = None
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


# ---------------------------------------------------------------------------
# POST /projects — Create / PUT — Update (request body)
# ---------------------------------------------------------------------------

class ProjectUpsertPublicAuthority(BaseModel):
    """Public authority info inside an upsert payload."""
    name: Optional[str] = Field(None, description="Public authority name (looked up against the agency reference table)")

    model_config = {"extra": "allow"}


class ProjectUpsertRequest(BaseModel):
    """
    Request body for POST /projects and PUT /projects/{id}.

    Validates the small set of fields the service unconditionally reads
    (so a missing `type` returns 422 instead of a 500 KeyError) while
    leaving the rest of the OC4IDS payload (~50 nested sections) untyped
    via `extra=allow`. Documented optional fields are surfaced in the
    OpenAPI spec as a hint to API consumers.
    """

    id: Optional[str] = Field(
        None,
        description="Project UUID. If invalid or omitted, the server generates one.",
        examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"],
    )
    title: str = Field(
        ...,
        min_length=1,
        description="Project title (required).",
        examples=["โครงการทางหลวงพิเศษระหว่างเมือง สาย กรุงเทพ–นครราชสีมา"],
    )
    type: str = Field(
        ...,
        min_length=1,
        description="Project type code (required). Looked up against the project_type reference table; created on the fly if unseen.",
        examples=["หมวดการขนส่ง"],
    )
    description: Optional[str] = Field(None, description="Free-text project description")
    status: Optional[str] = Field(None, description="Project status", examples=["planned", "inProgress", "completed"])
    purpose: Optional[str] = None

    publicAuthority: Optional[ProjectUpsertPublicAuthority] = Field(
        None,
        description="Government agency that owns the project. Auto-resolved to a ministry when the name matches.",
    )
    period: Optional[Dict[str, Any]] = Field(
        None,
        description="Overall project period (`startDate`, `endDate`, `durationInDays`).",
    )
    sector: Optional[List[Any]] = Field(
        None,
        description="List of sector codes (string) or `{id: code}` objects. Unknown codes are logged and skipped.",
    )
    parties: Optional[List[Dict[str, Any]]] = Field(None, description="OC4IDS parties array")
    budget: Optional[Dict[str, Any]] = Field(None, description="OC4IDS budget object")
    contractingProcesses: Optional[List[Dict[str, Any]]] = Field(None, description="OC4IDS contracting processes")
    risks: Optional[List[Dict[str, Any]]] = Field(None, description="Risk register entries")

    # Allow any other OC4IDS field (locations, documents, identifiers, etc.)
    # without requiring a typed model for each — the service layer handles them.
    model_config = {"extra": "allow"}


# ---------------------------------------------------------------------------
# POST /projects — Create / PUT — Update / DELETE (responses)
# ---------------------------------------------------------------------------

class CreateProjectResponse(BaseModel):
    """Response after successfully creating a project"""
    status: str = Field(..., description="Operation status", examples=["success"])
    project_id: Optional[str] = Field(None, description="UUID of the created project")
    title: Optional[str] = Field(None, description="Project title")
    message: Optional[str] = Field(None, description="Additional message")
    warnings: Optional[List[str]] = Field(None, description="Non-fatal validation warnings")

    model_config = {"extra": "allow"}


class UpdateProjectResponse(CreateProjectResponse):
    """Response after updating a project (same shape as create)"""
    pass


class DeleteProjectResponse(BaseModel):
    """Response after deleting a project"""
    message: str = Field(..., description="Confirmation message", examples=["Project deleted successfully"])


# ---------------------------------------------------------------------------
# POST /upload — File Upload
# ---------------------------------------------------------------------------

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
