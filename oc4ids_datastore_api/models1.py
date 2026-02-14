from typing import Optional
import datetime
import uuid

from sqlalchemy import Boolean, Column, Date, DateTime, Double, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, Table, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class AdditionalClassifications(Base):
    __tablename__ = 'additional_classifications'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='additional_classifications_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scheme: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    uri: Mapped[Optional[str]] = mapped_column(String)

    project: Mapped[list['Projects']] = relationship('Projects', secondary='project_additional_classifications', back_populates='classification')


class Currencies(Base):
    __tablename__ = 'currencies'
    __table_args__ = (
        PrimaryKeyConstraint('code', name='currencies_pkey'),
    )

    code: Mapped[str] = mapped_column(String(3), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    symbol: Mapped[Optional[str]] = mapped_column(String)


class Ministry(Base):
    __tablename__ = 'ministry'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='ministry_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_th: Mapped[str] = mapped_column(String, nullable=False)
    name_en: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    agency: Mapped[list['Agency']] = relationship('Agency', back_populates='ministry')
    party_additional_identifiers: Mapped[list['PartyAdditionalIdentifiers']] = relationship('PartyAdditionalIdentifiers', back_populates='legal_name')


class PeriodTypes(Base):
    __tablename__ = 'period_types'
    __table_args__ = (
        PrimaryKeyConstraint('code', name='period_types_pkey'),
    )

    code: Mapped[str] = mapped_column(String, primary_key=True)
    name_en: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    name_th: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)
    sequence: Mapped[Optional[int]] = mapped_column(Integer)

    project_periods: Mapped[list['ProjectPeriods']] = relationship('ProjectPeriods', back_populates='period_types')


class ProjectType(Base):
    __tablename__ = 'project_type'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='project_type_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String, nullable=False)
    scheme: Mapped[Optional[str]] = mapped_column(String)
    name_th: Mapped[Optional[str]] = mapped_column(String)
    name_en: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)

    projects: Mapped[list['Projects']] = relationship('Projects', back_populates='project_type')


