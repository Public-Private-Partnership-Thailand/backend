from sqlmodel import Session
from oc4ids_datastore_api.daos import ProjectDAO
from oc4ids_datastore_api.models import Project

def test_create_project(session: Session):
    dao = ProjectDAO(session)
    project_data = Project(title="Test Project", status="active")
    
    created_project = dao.create(project_data)
    
    assert created_project.id is not None
    assert created_project.title == "Test Project"
    assert created_project.status == "active"

def test_get_project_by_id(session: Session):
    dao = ProjectDAO(session)
    project = Project(title="Find Me")
    dao.create(project)
    
    found_project = dao.get_by_id(str(project.id))
    
    assert found_project is not None
    assert found_project.title == "Find Me"

def test_update_project(session: Session):
    dao = ProjectDAO(session)
    project = Project(title="Old Title")
    created = dao.create(project)
    
    created.title = "New Title"
    updated = dao.update(created)
    
    assert updated.title == "New Title"
    assert updated.updated_at is not None

def test_delete_project(session: Session):
    dao = ProjectDAO(session)
    project = Project(title="To Delete")
    created = dao.create(project)
    
    # Verify it exists
    assert dao.get_by_id(str(created.id)) is not None
    
    dao.delete(created)
    
    # Verify it is gone
    assert dao.get_by_id(str(created.id)) is None

def test_get_all_projects(session: Session):
    dao = ProjectDAO(session)
    dao.create(Project(title="P1"))
    dao.create(Project(title="P2"))
    
    all_projects = dao.get_all()
    assert len(all_projects) == 2
