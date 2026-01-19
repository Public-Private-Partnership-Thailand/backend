from typing import List, Optional
import uuid
from sqlmodel import Session, select, func
from oc4ids_datastore_api.models import Project

class ProjectDAO:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, project_id: str) -> Optional[Project]:
        return self.session.get(Project, project_id)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Project]:
        return self.session.exec(select(Project).offset(skip).limit(limit)).all()

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
