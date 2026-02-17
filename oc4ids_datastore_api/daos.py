from typing import List, Optional
import uuid
from sqlmodel import Session, select, func, or_
from oc4ids_datastore_api.models import Project, Ministry, Agency, ProjectParty, PartyAdditionalIdentifier, Sector
from sqlalchemy.dialects.postgresql import array_agg
class ProjectDAO:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, project_id: str) -> Optional[Project]:
        project = self.session.get(Project, project_id)
        if project and project.deleted_at:
            return None
        return project

    #def get_all(self, skip: int = 0, limit: int = 100) -> List[Project]:
    #    return self.session.exec(select(Project).offset(skip).limit(limit)).all()

    def get_projects(
        self, 
        skip: int = 0, 
        limit: int = 20,
        title: Optional[str] = None,
        sector_id: Optional[List[int]] = None,
        ministry_id: Optional[List[int]] = None,
        agency_id: Optional[List[int]] = None,
        concession_form_id: Optional[List[int]] = None,
        contract_type_id: Optional[List[int]] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None
    ):
        from sqlalchemy.orm import aliased
        from oc4ids_datastore_api.models import ProjectSectorLink, ProjectPeriod, ProjectAdditionalClassificationLink, ProjectBudget, AdditionalClassification
        
        # Aliases for filtering
        FilterLastPeriod = aliased(ProjectPeriod)
        FilterSectorLink = aliased(ProjectSectorLink)
        FilterLinkConcession = aliased(ProjectAdditionalClassificationLink)
        FilterAgency = aliased(Agency)
        
        id_query = select(Project.id).where(Project.deleted_at.is_(None))

        # Apply Filters
        if title:
            id_query = id_query.where(Project.title.ilike(f"%{title}%"))

        if sector_id:
            id_query = id_query.join(FilterSectorLink, Project.id == FilterSectorLink.project_id)
            id_query = id_query.where(FilterSectorLink.sector_id.in_(sector_id))
        
        if ministry_id:
            id_query = id_query.join(FilterAgency, Project.public_authority_id == FilterAgency.id, isouter=True)
            
            PartyMinistryFilter = aliased(Ministry)
            PartyAgencyFilter = aliased(Agency)
            PartyIdentifierFilter = aliased(PartyAdditionalIdentifier)
            ProjectPartyFilter = aliased(ProjectParty)
            
            id_query = id_query.outerjoin(ProjectPartyFilter, Project.id == ProjectPartyFilter.project_id)
            id_query = id_query.outerjoin(PartyIdentifierFilter, ProjectPartyFilter.id == PartyIdentifierFilter.party_id)
            id_query = id_query.outerjoin(PartyMinistryFilter, PartyIdentifierFilter.legal_name_id == PartyMinistryFilter.id)
            
            id_query = id_query.where(
                or_(
                    PartyMinistryFilter.id.in_(ministry_id),
                    FilterAgency.ministry_id.in_(ministry_id)
                )
            )

       

        if concession_form_id:
            id_query = id_query.join(FilterLinkConcession, Project.id == FilterLinkConcession.project_id)
            id_query = id_query.where(FilterLinkConcession.classification_id.in_(concession_form_id))
        
        if contract_type_id:
            FilterLinkContract = aliased(ProjectAdditionalClassificationLink)
            id_query = id_query.join(FilterLinkContract, Project.id == FilterLinkContract.project_id)
            id_query = id_query.where(FilterLinkContract.classification_id.in_(contract_type_id))
        
        if year_from or year_to:
             id_query = id_query.join(FilterLastPeriod, (Project.id == FilterLastPeriod.project_id) & (FilterLastPeriod.period_type == 'duration'))

        if year_from and year_to:
             id_query = id_query.where(func.extract('year', FilterLastPeriod.start_date) <= year_to)
             id_query = id_query.where(func.extract('year', FilterLastPeriod.end_date) >= year_from)
        elif year_from:
             id_query = id_query.where(func.extract('year', FilterLastPeriod.end_date) >= year_from)
        elif year_to:
             id_query = id_query.where(func.extract('year', FilterLastPeriod.start_date) <= year_to)

        id_query = id_query.distinct().offset(skip).limit(limit)
        
        project_ids = self.session.exec(id_query).all()

        if not project_ids:
            return []

        PartyAgency = aliased(Agency)
        AgencyMinistry = aliased(Ministry)
        
        # Main Query for Details
        statement = (
            select(
                Project.id,
                Project.title,
                Agency.name_en.label("agency_name"),
                # Aggregated columns
                func.string_agg(Ministry.name_en.distinct(), ', ').label("party_ministry_names"),
                func.string_agg(PartyAgency.name_en.distinct(), ', ').label("private_party_name"),
                func.array_agg(Sector.name_en.distinct()).label("sector_names"),
                # Concession Forms Only
                func.array_agg(
                    AdditionalClassification.description.distinct()
                ).filter(AdditionalClassification.scheme == 'รูปแบบสัมปทานหรือค่าตอบแทน').label("concession_names"),
                func.array_agg(
                    AdditionalClassification.description.distinct()
                ).filter(AdditionalClassification.scheme == 'รูปแบบการจัดสรรกรรมสิทธิ์').label("contract_type_names"),
                func.min(ProjectPeriod.start_date).label("start_date"),
                func.sum(ProjectBudget.total_amount).label("budget_amount"),
            )
            .filter(Project.id.in_(project_ids)) # Filter by pre-selected IDs
            
            .join(Agency, Project.public_authority_id == Agency.id, isouter=True) 
            .join(ProjectBudget, Project.id == ProjectBudget.project_id, isouter=True)           
            # Party connections
            .join(ProjectParty, Project.id == ProjectParty.project_id, isouter=True)
            .join(PartyAdditionalIdentifier, ProjectParty.id == PartyAdditionalIdentifier.party_id, isouter=True)
            #ministry
            .join(Ministry, PartyAdditionalIdentifier.legal_name_id == Ministry.id, isouter=True)
            #agency
            .join(PartyAgency, ProjectParty.identifier_legal_name_id == PartyAgency.id, isouter=True)
            #sector
            .join(ProjectSectorLink, Project.id == ProjectSectorLink.project_id, isouter=True)
            .join(Sector, ProjectSectorLink.sector_id == Sector.id, isouter=True)

            .join(ProjectAdditionalClassificationLink, Project.id == ProjectAdditionalClassificationLink.project_id, isouter=True)
            .join(AdditionalClassification, ProjectAdditionalClassificationLink.classification_id == AdditionalClassification.id, isouter=True)
            #start_date
            .join(ProjectPeriod, Project.id == ProjectPeriod.project_id, isouter=True)
        )
        
        statement = statement.group_by(Project.id, Project.title, Agency.name_en)
        return self.session.exec(statement).all()

    def get_summaries(self, *args, **kwargs):
        return self.get_projects(*args, **kwargs)

    def count(self) -> int:
        return self.session.exec(select(func.count()).select_from(Project).where(Project.deleted_at.is_(None))).one()

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

    def delete(self, project_id: str, hard_delete: bool = False) -> None:
        from datetime import datetime
        
        project = self.session.get(Project, project_id)
        
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
            
        if hard_delete:
            self.session.delete(project)
        else:
            project.deleted_at = datetime.utcnow()
            self.session.add(project)
            
        self.session.commit()

    def get_dashboard_stats(
        self,
        title: Optional[str] = None,
        sector_id: Optional[List[int]] = None,
        ministry_id: Optional[List[int]] = None,
        agency_id: Optional[List[int]] = None,
        concession_form_id: Optional[List[int]] = None,
        contract_type_id: Optional[List[int]] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None
    ) -> dict:
        """
        Get aggregated statistics for the dashboard.
        """
        from sqlalchemy.orm import aliased
        from sqlalchemy import func, case, and_, or_
        from oc4ids_datastore_api.models import ProjectSectorLink, ProjectPeriod, ProjectAdditionalClassificationLink, ProjectBudget, AdditionalClassification
        
        # --- 1. Base Query Construction (Similar to get_projects) ---
        FilterLastPeriod = aliased(ProjectPeriod)
        FilterSectorLink = aliased(ProjectSectorLink)
        FilterLinkConcession = aliased(ProjectAdditionalClassificationLink)
        FilterAgency = aliased(Agency)
        
        id_query = select(Project.id).where(Project.deleted_at.is_(None))

        # Apply Filters (Same logic as get_projects)
        if title:
            id_query = id_query.where(Project.title.ilike(f"%{title}%"))

        if sector_id:
            id_query = id_query.join(FilterSectorLink, Project.id == FilterSectorLink.project_id)
            id_query = id_query.where(FilterSectorLink.sector_id.in_(sector_id))
        
        if ministry_id:
            id_query = id_query.join(FilterAgency, Project.public_authority_id == FilterAgency.id, isouter=True)
            PartyMinistryFilter = aliased(Ministry)
            PartyAgencyFilter = aliased(Agency)
            PartyIdentifierFilter = aliased(PartyAdditionalIdentifier)
            ProjectPartyFilter = aliased(ProjectParty)
            
            id_query = id_query.outerjoin(ProjectPartyFilter, Project.id == ProjectPartyFilter.project_id)
            id_query = id_query.outerjoin(PartyIdentifierFilter, ProjectPartyFilter.id == PartyIdentifierFilter.party_id)
            id_query = id_query.outerjoin(PartyMinistryFilter, PartyIdentifierFilter.legal_name_id == PartyMinistryFilter.id)
            
            id_query = id_query.where(
                or_(
                    PartyMinistryFilter.id.in_(ministry_id),
                    FilterAgency.ministry_id.in_(ministry_id)
                )
            )

        if concession_form_id:
            id_query = id_query.join(FilterLinkConcession, Project.id == FilterLinkConcession.project_id)
            id_query = id_query.where(FilterLinkConcession.classification_id.in_(concession_form_id))
        
        if contract_type_id:
            FilterLinkContract = aliased(ProjectAdditionalClassificationLink)
            id_query = id_query.join(FilterLinkContract, Project.id == FilterLinkContract.project_id)
            id_query = id_query.where(FilterLinkContract.classification_id.in_(contract_type_id))
        
        if year_from or year_to:
             id_query = id_query.join(FilterLastPeriod, (Project.id == FilterLastPeriod.project_id) & (FilterLastPeriod.period_type == 'duration'))

        if year_from and year_to:
             id_query = id_query.where(func.extract('year', FilterLastPeriod.start_date) <= year_to)
             id_query = id_query.where(func.extract('year', FilterLastPeriod.end_date) >= year_from)
        elif year_from:
             id_query = id_query.where(func.extract('year', FilterLastPeriod.end_date) >= year_from)
        elif year_to:
             id_query = id_query.where(func.extract('year', FilterLastPeriod.start_date) <= year_to)

        # Use CTE or subquery for filtered project IDs
        filtered_project_ids = id_query.distinct().subquery()
        
        # --- 2. Aggregations ---
        
        # 2.1 Total Projects
        total_projects = self.session.exec(select(func.count()).select_from(filtered_project_ids)).one()
        
        if total_projects == 0:
            return {
                "total_projects": 0,
                "total_investment": 0,
                "max_budget": 0,
                "unique_contractors": 0,
                "ministry_counts": {},
                "ministry_investments": {},
                "project_scales": {
                    "big": {"count": 0, "investment": 0},
                    "medium": {"count": 0, "investment": 0},
                    "small": {"count": 0, "investment": 0},
                },
                "sector_stats": {},
                "investment_by_year": {},
                "project_ids": []
            }

        # 2.2 Total Investment & Max Budget (using ProjectBudget or logic used in get_projects?)
        # Wait, get_projects logic doesn't select budget directly in the main query shown earlier.
        # But dashboard summary had "total_investment" and "max_budget".
        # Assuming budget info is in ProjectBudget linked to Project
        
        # We need to join ProjectBudget to the filtered IDs
        # Note: A project might have multiple budgets? Assuming distinct sum logic or specific budget type?
        # Standard OC4IDS has budget.amount.
        # Let's check ProjectBudget model implicitly.
        
        ProjectBudgetAlias = aliased(ProjectBudget)
        
        # Total Investment (Sum of all budgets for filtered projects)
        investment_query = select(func.sum(ProjectBudgetAlias.total_amount)).where(ProjectBudgetAlias.project_id.in_(select(filtered_project_ids.c.id)))
        total_investment = self.session.exec(investment_query).one() or 0
        
        # Max Budget
        max_budget_query = select(func.max(ProjectBudgetAlias.total_amount)).where(ProjectBudgetAlias.project_id.in_(select(filtered_project_ids.c.id)))
        max_budget = self.session.exec(max_budget_query).one() or 0
        
        # 2.3 Unique Contractors = Total count of agencies
        AgencyCountAlias = aliased(Agency)
        contractor_query = select(func.count(AgencyCountAlias.id)).where(AgencyCountAlias.ministry_id.is_(None))
        unique_contractors = self.session.exec(contractor_query).one()

        ProjectPartyAlias = aliased(ProjectParty)

        # 2.4 Ministry Stats (Count and Investment)
        # Group by Ministry (via Agency -> Ministry OR ProjectParty -> Ministry?)
        # Based on get_projects logic, it seems we care about the "Public Authority" ministry.
        
        MinistryAlias = aliased(Ministry)
        AgencyAlias = aliased(Agency)
        IdentifierAlias = aliased(PartyAdditionalIdentifier)
        
        # Basic approach: Group by Ministry of the Public Authority (Agency)
        stats_query = (
            select(
                MinistryAlias.name_en, # Use name_en to match get_projects
                func.count(func.distinct(Project.id)),
                func.sum(ProjectBudgetAlias.total_amount)
            )
            .join(ProjectPartyAlias, Project.id == ProjectPartyAlias.project_id)
            .join(IdentifierAlias, ProjectPartyAlias.id == IdentifierAlias.party_id)
            .join(MinistryAlias, IdentifierAlias.legal_name_id == MinistryAlias.id)
            .outerjoin(ProjectBudgetAlias, Project.id == ProjectBudgetAlias.project_id)
            .where(Project.id.in_(select(filtered_project_ids.c.id)))
            .group_by(MinistryAlias.id, MinistryAlias.name_en)
        )
        
        ministry_stats_results = self.session.exec(stats_query).all()
        
        ministry_counts = {row[0]: row[1] for row in ministry_stats_results}
        ministry_investments = {row[0]: (row[2] or 0) for row in ministry_stats_results}

        # 2.5 Project Scales (Small, Medium, Big)
        # Small < 1,000M, Medium 1,000M - 5,000M, Big > 5,000M
        
        # We can do this with a single query using CASE WHEN
        scale_query = (
            select(
                func.sum(case((ProjectBudgetAlias.total_amount >= 5000000000, 1), else_=0)).label("big_count"),
                func.sum(case((ProjectBudgetAlias.total_amount >= 5000000000, ProjectBudgetAlias.total_amount), else_=0)).label("big_investment"),
                
                func.sum(case((and_(ProjectBudgetAlias.total_amount >= 1000000000, ProjectBudgetAlias.total_amount < 5000000000), 1), else_=0)).label("medium_count"),
                func.sum(case((and_(ProjectBudgetAlias.total_amount >= 1000000000, ProjectBudgetAlias.total_amount < 5000000000), ProjectBudgetAlias.total_amount), else_=0)).label("medium_investment"),
                
                func.sum(case((ProjectBudgetAlias.total_amount < 1000000000, 1), else_=0)).label("small_count"),
                func.sum(case((ProjectBudgetAlias.total_amount < 1000000000, ProjectBudgetAlias.total_amount), else_=0)).label("small_investment"),
            )
            .where(ProjectBudgetAlias.project_id.in_(select(filtered_project_ids.c.id)))
        )
        
        scale_results = self.session.exec(scale_query).first()
        
        project_scales = {
            "big": {"count": scale_results[0] or 0, "investment": scale_results[1] or 0},
            "medium": {"count": scale_results[2] or 0, "investment": scale_results[3] or 0},
            "small": {"count": scale_results[4] or 0, "investment": scale_results[5] or 0},
        }

        # 2.6 Sector Stats
        # Group by Sector Name
        
        SectorAlias = aliased(Sector)
        ProjectSectorLinkAlias = aliased(ProjectSectorLink)
        
        sector_stats = {}
        # Need to join Project -> ProjectSectorLink -> Sector
        # And also ProjectBudget for investment amounts and scale breakdown per sector?
        # The original code structure suggested complex nested stats: sector -> total/small/medium/big
        
        # Simplified Sector Stats Query (Group by Sector, then maybe post-process or complex query)
        # Let's do basic sector stats first: Count and Total Investment
        
        sector_query = (
             select(
                 SectorAlias.name_en,
                 func.count(func.distinct(Project.id)),
                 func.sum(ProjectBudgetAlias.total_amount),
                 # Small < 1,000M
                 func.sum(case((ProjectBudgetAlias.total_amount < 1000000000, 1), else_=0)),
                 func.sum(case((ProjectBudgetAlias.total_amount < 1000000000, ProjectBudgetAlias.total_amount), else_=0)),
                 # Medium 1,000M - < 5,000M
                 func.sum(case((and_(ProjectBudgetAlias.total_amount >= 1000000000, ProjectBudgetAlias.total_amount < 5000000000), 1), else_=0)),
                 func.sum(case((and_(ProjectBudgetAlias.total_amount >= 1000000000, ProjectBudgetAlias.total_amount < 5000000000), ProjectBudgetAlias.total_amount), else_=0)),
                 # Big >= 5,000M
                 func.sum(case((ProjectBudgetAlias.total_amount >= 5000000000, 1), else_=0)),
                 func.sum(case((ProjectBudgetAlias.total_amount >= 5000000000, ProjectBudgetAlias.total_amount), else_=0))
             )
             .join(ProjectSectorLinkAlias, Project.id == ProjectSectorLinkAlias.project_id)
             .join(SectorAlias, ProjectSectorLinkAlias.sector_id == SectorAlias.id)
             .outerjoin(ProjectBudgetAlias, Project.id == ProjectBudgetAlias.project_id)
             .where(Project.id.in_(select(filtered_project_ids.c.id)))
             .group_by(SectorAlias.id, SectorAlias.name_en)
        )
        
        sector_results = self.session.exec(sector_query).all()
        
        for row in sector_results:
             name = row[0]
             total_count = row[1]
             total_inv = row[2]
             
             small_count = row[3] or 0
             small_inv = row[4] or 0
             
             medium_count = row[5] or 0
             medium_inv = row[6] or 0
             
             big_count = row[7] or 0
             big_inv = row[8] or 0

             sector_stats[name] = {
                 "total": {"count": total_count, "investment": total_inv or 0},
                 "small": {"count": small_count, "investment": small_inv},
                 "medium": {"count": medium_count, "investment": medium_inv},
                 "big": {"count": big_count, "investment": big_inv}
             }

        # 2.7 Investment by Year
        # Group by start_date year
        ProjectPeriodAlias = aliased(ProjectPeriod)
        
        year_query = (
            select(
                func.extract('year', ProjectPeriodAlias.start_date).label("year"),
                func.count(func.distinct(Project.id)),
                func.sum(ProjectBudgetAlias.total_amount)
            )
            .join(ProjectPeriodAlias, Project.id == ProjectPeriodAlias.project_id)
            .outerjoin(ProjectBudgetAlias, Project.id == ProjectBudgetAlias.project_id)
            .where(
                Project.id.in_(select(filtered_project_ids.c.id)),
                ProjectPeriodAlias.period_type == 'duration', # Assuming main project duration
                ProjectPeriodAlias.start_date.is_not(None)
            )
            .group_by("year")
            .order_by("year")
        )
        
        year_results = self.session.exec(year_query).all()
        # Format: {year: {count: x, investment: y}}
        investment_by_year = {}
        for y, c, i in year_results:
            if y:
                investment_by_year[int(y)] = {"count": c, "investment": i or 0}

        return {
            "total_projects": total_projects,
            "total_investment": total_investment,
            "max_budget": max_budget,
            "unique_contractors": unique_contractors,
            "ministry_counts": ministry_counts,
            "ministry_investments": ministry_investments,
            "project_scales": project_scales,
            "sector_stats": sector_stats,
            "investment_by_year": investment_by_year,
            "project_ids": [row for row in self.session.exec(select(filtered_project_ids)).all()] 
        }

class ReferenceDataDAO:
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
    
    def get_project_types(self):
        """Fetch all project types"""
        from oc4ids_datastore_api.models import ProjectType
        return self.session.exec(select(ProjectType)).all()
    
    def get_concession_forms(self) -> List:
        """Fetch concession forms from additional_classifications"""
        from oc4ids_datastore_api.models import AdditionalClassification
        return self.session.exec(
            select(AdditionalClassification)
            .where(AdditionalClassification.scheme == "รูปแบบสัมปทานหรือค่าตอบแทน")
            .distinct()
        ).all()

    def get_contract_types(self) -> List:
        """Fetch contract types from additional_classifications"""
        from oc4ids_datastore_api.models import AdditionalClassification
        return self.session.exec(
            select(AdditionalClassification)
            .where(AdditionalClassification.scheme == "รูปแบบการจัดสรรกรรมสิทธิ์")
            .distinct()
        ).all()
    

