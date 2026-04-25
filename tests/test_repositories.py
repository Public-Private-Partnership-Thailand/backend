from sqlmodel import Session
import uuid
import pytest

from oc4ids_datastore_api.repositories.project_repository import ProjectRepository
from oc4ids_datastore_api.repositories.reference_repository import ReferenceRepository
from oc4ids_datastore_api.models import Project

def test_create_and_get_project_repository(session: Session):
    repo = ProjectRepository(session)
    project_id = uuid.uuid4()
    
    project = Project(
        id=project_id,
        title="Repo Test Project", 
        status="active"
    )
    
    created_project = repo.create(project)
    assert created_project.id == project_id
    assert created_project.title == "Repo Test Project"
    
    found_project = repo.get_by_id(str(project_id))
    assert found_project is not None
    assert found_project.title == "Repo Test Project"

def test_update_project_repository(session: Session):
    repo = ProjectRepository(session)
    project_id = uuid.uuid4()
    project = Project(id=project_id, title="Old Title")
    created = repo.create(project)
    
    created.title = "New Title"
    updated = repo.update(created)
    
    assert updated.title == "New Title"

def test_delete_project_repository_soft(session: Session):
    repo = ProjectRepository(session)
    project_id = uuid.uuid4()
    project = Project(id=project_id, title="To Soft Delete")
    created = repo.create(project)
    
    # Verify it exists
    assert repo.get_by_id(str(created.id)) is not None
    
    # Soft delete
    repo.delete(str(created.id), hard_delete=False)
    
    # Verify it is gone via getter (which respects deleted_at)
    assert repo.get_by_id(str(created.id)) is None

def test_get_projects_filtered_repository(session: Session):
    repo = ProjectRepository(session)
    repo.create(Project(id=uuid.uuid4(), title="P1 Filter"))
    repo.create(Project(id=uuid.uuid4(), title="P2 Dummy"))
    
    projects = repo.get_projects(title="Filter")
    assert len(projects) == 1
    assert projects[0].title == "P1 Filter"

def test_dashboard_stats_repository(session: Session):
    repo = ProjectRepository(session)
    stats = repo.get_dashboard_stats()
    
    assert "total_projects" in stats
    assert "total_investment" in stats
    assert "unique_contractors" in stats

def test_reference_repository_getters(session: Session):
    repo = ReferenceRepository(session)
    
    # Should not throw errors; might be empty if DB isn't seeded with reference data
    sectors = repo.get_sectors()
    assert isinstance(sectors, list)
    
    ministries = repo.get_ministries()
    assert isinstance(ministries, list)
    
    risk_cats = repo.get_risk_categories()
    assert isinstance(risk_cats, list)
