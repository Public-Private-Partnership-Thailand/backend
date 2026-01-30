from typing import List, Optional
import uuid
from sqlmodel import Session, select, func
from oc4ids_datastore_api.models import Project, Ministry, Agency, ProjectParty, PartyAdditionalIdentifier

class ProjectDAO:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, project_id: str) -> Optional[Project]:
        return self.session.get(Project, project_id)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Project]:
        return self.session.exec(select(Project).offset(skip).limit(limit)).all()

    def get_summaries(self, skip: int = 0, limit: int = 20):
        from sqlalchemy.orm import aliased
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
            .group_by(Project.id, Project.title, Agency.name_en)
            .offset(skip)
            .limit(limit)
        )
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

    def delete(self, project: Project) -> None:
        self.session.delete(project)
        self.session.commit()
