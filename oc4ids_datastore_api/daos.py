from typing import List, Optional
import uuid
from sqlmodel import Session, select, func
from oc4ids_datastore_api.models import Project, Ministry, Agency, ProjectParty, PartyAdditionalIdentifier, Sector

class ProjectDAO:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, project_id: str) -> Optional[Project]:
        return self.session.get(Project, project_id)

    #def get_all(self, skip: int = 0, limit: int = 100) -> List[Project]:
    #    return self.session.exec(select(Project).offset(skip).limit(limit)).all()

    def get_summaries(
        self, 
        skip: int = 0, 
        limit: int = 20,
        title: Optional[str] = None,
        sector_id: Optional[List[int]] = None,
        ministry_id: Optional[List[int]] = None,
        agency_id: Optional[List[int]] = None,
        concession_form: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None
    ):
        from sqlalchemy.orm import aliased
        from oc4ids_datastore_api.models import ProjectSectorLink, ProjectPeriod
        PartyAgency = aliased(Agency)

        statement = (
            select(
                Project.id,
                Project.title,
                Agency.name_en.label("agency_name"),
                func.string_agg(Ministry.name_en.distinct(), ', ').label("ministry_names"),
                func.string_agg(PartyAgency.name_en.distinct(), ', ').label("private_party_name")
            )
            .join(Agency, Project.public_authority_id == Agency.id, isouter=True)
            .join(ProjectParty, Project.id == ProjectParty.project_id, isouter=True)
            .join(PartyAdditionalIdentifier, ProjectParty.id == PartyAdditionalIdentifier.party_id, isouter=True)
            .join(Ministry, PartyAdditionalIdentifier.legal_name_id == Ministry.id, isouter=True)
            .join(PartyAgency, ProjectParty.identifier_legal_name_id == PartyAgency.id, isouter=True)
        )
        
        # Apply filters
        if title:
            statement = statement.where(Project.title.ilike(f"%{title}%"))
        
        if sector_id:
            statement = statement.join(
                ProjectSectorLink, 
                Project.id == ProjectSectorLink.project_id, 
                isouter=False
            ).where(ProjectSectorLink.sector_id.in_(sector_id))
        
        if ministry_id:
            statement = statement.where(Ministry.id.in_(ministry_id))
        
        if agency_id:
            statement = statement.where(Project.public_authority_id.in_(agency_id))
        
        if year_from or year_to:
            statement = statement.join(
                ProjectPeriod,
                Project.id == ProjectPeriod.project_id,
                isouter=False
            )
            if year_from:
                statement = statement.where(
                    func.extract('year', ProjectPeriod.start_date) >= year_from
                )
            if year_to:
                statement = statement.where(
                    func.extract('year', ProjectPeriod.end_date) <= year_to
                )
        
        statement = statement.group_by(Project.id, Project.title, Agency.name_en).offset(skip).limit(limit)
        
        return self.session.exec(statement).all()

    def count(self) -> int:
        return self.session.exec(select(func.count()).select_from(Project)).one()

    def create(self, project: Project) -> Project:
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def update(self, project: Project) -> Project:
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def delete(self, project_id: str) -> None:
        """Delete a project and all its related data (cascade delete)
        
        Preserves reference data: ministry, agency, sector, currency, etc.
        Deletes all project-specific data using raw SQL in the correct order.
        """
        from sqlalchemy import text
        
        # Verify project exists
        project = self.session.exec(
            select(Project).where(Project.id == project_id)
        ).first()
        
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # CRITICAL: Expunge all objects from session to prevent SQLAlchemy
        # from trying to manage relationships during raw SQL deletes
        self.session.expunge_all()
        
        # Use raw SQL DELETE for cascade - this avoids SQLAlchemy relationship issues
        # Delete in order: deepest children first, then parents
        
        delete_queries = [
            # Level 1: Deepest children (3+ levels deep)
            "DELETE FROM location_gazetteer_identifiers WHERE gazetteer_id IN (SELECT id FROM location_gazetteers WHERE location_id IN (SELECT id FROM project_locations WHERE project_id = :project_id))",
            "DELETE FROM location_gazetteers WHERE location_id IN (SELECT id FROM project_locations WHERE project_id = :project_id)",
            
            # Budget structure
            "DELETE FROM budget_breakdown_items WHERE breakdown_id IN (SELECT id FROM budget_breakdowns WHERE budget_id IN (SELECT id FROM project_budgets WHERE project_id = :project_id))",
            "DELETE FROM budget_breakdowns WHERE budget_id IN (SELECT id FROM project_budgets WHERE project_id = :project_id)",
            "DELETE FROM project_finance WHERE budget_id IN (SELECT id FROM project_budgets WHERE project_id = :project_id)",
            
            # Cost measurements
            "DELETE FROM cost_items WHERE cost_group_id IN (SELECT id FROM cost_groups WHERE cost_measurement_id IN (SELECT id FROM project_cost_measurements WHERE project_id = :project_id))",
            "DELETE FROM cost_groups WHERE cost_measurement_id IN (SELECT id FROM project_cost_measurements WHERE project_id = :project_id)",
            
            # Forecasts
            "DELETE FROM forecast_observations WHERE forecast_id IN (SELECT id FROM project_forecasts WHERE project_id = :project_id)",
            
            # Parties
            "DELETE FROM beneficial_owner_nationalities WHERE owner_id IN (SELECT id FROM party_beneficial_owners WHERE party_id IN (SELECT id FROM project_parties WHERE project_id = :project_id))",
            "DELETE FROM party_beneficial_owners WHERE party_id IN (SELECT id FROM project_parties WHERE project_id = :project_id)",
            "DELETE FROM party_people WHERE party_id IN (SELECT id FROM project_parties WHERE project_id = :project_id)",
            "DELETE FROM party_roles WHERE party_id IN (SELECT id FROM project_parties WHERE project_id = :project_id)",
            "DELETE FROM party_additional_identifiers WHERE party_id IN (SELECT id FROM project_parties WHERE project_id = :project_id)",
            "DELETE FROM party_classifications WHERE party_id IN (SELECT id FROM project_parties WHERE project_id = :project_id)",
            
            # Contracting processes
            "DELETE FROM contracting_tenders WHERE process_id IN (SELECT id FROM project_contracting_processes WHERE project_id = :project_id)",
            "DELETE FROM contracting_tender_tenderers WHERE process_id IN (SELECT id FROM project_contracting_processes WHERE project_id = :project_id)",
            "DELETE FROM contracting_tender_entities WHERE process_id IN (SELECT id FROM project_contracting_processes WHERE project_id = :project_id)",
            "DELETE FROM contracting_tender_sustainability WHERE process_id IN (SELECT id FROM project_contracting_processes WHERE project_id = :project_id)",
            "DELETE FROM contracting_suppliers WHERE process_id IN (SELECT id FROM project_contracting_processes WHERE project_id = :project_id)",
            "DELETE FROM contracting_documents WHERE process_id IN (SELECT id FROM project_contracting_processes WHERE project_id = :project_id)",
            "DELETE FROM contracting_modifications WHERE process_id IN (SELECT id FROM project_contracting_processes WHERE project_id = :project_id)",
            "DELETE FROM contracting_transactions WHERE process_id IN (SELECT id FROM project_contracting_processes WHERE project_id = :project_id)",
            "DELETE FROM contracting_milestones WHERE process_id IN (SELECT id FROM project_contracting_processes WHERE project_id = :project_id)",
            "DELETE FROM contracting_social WHERE process_id IN (SELECT id FROM project_contracting_processes WHERE project_id = :project_id)",
            "DELETE FROM contracting_releases WHERE process_id IN (SELECT id FROM project_contracting_processes WHERE project_id = :project_id)",
            
            # Metrics
            "DELETE FROM metric_observations WHERE metric_id IN (SELECT id FROM project_metrics WHERE project_id = :project_id)",
            
            # Social children
            "DELETE FROM social_health_safety_material_tests WHERE project_id = :project_id",
            "DELETE FROM social_consultation_meetings WHERE project_id = :project_id",
            
            # Environment children
            "DELETE FROM environment_goals WHERE project_id = :project_id",
            "DELETE FROM environment_climate_oversight_types WHERE project_id = :project_id",
            "DELETE FROM environment_conservation_measures WHERE project_id = :project_id",
            "DELETE FROM environment_environmental_measures WHERE project_id = :project_id",
            "DELETE FROM environment_climate_measures WHERE project_id = :project_id",
            "DELETE FROM environment_impact_categories WHERE project_id = :project_id",
            
            # Benefits
            "DELETE FROM benefit_beneficiaries WHERE benefit_id IN (SELECT id FROM project_benefits WHERE project_id = :project_id)",
            
            # Policy alignment
            "DELETE FROM project_policy_alignment_policies WHERE project_id = :project_id",
            
            # Level 2: Direct children of projects table
            "DELETE FROM project_identifiers WHERE project_id = :project_id",
            "DELETE FROM project_periods WHERE project_id = :project_id",
            "DELETE FROM project_sector WHERE project_id = :project_id",
            "DELETE FROM project_additional_classifications WHERE project_id = :project_id",
            "DELETE FROM project_related_projects WHERE project_id = :project_id",
            "DELETE FROM project_locations WHERE project_id = :project_id",
            "DELETE FROM project_documents WHERE project_id = :project_id",
            "DELETE FROM project_budgets WHERE project_id = :project_id",
            "DELETE FROM project_cost_measurements WHERE project_id = :project_id",
            "DELETE FROM project_forecasts WHERE project_id = :project_id",
            "DELETE FROM project_parties WHERE project_id = :project_id",
            "DELETE FROM project_contracting_processes WHERE project_id = :project_id",
            "DELETE FROM project_metrics WHERE project_id = :project_id",
            "DELETE FROM project_transactions WHERE project_id = :project_id",
            "DELETE FROM project_milestones WHERE project_id = :project_id",
            "DELETE FROM project_completion WHERE project_id = :project_id",
            "DELETE FROM project_lobbying_meetings WHERE project_id = :project_id",
            "DELETE FROM project_social WHERE project_id = :project_id",
            "DELETE FROM project_environment WHERE project_id = :project_id",
            "DELETE FROM project_benefits WHERE project_id = :project_id",
            "DELETE FROM project_policy_alignment WHERE project_id = :project_id",
            "DELETE FROM project_asset_lifetime WHERE project_id = :project_id",
            
            # Finally: The project itself
            "DELETE FROM projects WHERE id = :project_id",
        ]
        
        # Execute all delete queries
        # Use nested transactions (SAVEPOINT) to allow individual queries to fail 
        # (e.g. if table missing) without aborting the main transaction
        for query in delete_queries:
            try:
                with self.session.begin_nested():
                    self.session.execute(text(query), {"project_id": project_id})
            except Exception as e:
                # Check if it's a "relation does not exist" error and ignore it
                if "does not exist" in str(e):
                    continue
                # For other errors, re-raise (will abort the main transaction)
                raise e
        
        self.session.commit()

class ReferenceDataDAO:
    """DAO for fetching reference/lookup data"""
    def __init__(self, session: Session):
        self.session = session
    
    def get_sectors(self) -> List[Sector]:
        """Fetch all active sectors"""
        return self.session.exec(
            select(Sector).where(Sector.is_active == True)
        ).all()
    
    def get_ministries(self) -> List[Ministry]:
        """Fetch all ministries"""
        return self.session.exec(select(Ministry)).all()
    
    def get_contract_types(self) -> List:
        """Fetch contract types from additional_classifications"""
        from oc4ids_datastore_api.models import AdditionalClassification
        return self.session.exec(
            select(AdditionalClassification).distinct()
        ).all()
    
    def get_project_types(self):
        """Fetch all project types"""
        from oc4ids_datastore_api.models import ProjectType
        return self.session.exec(select(ProjectType)).all()
    
    def get_concession_forms(self) -> List:
        """Fetch concession forms from additional_classifications"""
        from oc4ids_datastore_api.models import AdditionalClassification
        return self.session.exec(
            select(AdditionalClassification).distinct()
        ).all()
