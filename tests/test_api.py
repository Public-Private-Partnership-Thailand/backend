from fastapi.testclient import TestClient
from sqlmodel import Session
from oc4ids_datastore_api.models import Project

def test_create_project_api(client: TestClient):
    payload = {
        "title": "API Project",
        "description": "Created via API",
        "status": "planned"
    }
    response = client.post("/api/v1/datasets", json=payload)
    
    # 201 Created or 200 OK depending on implementation. 
    # Current services.py implementation returns {"message": ..., "project": ...} and default status is 200.
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Project created successfully"
    assert "project" in data
    assert data["project"]["title"] == "API Project"
    # Logic in services.py adds default values, check if id is there
    assert "id" in data["project"]

def test_read_projects_api(client: TestClient, session: Session):
    # Pre-seed
    client.post("/api/v1/datasets", json={"title": "P1"})
    client.post("/api/v1/datasets", json={"title": "P2"})
    
    response = client.get("/api/v1/datasets")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 2

def test_read_single_project_api(client: TestClient):
    # Create first
    create_res = client.post("/api/v1/datasets", json={"title": "Single"})
    project_id = create_res.json()["project"]["id"]
    
    response = client.get(f"/api/v1/datasets/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Single"
    assert data["id"] == project_id

def test_update_project_api(client: TestClient):
    create_res = client.post("/api/v1/datasets", json={"title": "To Update"})
    project_id = create_res.json()["project"]["id"]
    
    update_payload = {"title": "Updated API"}
    response = client.put(f"/api/v1/datasets/{project_id}", json=update_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["project"]["title"] == "Updated API"

def test_delete_project_api(client: TestClient):
    create_res = client.post("/api/v1/datasets", json={"title": "To Delete"})
    project_id = create_res.json()["project"]["id"]
    
    response = client.delete(f"/api/v1/datasets/{project_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Project deleted successfully"
    
    # Verify 404
    get_res = client.get(f"/api/v1/datasets/{project_id}")
    assert get_res.status_code == 404
