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
        
        if year_from:
             id_query = id_query.join(FilterLastPeriod, (Project.id == FilterLastPeriod.project_id) & (FilterLastPeriod.period_type == 'duration'))
             id_query = id_query.where(func.extract('year', FilterLastPeriod.start_date) >= year_from)
        
        if year_to:
             if not year_from:
                 id_query = id_query.join(FilterLastPeriod, (Project.id == FilterLastPeriod.project_id) & (FilterLastPeriod.period_type == 'duration'))
             
             id_query = id_query.where(func.extract('year', FilterLastPeriod.end_date) <= year_to)

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
                func.min(ProjectPeriod.start_date).label("start_date"),
            )
            .filter(Project.id.in_(project_ids)) # Filter by pre-selected IDs
            
            .join(Agency, Project.public_authority_id == Agency.id, isouter=True)            
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

    def delete(self, project_id: str) -> None:
        from datetime import datetime
        
        project = self.session.get(Project, project_id)
        
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
            
        project.deleted_at = datetime.utcnow()
        self.session.add(project)
        self.session.commit()

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
    