class Sector(Base):
    __tablename__ = 'sector'
    __table_args__ = (
        ForeignKeyConstraint(['parent_id'], ['sector.id'], name='sector_parent_id_fkey'),
        PrimaryKeyConstraint('id', name='sector_pkey'),
        UniqueConstraint('code', name='sector_code_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String, nullable=False)
    name_th: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer)
    name_en: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    parent: Mapped[Optional['Sector']] = relationship('Sector', remote_side=[id], back_populates='parent_reverse')
    parent_reverse: Mapped[list['Sector']] = relationship('Sector', remote_side=[parent_id], back_populates='parent')
    project: Mapped[list['Projects']] = relationship('Projects', secondary='project_sector', back_populates='sector')


class Agency(Base):
    __tablename__ = 'agency'
    __table_args__ = (
        ForeignKeyConstraint(['ministry_id'], ['ministry.id'], name='agency_ministry_id_fkey'),
        PrimaryKeyConstraint('id', name='agency_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_th: Mapped[str] = mapped_column(String, nullable=False)
    name_en: Mapped[Optional[str]] = mapped_column(String)
    ministry_id: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    ministry: Mapped[Optional['Ministry']] = relationship('Ministry', back_populates='agency')
    projects: Mapped[list['Projects']] = relationship('Projects', back_populates='public_authority')
    project_parties: Mapped[list['ProjectParties']] = relationship('ProjectParties', back_populates='identifier_legal_name')


class Projects(Base):
    __tablename__ = 'projects'
    __table_args__ = (
        ForeignKeyConstraint(['project_type_id'], ['project_type.id'], name='projects_project_type_id_fkey'),
        ForeignKeyConstraint(['public_authority_id'], ['agency.id'], name='projects_public_authority_id_fkey'),
        PrimaryKeyConstraint('id', name='projects_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[Optional[str]] = mapped_column(String)
    purpose: Mapped[Optional[str]] = mapped_column(String)
    project_type_id: Mapped[Optional[int]] = mapped_column(Integer)
    public_authority_id: Mapped[Optional[int]] = mapped_column(Integer)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    classification: Mapped[list['AdditionalClassifications']] = relationship('AdditionalClassifications', secondary='project_additional_classifications', back_populates='project')
    project_type: Mapped[Optional['ProjectType']] = relationship('ProjectType', back_populates='projects')
    public_authority: Mapped[Optional['Agency']] = relationship('Agency', back_populates='projects')
    sector: Mapped[list['Sector']] = relationship('Sector', secondary='project_sector', back_populates='project')
    project_benefits: Mapped[list['ProjectBenefits']] = relationship('ProjectBenefits', back_populates='project')
    project_budgets: Mapped[list['ProjectBudgets']] = relationship('ProjectBudgets', back_populates='project')
    project_contracting_processes: Mapped[list['ProjectContractingProcesses']] = relationship('ProjectContractingProcesses', back_populates='project')
    project_cost_measurements: Mapped[list['ProjectCostMeasurements']] = relationship('ProjectCostMeasurements', back_populates='project')
    project_documents: Mapped[list['ProjectDocuments']] = relationship('ProjectDocuments', back_populates='project')
    project_forecasts: Mapped[list['ProjectForecasts']] = relationship('ProjectForecasts', back_populates='project')
    project_identifiers: Mapped[list['ProjectIdentifiers']] = relationship('ProjectIdentifiers', back_populates='project')
    project_lobbying_meetings: Mapped[list['ProjectLobbyingMeetings']] = relationship('ProjectLobbyingMeetings', back_populates='project')
    project_locations: Mapped[list['ProjectLocations']] = relationship('ProjectLocations', back_populates='project')
    project_metrics: Mapped[list['ProjectMetrics']] = relationship('ProjectMetrics', back_populates='project')
    project_parties: Mapped[list['ProjectParties']] = relationship('ProjectParties', back_populates='project')
    project_periods: Mapped[list['ProjectPeriods']] = relationship('ProjectPeriods', back_populates='project')
    project_related_projects: Mapped[list['ProjectRelatedProjects']] = relationship('ProjectRelatedProjects', back_populates='project')


t_project_additional_classifications = Table(
    'project_additional_classifications', Base.metadata,
    Column('project_id', Uuid, primary_key=True),
    Column('classification_id', Integer, primary_key=True),
    ForeignKeyConstraint(['classification_id'], ['additional_classifications.id'], name='project_additional_classifications_classification_id_fkey'),
    ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_additional_classifications_project_id_fkey'),
    PrimaryKeyConstraint('project_id', 'classification_id', name='project_additional_classifications_pkey')
)


class ProjectAssetLifetime(Projects):
    __tablename__ = 'project_asset_lifetime'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_asset_lifetime_project_id_fkey'),
        PrimaryKeyConstraint('project_id', name='project_asset_lifetime_pkey')
    )

    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    period_start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    period_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    period_max_extent_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    period_duration_days: Mapped[Optional[int]] = mapped_column(Integer)


class ProjectBenefits(Base):
    __tablename__ = 'project_benefits'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_benefits_project_id_fkey'),
        PrimaryKeyConstraint('id', name='project_benefits_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)

    project: Mapped['Projects'] = relationship('Projects', back_populates='project_benefits')
    benefit_beneficiaries: Mapped[list['BenefitBeneficiaries']] = relationship('BenefitBeneficiaries', back_populates='benefit')


class ProjectBudgets(Base):
    __tablename__ = 'project_budgets'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_budgets_project_id_fkey'),
        PrimaryKeyConstraint('id', name='project_budgets_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    total_amount: Mapped[Optional[float]] = mapped_column(Double(53))
    currency: Mapped[Optional[str]] = mapped_column(String)
    request_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    approval_date: Mapped[Optional[datetime.date]] = mapped_column(Date)

    project: Mapped['Projects'] = relationship('Projects', back_populates='project_budgets')
    budget_breakdowns: Mapped[list['BudgetBreakdowns']] = relationship('BudgetBreakdowns', back_populates='budget')
    project_finance: Mapped[list['ProjectFinance']] = relationship('ProjectFinance', back_populates='budget')


class ProjectCompletion(Projects):
    __tablename__ = 'project_completion'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_completion_project_id_fkey'),
        PrimaryKeyConstraint('project_id', name='project_completion_pkey')
    )

    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    end_date_details: Mapped[Optional[str]] = mapped_column(String)
    final_scope: Mapped[Optional[str]] = mapped_column(String)
    final_scope_details: Mapped[Optional[str]] = mapped_column(String)
    final_value_amount: Mapped[Optional[float]] = mapped_column(Double(53))
    final_value_currency: Mapped[Optional[str]] = mapped_column(String)


class ProjectContractingProcesses(Base):
    __tablename__ = 'project_contracting_processes'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_contracting_processes_project_id_fkey'),
        PrimaryKeyConstraint('id', name='project_contracting_processes_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    ocid: Mapped[Optional[str]] = mapped_column(String)
    external_reference: Mapped[Optional[str]] = mapped_column(String)
    title: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[Optional[str]] = mapped_column(String)
    nature: Mapped[Optional[dict]] = mapped_column(JSONB)
    contract_amount: Mapped[Optional[float]] = mapped_column(Double(53))
    contract_currency: Mapped[Optional[str]] = mapped_column(String)
    final_amount: Mapped[Optional[float]] = mapped_column(Double(53))
    final_currency: Mapped[Optional[str]] = mapped_column(String)
    period_start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    period_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    period_max_extent_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    period_duration_days: Mapped[Optional[int]] = mapped_column(Integer)

    project: Mapped['Projects'] = relationship('Projects', back_populates='project_contracting_processes')
    contracting_documents: Mapped[list['ContractingDocuments']] = relationship('ContractingDocuments', back_populates='process')
    contracting_milestones: Mapped[list['ContractingMilestones']] = relationship('ContractingMilestones', back_populates='process')
    contracting_modifications: Mapped[list['ContractingModifications']] = relationship('ContractingModifications', back_populates='process')
    contracting_releases: Mapped[list['ContractingReleases']] = relationship('ContractingReleases', back_populates='process')
    contracting_suppliers: Mapped[list['ContractingSuppliers']] = relationship('ContractingSuppliers', back_populates='process')
    contracting_transactions: Mapped[list['ContractingTransactions']] = relationship('ContractingTransactions', back_populates='process')


class ProjectCostMeasurements(Base):
    __tablename__ = 'project_cost_measurements'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_cost_measurements_project_id_fkey'),
        PrimaryKeyConstraint('id', name='project_cost_measurements_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    measurement_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    lifecycle_cost_amount: Mapped[Optional[float]] = mapped_column(Double(53))
    lifecycle_cost_currency: Mapped[Optional[str]] = mapped_column(String)

    project: Mapped['Projects'] = relationship('Projects', back_populates='project_cost_measurements')
    cost_groups: Mapped[list['CostGroups']] = relationship('CostGroups', back_populates='cost_measurement')


class ProjectDocuments(Base):
    __tablename__ = 'project_documents'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_documents_project_id_fkey'),
        PrimaryKeyConstraint('id', name='project_documents_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    document_type: Mapped[Optional[str]] = mapped_column(String)
    title: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)
    url: Mapped[Optional[str]] = mapped_column(String)
    date_published: Mapped[Optional[datetime.date]] = mapped_column(Date)
    date_modified: Mapped[Optional[datetime.date]] = mapped_column(Date)
    format: Mapped[Optional[str]] = mapped_column(String)
    language: Mapped[Optional[str]] = mapped_column(String)
    page_start: Mapped[Optional[str]] = mapped_column(String)
    page_end: Mapped[Optional[str]] = mapped_column(String)
    access_details: Mapped[Optional[str]] = mapped_column(String)
    author: Mapped[Optional[str]] = mapped_column(String)

    project: Mapped['Projects'] = relationship('Projects', back_populates='project_documents')


class ProjectEnvironment(Projects):
    __tablename__ = 'project_environment'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_environment_project_id_fkey'),
        PrimaryKeyConstraint('project_id', name='project_environment_pkey')
    )

    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    has_impact_assessment: Mapped[Optional[bool]] = mapped_column(Boolean)
    in_protected_area: Mapped[Optional[bool]] = mapped_column(Boolean)
    abatement_cost_amount: Mapped[Optional[float]] = mapped_column(Double(53))
    abatement_cost_currency: Mapped[Optional[str]] = mapped_column(String)

    environment_climate_measures: Mapped[list['EnvironmentClimateMeasures']] = relationship('EnvironmentClimateMeasures', back_populates='project')
    environment_climate_oversight_types: Mapped[list['EnvironmentClimateOversightTypes']] = relationship('EnvironmentClimateOversightTypes', back_populates='project')
    environment_conservation_measures: Mapped[list['EnvironmentConservationMeasures']] = relationship('EnvironmentConservationMeasures', back_populates='project')
    environment_environmental_measures: Mapped[list['EnvironmentEnvironmentalMeasures']] = relationship('EnvironmentEnvironmentalMeasures', back_populates='project')
    environment_goals: Mapped[list['EnvironmentGoals']] = relationship('EnvironmentGoals', back_populates='project')
    environment_impact_categories: Mapped[list['EnvironmentImpactCategories']] = relationship('EnvironmentImpactCategories', back_populates='project')


class ProjectForecasts(Base):
    __tablename__ = 'project_forecasts'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_forecasts_project_id_fkey'),
        PrimaryKeyConstraint('id', name='project_forecasts_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)

    project: Mapped['Projects'] = relationship('Projects', back_populates='project_forecasts')
    forecast_observations: Mapped[list['ForecastObservations']] = relationship('ForecastObservations', back_populates='forecast')


class ProjectIdentifiers(Base):
    __tablename__ = 'project_identifiers'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_identifiers_project_id_fkey'),
        PrimaryKeyConstraint('id', name='project_identifiers_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    identifier_value: Mapped[str] = mapped_column(String, nullable=False)
    scheme: Mapped[Optional[str]] = mapped_column(String)

    project: Mapped['Projects'] = relationship('Projects', back_populates='project_identifiers')


class ProjectLobbyingMeetings(Base):
    __tablename__ = 'project_lobbying_meetings'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_lobbying_meetings_project_id_fkey'),
        PrimaryKeyConstraint('id', name='project_lobbying_meetings_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    meeting_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    number_of_participants: Mapped[Optional[int]] = mapped_column(Integer)
    street_address: Mapped[Optional[str]] = mapped_column(String)
    locality: Mapped[Optional[str]] = mapped_column(String)
    region: Mapped[Optional[str]] = mapped_column(String)
    postal_code: Mapped[Optional[str]] = mapped_column(String)
    country_name: Mapped[Optional[str]] = mapped_column(String)
    public_office_job_title: Mapped[Optional[str]] = mapped_column(String)
    public_office_person_name: Mapped[Optional[str]] = mapped_column(String)
    public_office_org_id: Mapped[Optional[str]] = mapped_column(String)
    public_office_org_name: Mapped[Optional[str]] = mapped_column(String)

    project: Mapped['Projects'] = relationship('Projects', back_populates='project_lobbying_meetings')


class ProjectLocations(Base):
    __tablename__ = 'project_locations'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_locations_project_id_fkey'),
        PrimaryKeyConstraint('id', name='project_locations_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    uri: Mapped[Optional[str]] = mapped_column(String)
    geometry_type: Mapped[Optional[str]] = mapped_column(String)
    geometry_coordinates: Mapped[Optional[dict]] = mapped_column(JSONB)
    street_address: Mapped[Optional[str]] = mapped_column(String)
    locality: Mapped[Optional[str]] = mapped_column(String)
    region: Mapped[Optional[str]] = mapped_column(String)
    postal_code: Mapped[Optional[str]] = mapped_column(String)
    country_name: Mapped[Optional[str]] = mapped_column(String)

    project: Mapped['Projects'] = relationship('Projects', back_populates='project_locations')
    location_gazetteers: Mapped[list['LocationGazetteers']] = relationship('LocationGazetteers', back_populates='location')


class ProjectMetrics(Base):
    __tablename__ = 'project_metrics'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_metrics_project_id_fkey'),
        PrimaryKeyConstraint('id', name='project_metrics_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)

    project: Mapped['Projects'] = relationship('Projects', back_populates='project_metrics')
    metric_observations: Mapped[list['MetricObservations']] = relationship('MetricObservations', back_populates='metric')


class ProjectParties(Base):
    __tablename__ = 'project_parties'
    __table_args__ = (
        ForeignKeyConstraint(['identifier_legal_name_id'], ['agency.id'], name='project_parties_identifier_legal_name_id_fkey'),
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_parties_project_id_fkey'),
        PrimaryKeyConstraint('id', name='project_parties_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String)
    identifier_scheme: Mapped[Optional[str]] = mapped_column(String)
    identifier_value: Mapped[Optional[str]] = mapped_column(String)
    identifier_legal_name_id: Mapped[Optional[int]] = mapped_column(Integer)
    identifier_uri: Mapped[Optional[str]] = mapped_column(String)
    street_address: Mapped[Optional[str]] = mapped_column(String)
    locality: Mapped[Optional[str]] = mapped_column(String)
    region: Mapped[Optional[str]] = mapped_column(String)
    postal_code: Mapped[Optional[str]] = mapped_column(String)
    country_name: Mapped[Optional[str]] = mapped_column(String)
    contact_name: Mapped[Optional[str]] = mapped_column(String)
    contact_email: Mapped[Optional[str]] = mapped_column(String)
    contact_telephone: Mapped[Optional[str]] = mapped_column(String)
    contact_fax: Mapped[Optional[str]] = mapped_column(String)
    contact_url: Mapped[Optional[str]] = mapped_column(String)

    identifier_legal_name: Mapped[Optional['Agency']] = relationship('Agency', back_populates='project_parties')
    project: Mapped['Projects'] = relationship('Projects', back_populates='project_parties')
    party_additional_identifiers: Mapped[list['PartyAdditionalIdentifiers']] = relationship('PartyAdditionalIdentifiers', back_populates='party')
    party_beneficial_owners: Mapped[list['PartyBeneficialOwners']] = relationship('PartyBeneficialOwners', back_populates='party')
    party_classifications: Mapped[list['PartyClassifications']] = relationship('PartyClassifications', back_populates='party')
    party_people: Mapped[list['PartyPeople']] = relationship('PartyPeople', back_populates='party')
    party_roles: Mapped[list['PartyRoles']] = relationship('PartyRoles', back_populates='party')


class ProjectPeriods(Base):
    __tablename__ = 'project_periods'
    __table_args__ = (
        ForeignKeyConstraint(['period_type'], ['period_types.code'], name='project_periods_period_type_fkey'),
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_periods_project_id_fkey'),
        PrimaryKeyConstraint('id', name='project_periods_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    period_type: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    max_extent_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    duration_days: Mapped[Optional[int]] = mapped_column(Integer)

    period_types: Mapped['PeriodTypes'] = relationship('PeriodTypes', back_populates='project_periods')
    project: Mapped['Projects'] = relationship('Projects', back_populates='project_periods')


class ProjectPolicyAlignment(Projects):
    __tablename__ = 'project_policy_alignment'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_policy_alignment_project_id_fkey'),
        PrimaryKeyConstraint('project_id', name='project_policy_alignment_pkey')
    )

    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    description: Mapped[Optional[str]] = mapped_column(String)

    project_policy_alignment_policies: Mapped[list['ProjectPolicyAlignmentPolicies']] = relationship('ProjectPolicyAlignmentPolicies', back_populates='project')


class ProjectRelatedProjects(Base):
    __tablename__ = 'project_related_projects'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_related_projects_project_id_fkey'),
        PrimaryKeyConstraint('id', name='project_related_projects_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    relationship_id: Mapped[str] = mapped_column(String, nullable=False)
    identifier: Mapped[str] = mapped_column(String, nullable=False)
    relationship_: Mapped[str] = mapped_column('relationship', String, nullable=False)
    scheme: Mapped[Optional[str]] = mapped_column(String)
    title: Mapped[Optional[str]] = mapped_column(String)
    uri: Mapped[Optional[str]] = mapped_column(String)

    project: Mapped['Projects'] = relationship('Projects', back_populates='project_related_projects')


t_project_sector = Table(
    'project_sector', Base.metadata,
    Column('project_id', Uuid, primary_key=True),
    Column('sector_id', Integer, primary_key=True),
    ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_sector_project_id_fkey'),
    ForeignKeyConstraint(['sector_id'], ['sector.id'], name='project_sector_sector_id_fkey'),
    PrimaryKeyConstraint('project_id', 'sector_id', name='project_sector_pkey')
)


class ProjectSocial(Projects):
    __tablename__ = 'project_social'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_social_project_id_fkey'),
        PrimaryKeyConstraint('project_id', name='project_social_pkey')
    )

    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    in_indigenous_land: Mapped[Optional[bool]] = mapped_column(Boolean)
    land_compensation_amount: Mapped[Optional[float]] = mapped_column(Double(53))
    land_compensation_currency: Mapped[Optional[str]] = mapped_column(String)
    health_safety_material_test_description: Mapped[Optional[str]] = mapped_column(String)

    social_consultation_meetings: Mapped[list['SocialConsultationMeetings']] = relationship('SocialConsultationMeetings', back_populates='project')
    social_health_safety_material_tests: Mapped[list['SocialHealthSafetyMaterialTests']] = relationship('SocialHealthSafetyMaterialTests', back_populates='project')


class BenefitBeneficiaries(Base):
    __tablename__ = 'benefit_beneficiaries'
    __table_args__ = (
        ForeignKeyConstraint(['benefit_id'], ['project_benefits.id'], name='benefit_beneficiaries_benefit_id_fkey'),
        PrimaryKeyConstraint('id', name='benefit_beneficiaries_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    benefit_id: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    number_of_people: Mapped[Optional[int]] = mapped_column(Integer)
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    benefit: Mapped['ProjectBenefits'] = relationship('ProjectBenefits', back_populates='benefit_beneficiaries')


class BudgetBreakdowns(Base):
    __tablename__ = 'budget_breakdowns'
    __table_args__ = (
        ForeignKeyConstraint(['budget_id'], ['project_budgets.id'], name='budget_breakdowns_budget_id_fkey'),
        PrimaryKeyConstraint('id', name='budget_breakdowns_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    budget_id: Mapped[int] = mapped_column(Integer, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)

    budget: Mapped['ProjectBudgets'] = relationship('ProjectBudgets', back_populates='budget_breakdowns')
    budget_breakdown_items: Mapped[list['BudgetBreakdownItems']] = relationship('BudgetBreakdownItems', back_populates='breakdown')


class ContractingDocuments(Base):
    __tablename__ = 'contracting_documents'
    __table_args__ = (
        ForeignKeyConstraint(['process_id'], ['project_contracting_processes.id'], name='contracting_documents_process_id_fkey'),
        PrimaryKeyConstraint('id', name='contracting_documents_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    process_id: Mapped[int] = mapped_column(Integer, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    document_type: Mapped[Optional[str]] = mapped_column(String)
    title: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)
    url: Mapped[Optional[str]] = mapped_column(String)
    date_published: Mapped[Optional[datetime.date]] = mapped_column(Date)
    date_modified: Mapped[Optional[datetime.date]] = mapped_column(Date)
    format: Mapped[Optional[str]] = mapped_column(String)
    language: Mapped[Optional[str]] = mapped_column(String)
    page_start: Mapped[Optional[str]] = mapped_column(String)
    page_end: Mapped[Optional[str]] = mapped_column(String)
    access_details: Mapped[Optional[str]] = mapped_column(String)
    author: Mapped[Optional[str]] = mapped_column(String)

    process: Mapped['ProjectContractingProcesses'] = relationship('ProjectContractingProcesses', back_populates='contracting_documents')


class ContractingMilestones(Base):
    __tablename__ = 'contracting_milestones'
    __table_args__ = (
        ForeignKeyConstraint(['process_id'], ['project_contracting_processes.id'], name='contracting_milestones_process_id_fkey'),
        PrimaryKeyConstraint('id', name='contracting_milestones_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    process_id: Mapped[int] = mapped_column(Integer, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String)
    type: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)
    code: Mapped[Optional[str]] = mapped_column(String)
    due_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    date_met: Mapped[Optional[datetime.date]] = mapped_column(Date)
    date_modified: Mapped[Optional[datetime.date]] = mapped_column(Date)
    status: Mapped[Optional[str]] = mapped_column(String)
    value_amount: Mapped[Optional[float]] = mapped_column(Double(53))
    value_currency: Mapped[Optional[str]] = mapped_column(String)

    process: Mapped['ProjectContractingProcesses'] = relationship('ProjectContractingProcesses', back_populates='contracting_milestones')


class ContractingModifications(Base):
    __tablename__ = 'contracting_modifications'
    __table_args__ = (
        ForeignKeyConstraint(['process_id'], ['project_contracting_processes.id'], name='contracting_modifications_process_id_fkey'),
        PrimaryKeyConstraint('id', name='contracting_modifications_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    process_id: Mapped[int] = mapped_column(Integer, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    description: Mapped[Optional[str]] = mapped_column(String)
    rationale: Mapped[Optional[str]] = mapped_column(String)
    type: Mapped[Optional[str]] = mapped_column(String)
    release_id: Mapped[Optional[str]] = mapped_column(String)
    old_amount: Mapped[Optional[float]] = mapped_column(Double(53))
    old_currency: Mapped[Optional[str]] = mapped_column(String)
    new_amount: Mapped[Optional[float]] = mapped_column(Double(53))
    new_currency: Mapped[Optional[str]] = mapped_column(String)
    old_start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    old_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    new_start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    new_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)

    process: Mapped['ProjectContractingProcesses'] = relationship('ProjectContractingProcesses', back_populates='contracting_modifications')


class ContractingReleases(Base):
    __tablename__ = 'contracting_releases'
    __table_args__ = (
        ForeignKeyConstraint(['process_id'], ['project_contracting_processes.id'], name='contracting_releases_process_id_fkey'),
        PrimaryKeyConstraint('id', name='contracting_releases_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    process_id: Mapped[int] = mapped_column(Integer, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    tag: Mapped[Optional[dict]] = mapped_column(JSONB)
    date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    url: Mapped[Optional[str]] = mapped_column(String)

    process: Mapped['ProjectContractingProcesses'] = relationship('ProjectContractingProcesses', back_populates='contracting_releases')


class ContractingSocial(ProjectContractingProcesses):
    __tablename__ = 'contracting_social'
    __table_args__ = (
        ForeignKeyConstraint(['process_id'], ['project_contracting_processes.id'], name='contracting_social_process_id_fkey'),
        PrimaryKeyConstraint('process_id', name='contracting_social_pkey')
    )

    process_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    labor_budget_amount: Mapped[Optional[float]] = mapped_column(Double(53))
    labor_budget_currency: Mapped[Optional[str]] = mapped_column(String)
    labor_obligations: Mapped[Optional[dict]] = mapped_column(JSONB)
    labor_description: Mapped[Optional[str]] = mapped_column(String)


class ContractingSuppliers(Base):
    __tablename__ = 'contracting_suppliers'
    __table_args__ = (
        ForeignKeyConstraint(['process_id'], ['project_contracting_processes.id'], name='contracting_suppliers_process_id_fkey'),
        PrimaryKeyConstraint('id', name='contracting_suppliers_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    process_id: Mapped[int] = mapped_column(Integer, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String)

    process: Mapped['ProjectContractingProcesses'] = relationship('ProjectContractingProcesses', back_populates='contracting_suppliers')


class ContractingTenders(ProjectContractingProcesses):
    __tablename__ = 'contracting_tenders'
    __table_args__ = (
        ForeignKeyConstraint(['process_id'], ['project_contracting_processes.id'], name='contracting_tenders_process_id_fkey'),
        PrimaryKeyConstraint('process_id', name='contracting_tenders_pkey')
    )

    process_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    procurement_method: Mapped[Optional[str]] = mapped_column(String)
    procurement_method_details: Mapped[Optional[str]] = mapped_column(String)
    date_published: Mapped[Optional[datetime.date]] = mapped_column(Date)
    cost_estimate_amount: Mapped[Optional[float]] = mapped_column(Double(53))
    cost_estimate_currency: Mapped[Optional[str]] = mapped_column(String)
    number_of_tenderers: Mapped[Optional[int]] = mapped_column(Integer)

    contracting_tender_entities: Mapped[list['ContractingTenderEntities']] = relationship('ContractingTenderEntities', back_populates='process')
    contracting_tender_sustainability: Mapped[list['ContractingTenderSustainability']] = relationship('ContractingTenderSustainability', back_populates='process')
    contracting_tender_tenderers: Mapped[list['ContractingTenderTenderers']] = relationship('ContractingTenderTenderers', back_populates='process')


class ContractingTransactions(Base):
    __tablename__ = 'contracting_transactions'
    __table_args__ = (
        ForeignKeyConstraint(['process_id'], ['project_contracting_processes.id'], name='contracting_transactions_process_id_fkey'),
        PrimaryKeyConstraint('id', name='contracting_transactions_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    process_id: Mapped[int] = mapped_column(Integer, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String)
    date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    amount: Mapped[Optional[float]] = mapped_column(Double(53))
    currency: Mapped[Optional[str]] = mapped_column(String)
    payer_name: Mapped[Optional[str]] = mapped_column(String)
    payee_name: Mapped[Optional[str]] = mapped_column(String)
    uri: Mapped[Optional[str]] = mapped_column(String)

    process: Mapped['ProjectContractingProcesses'] = relationship('ProjectContractingProcesses', back_populates='contracting_transactions')


class CostGroups(Base):
    __tablename__ = 'cost_groups'
    __table_args__ = (
        ForeignKeyConstraint(['cost_measurement_id'], ['project_cost_measurements.id'], name='cost_groups_cost_measurement_id_fkey'),
        PrimaryKeyConstraint('id', name='cost_groups_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cost_measurement_id: Mapped[int] = mapped_column(Integer, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String)

    cost_measurement: Mapped['ProjectCostMeasurements'] = relationship('ProjectCostMeasurements', back_populates='cost_groups')
    cost_items: Mapped[list['CostItems']] = relationship('CostItems', back_populates='cost_group')


class EnvironmentClimateMeasures(Base):
    __tablename__ = 'environment_climate_measures'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['project_environment.project_id'], name='environment_climate_measures_project_id_fkey'),
        PrimaryKeyConstraint('id', name='environment_climate_measures_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)

    project: Mapped['ProjectEnvironment'] = relationship('ProjectEnvironment', back_populates='environment_climate_measures')


class EnvironmentClimateOversightTypes(Base):
    __tablename__ = 'environment_climate_oversight_types'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['project_environment.project_id'], name='environment_climate_oversight_types_project_id_fkey'),
        PrimaryKeyConstraint('project_id', 'oversight_type', name='environment_climate_oversight_types_pkey')
    )

    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    oversight_type: Mapped[str] = mapped_column(String, primary_key=True)

    project: Mapped['ProjectEnvironment'] = relationship('ProjectEnvironment', back_populates='environment_climate_oversight_types')


class EnvironmentConservationMeasures(Base):
    __tablename__ = 'environment_conservation_measures'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['project_environment.project_id'], name='environment_conservation_measures_project_id_fkey'),
        PrimaryKeyConstraint('id', name='environment_conservation_measures_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)

    project: Mapped['ProjectEnvironment'] = relationship('ProjectEnvironment', back_populates='environment_conservation_measures')


class EnvironmentEnvironmentalMeasures(Base):
    __tablename__ = 'environment_environmental_measures'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['project_environment.project_id'], name='environment_environmental_measures_project_id_fkey'),
        PrimaryKeyConstraint('id', name='environment_environmental_measures_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)

    project: Mapped['ProjectEnvironment'] = relationship('ProjectEnvironment', back_populates='environment_environmental_measures')


class EnvironmentGoals(Base):
    __tablename__ = 'environment_goals'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['project_environment.project_id'], name='environment_goals_project_id_fkey'),
        PrimaryKeyConstraint('project_id', 'goal', name='environment_goals_pkey')
    )

    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    goal: Mapped[str] = mapped_column(String, primary_key=True)

    project: Mapped['ProjectEnvironment'] = relationship('ProjectEnvironment', back_populates='environment_goals')


class EnvironmentImpactCategories(Base):
    __tablename__ = 'environment_impact_categories'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['project_environment.project_id'], name='environment_impact_categories_project_id_fkey'),
        PrimaryKeyConstraint('id', name='environment_impact_categories_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    scheme: Mapped[Optional[str]] = mapped_column(String)
    category_id: Mapped[Optional[str]] = mapped_column(String)

    project: Mapped['ProjectEnvironment'] = relationship('ProjectEnvironment', back_populates='environment_impact_categories')


class ForecastObservations(Base):
    __tablename__ = 'forecast_observations'
    __table_args__ = (
        ForeignKeyConstraint(['forecast_id'], ['project_forecasts.id'], name='forecast_observations_forecast_id_fkey'),
        PrimaryKeyConstraint('id', name='forecast_observations_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    forecast_id: Mapped[int] = mapped_column(Integer, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    measure: Mapped[Optional[str]] = mapped_column(String)
    notes: Mapped[Optional[str]] = mapped_column(String)
    value_amount: Mapped[Optional[float]] = mapped_column(Double(53))
    value_currency: Mapped[Optional[str]] = mapped_column(String)
    period_start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    period_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    period_max_extent_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    period_duration_days: Mapped[Optional[int]] = mapped_column(Integer)
    unit_name: Mapped[Optional[str]] = mapped_column(String)
    unit_scheme: Mapped[Optional[str]] = mapped_column(String)
    unit_id: Mapped[Optional[str]] = mapped_column(String)
    unit_uri: Mapped[Optional[str]] = mapped_column(String)
    dimensions: Mapped[Optional[dict]] = mapped_column(JSONB)

    forecast: Mapped['ProjectForecasts'] = relationship('ProjectForecasts', back_populates='forecast_observations')


class LocationGazetteers(Base):
    __tablename__ = 'location_gazetteers'
    __table_args__ = (
        ForeignKeyConstraint(['location_id'], ['project_locations.id'], name='location_gazetteers_location_id_fkey'),
        PrimaryKeyConstraint('id', name='location_gazetteers_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    scheme: Mapped[str] = mapped_column(String, nullable=False)

    location: Mapped['ProjectLocations'] = relationship('ProjectLocations', back_populates='location_gazetteers')
    location_gazetteer_identifiers: Mapped[list['LocationGazetteerIdentifiers']] = relationship('LocationGazetteerIdentifiers', back_populates='gazetteer')


class MetricObservations(Base):
    __tablename__ = 'metric_observations'
    __table_args__ = (
        ForeignKeyConstraint(['metric_id'], ['project_metrics.id'], name='metric_observations_metric_id_fkey'),
        PrimaryKeyConstraint('id', name='metric_observations_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    metric_id: Mapped[int] = mapped_column(Integer, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    measure: Mapped[Optional[str]] = mapped_column(String)
    notes: Mapped[Optional[str]] = mapped_column(String)
    value_amount: Mapped[Optional[float]] = mapped_column(Double(53))
    value_currency: Mapped[Optional[str]] = mapped_column(String)
    period_start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    period_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    period_max_extent_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    period_duration_days: Mapped[Optional[int]] = mapped_column(Integer)
    unit_name: Mapped[Optional[str]] = mapped_column(String)
    unit_scheme: Mapped[Optional[str]] = mapped_column(String)
    unit_id: Mapped[Optional[str]] = mapped_column(String)
    unit_uri: Mapped[Optional[str]] = mapped_column(String)
    dimensions: Mapped[Optional[dict]] = mapped_column(JSONB)

    metric: Mapped['ProjectMetrics'] = relationship('ProjectMetrics', back_populates='metric_observations')


class PartyAdditionalIdentifiers(Base):
    __tablename__ = 'party_additional_identifiers'
    __table_args__ = (
        ForeignKeyConstraint(['legal_name_id'], ['ministry.id'], name='party_additional_identifiers_legal_name_id_fkey'),
        ForeignKeyConstraint(['party_id'], ['project_parties.id'], name='party_additional_identifiers_party_id_fkey'),
        PrimaryKeyConstraint('id', name='party_additional_identifiers_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    party_id: Mapped[int] = mapped_column(Integer, nullable=False)
    scheme: Mapped[Optional[str]] = mapped_column(String)
    identifier: Mapped[Optional[str]] = mapped_column(String)
    legal_name_id: Mapped[Optional[int]] = mapped_column(Integer)
    uri: Mapped[Optional[str]] = mapped_column(String)

    legal_name: Mapped[Optional['Ministry']] = relationship('Ministry', back_populates='party_additional_identifiers')
    party: Mapped['ProjectParties'] = relationship('ProjectParties', back_populates='party_additional_identifiers')


class PartyBeneficialOwners(Base):
    __tablename__ = 'party_beneficial_owners'
    __table_args__ = (
        ForeignKeyConstraint(['party_id'], ['project_parties.id'], name='party_beneficial_owners_party_id_fkey'),
        PrimaryKeyConstraint('id', name='party_beneficial_owners_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    party_id: Mapped[int] = mapped_column(Integer, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String)
    email: Mapped[Optional[str]] = mapped_column(String)
    telephone: Mapped[Optional[str]] = mapped_column(String)
    fax_number: Mapped[Optional[str]] = mapped_column(String)
    identifier_scheme: Mapped[Optional[str]] = mapped_column(String)
    identifier_value: Mapped[Optional[str]] = mapped_column(String)
    street_address: Mapped[Optional[str]] = mapped_column(String)
    locality: Mapped[Optional[str]] = mapped_column(String)
    region: Mapped[Optional[str]] = mapped_column(String)
    postal_code: Mapped[Optional[str]] = mapped_column(String)
    country_name: Mapped[Optional[str]] = mapped_column(String)

    party: Mapped['ProjectParties'] = relationship('ProjectParties', back_populates='party_beneficial_owners')
    beneficial_owner_nationalities: Mapped[list['BeneficialOwnerNationalities']] = relationship('BeneficialOwnerNationalities', back_populates='owner')


class PartyClassifications(Base):
    __tablename__ = 'party_classifications'
    __table_args__ = (
        ForeignKeyConstraint(['party_id'], ['project_parties.id'], name='party_classifications_party_id_fkey'),
        PrimaryKeyConstraint('party_id', 'scheme', 'classification_id', name='party_classifications_pkey')
    )

    party_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scheme: Mapped[str] = mapped_column(String, primary_key=True)
    classification_id: Mapped[str] = mapped_column(String, primary_key=True)

    party: Mapped['ProjectParties'] = relationship('ProjectParties', back_populates='party_classifications')


class PartyPeople(Base):
    __tablename__ = 'party_people'
    __table_args__ = (
        ForeignKeyConstraint(['party_id'], ['project_parties.id'], name='party_people_party_id_fkey'),
        PrimaryKeyConstraint('id', name='party_people_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    party_id: Mapped[int] = mapped_column(Integer, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String)
    job_title: Mapped[Optional[str]] = mapped_column(String)

    party: Mapped['ProjectParties'] = relationship('ProjectParties', back_populates='party_people')


class PartyRoles(Base):
    __tablename__ = 'party_roles'
    __table_args__ = (
        ForeignKeyConstraint(['party_id'], ['project_parties.id'], name='party_roles_party_id_fkey'),
        PrimaryKeyConstraint('party_id', 'role', name='party_roles_pkey')
    )

    party_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String, primary_key=True)

    party: Mapped['ProjectParties'] = relationship('ProjectParties', back_populates='party_roles')


class ProjectFinance(Base):
    __tablename__ = 'project_finance'
    __table_args__ = (
        ForeignKeyConstraint(['budget_id'], ['project_budgets.id'], name='project_finance_budget_id_fkey'),
        PrimaryKeyConstraint('id', name='project_finance_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    budget_id: Mapped[int] = mapped_column(Integer, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    asset_class: Mapped[Optional[str]] = mapped_column(String)
    type: Mapped[Optional[str]] = mapped_column(String)
    concessional: Mapped[Optional[bool]] = mapped_column(Boolean)
    value_amount: Mapped[Optional[float]] = mapped_column(Double(53))
    value_currency: Mapped[Optional[str]] = mapped_column(String)
    source: Mapped[Optional[str]] = mapped_column(String)
    financing_party_id: Mapped[Optional[str]] = mapped_column(String)
    financing_party_name: Mapped[Optional[str]] = mapped_column(String)
    period_start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    period_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    payment_period_start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    payment_period_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    interest_rate_margin: Mapped[Optional[float]] = mapped_column(Double(53))
    description: Mapped[Optional[str]] = mapped_column(String)

    budget: Mapped['ProjectBudgets'] = relationship('ProjectBudgets', back_populates='project_finance')


class ProjectPolicyAlignmentPolicies(Base):
    __tablename__ = 'project_policy_alignment_policies'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['project_policy_alignment.project_id'], name='project_policy_alignment_policies_project_id_fkey'),
        PrimaryKeyConstraint('project_id', 'policy', name='project_policy_alignment_policies_pkey')
    )

    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    policy: Mapped[str] = mapped_column(String, primary_key=True)

    project: Mapped['ProjectPolicyAlignment'] = relationship('ProjectPolicyAlignment', back_populates='project_policy_alignment_policies')


class SocialConsultationMeetings(Base):
    __tablename__ = 'social_consultation_meetings'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['project_social.project_id'], name='social_consultation_meetings_project_id_fkey'),
        PrimaryKeyConstraint('id', name='social_consultation_meetings_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    number_of_participants: Mapped[Optional[int]] = mapped_column(Integer)
    street_address: Mapped[Optional[str]] = mapped_column(String)
    locality: Mapped[Optional[str]] = mapped_column(String)
    region: Mapped[Optional[str]] = mapped_column(String)
    postal_code: Mapped[Optional[str]] = mapped_column(String)
    country_name: Mapped[Optional[str]] = mapped_column(String)
    person_name: Mapped[Optional[str]] = mapped_column(String)
    organization_name: Mapped[Optional[str]] = mapped_column(String)
    organization_id: Mapped[Optional[str]] = mapped_column(String)
    job_title: Mapped[Optional[str]] = mapped_column(String)

    project: Mapped['ProjectSocial'] = relationship('ProjectSocial', back_populates='social_consultation_meetings')


class SocialHealthSafetyMaterialTests(Base):
    __tablename__ = 'social_health_safety_material_tests'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['project_social.project_id'], name='social_health_safety_material_tests_project_id_fkey'),
        PrimaryKeyConstraint('project_id', 'test', name='social_health_safety_material_tests_pkey')
    )

    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    test: Mapped[str] = mapped_column(String, primary_key=True)

    project: Mapped['ProjectSocial'] = relationship('ProjectSocial', back_populates='social_health_safety_material_tests')


class BeneficialOwnerNationalities(Base):
    __tablename__ = 'beneficial_owner_nationalities'
    __table_args__ = (
        ForeignKeyConstraint(['owner_id'], ['party_beneficial_owners.id'], name='beneficial_owner_nationalities_owner_id_fkey'),
        PrimaryKeyConstraint('owner_id', 'nationality', name='beneficial_owner_nationalities_pkey')
    )

    owner_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nationality: Mapped[str] = mapped_column(String, primary_key=True)

    owner: Mapped['PartyBeneficialOwners'] = relationship('PartyBeneficialOwners', back_populates='beneficial_owner_nationalities')


class BudgetBreakdownItems(Base):
    __tablename__ = 'budget_breakdown_items'
    __table_args__ = (
        ForeignKeyConstraint(['breakdown_id'], ['budget_breakdowns.id'], name='budget_breakdown_items_breakdown_id_fkey'),
        PrimaryKeyConstraint('id', name='budget_breakdown_items_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    breakdown_id: Mapped[int] = mapped_column(Integer, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    amount: Mapped[Optional[float]] = mapped_column(Double(53))
    currency: Mapped[Optional[str]] = mapped_column(String)
    uri: Mapped[Optional[str]] = mapped_column(String)
    period_start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    period_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    period_max_extent_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    period_duration_days: Mapped[Optional[int]] = mapped_column(Integer)
    source_party_id: Mapped[Optional[str]] = mapped_column(String)
    source_party_name: Mapped[Optional[str]] = mapped_column(String)

    breakdown: Mapped['BudgetBreakdowns'] = relationship('BudgetBreakdowns', back_populates='budget_breakdown_items')


class ContractingTenderEntities(Base):
    __tablename__ = 'contracting_tender_entities'
    __table_args__ = (
        ForeignKeyConstraint(['process_id'], ['contracting_tenders.process_id'], name='contracting_tender_entities_process_id_fkey'),
        PrimaryKeyConstraint('id', name='contracting_tender_entities_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    process_id: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[Optional[str]] = mapped_column(String)
    name: Mapped[Optional[str]] = mapped_column(String)

    process: Mapped['ContractingTenders'] = relationship('ContractingTenders', back_populates='contracting_tender_entities')


class ContractingTenderSustainability(Base):
    __tablename__ = 'contracting_tender_sustainability'
    __table_args__ = (
        ForeignKeyConstraint(['process_id'], ['contracting_tenders.process_id'], name='contracting_tender_sustainability_process_id_fkey'),
        PrimaryKeyConstraint('id', name='contracting_tender_sustainability_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    process_id: Mapped[int] = mapped_column(Integer, nullable=False)
    strategies: Mapped[Optional[dict]] = mapped_column(JSONB)

    process: Mapped['ContractingTenders'] = relationship('ContractingTenders', back_populates='contracting_tender_sustainability')


class ContractingTenderTenderers(Base):
    __tablename__ = 'contracting_tender_tenderers'
    __table_args__ = (
        ForeignKeyConstraint(['process_id'], ['contracting_tenders.process_id'], name='contracting_tender_tenderers_process_id_fkey'),
        PrimaryKeyConstraint('id', name='contracting_tender_tenderers_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    process_id: Mapped[int] = mapped_column(Integer, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String)

    process: Mapped['ContractingTenders'] = relationship('ContractingTenders', back_populates='contracting_tender_tenderers')


class CostItems(Base):
    __tablename__ = 'cost_items'
    __table_args__ = (
        ForeignKeyConstraint(['cost_group_id'], ['cost_groups.id'], name='cost_items_cost_group_id_fkey'),
        PrimaryKeyConstraint('id', name='cost_items_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cost_group_id: Mapped[int] = mapped_column(Integer, nullable=False)
    local_id: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[Optional[float]] = mapped_column(Double(53))
    currency: Mapped[Optional[str]] = mapped_column(String)
    classification_id: Mapped[Optional[str]] = mapped_column(String)
    classification_scheme: Mapped[Optional[str]] = mapped_column(String)
    classification_description: Mapped[Optional[str]] = mapped_column(String)

    cost_group: Mapped['CostGroups'] = relationship('CostGroups', back_populates='cost_items')


class LocationGazetteerIdentifiers(Base):
    __tablename__ = 'location_gazetteer_identifiers'
    __table_args__ = (
        ForeignKeyConstraint(['gazetteer_id'], ['location_gazetteers.id'], name='location_gazetteer_identifiers_gazetteer_id_fkey'),
        PrimaryKeyConstraint('id', name='location_gazetteer_identifiers_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gazetteer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    identifier: Mapped[str] = mapped_column(String, nullable=False)

    gazetteer: Mapped['LocationGazetteers'] = relationship('LocationGazetteers', back_populates='location_gazetteer_identifiers')
