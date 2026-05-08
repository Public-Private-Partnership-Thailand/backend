from fastapi.testclient import TestClient
from sqlmodel import Session
import uuid

# ==============================================================================
# Helper Factories
# ==============================================================================
def create_mock_project_payload(title="Test API Project"):
    return {
        "title": title,
        "description": "Created via Automated API Test",
        "status": "planned",
        "type": "หมวดการขนส่ง", # Matching projectType validation if any
        "publicAuthority": {
            "name": "กรมทางหลวง"
        },
        "period": {
            "startDate": "2024-01-01",
            "endDate": "2029-12-31"
        },
        "parties": [
            {
                "name": "บริษัท ทดสอบก่อสร้าง จำกัด",
                "roles": ["privateParty"],
                "identifier": {
                    "legalName": "บริษัท ทดสอบก่อสร้าง จำกัด"
                }
            }
        ]
    }

# ==============================================================================
# API Tests for Projects Router (/api/v1/projects)
# ==============================================================================

def test_create_project_api(client: TestClient):
    payload = create_mock_project_payload()
    response = client.post("/api/v1/projects/", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Project created successfully"
    assert "project" in data
    assert data["project"]["title"] == "Test API Project"
    assert "id" in data["project"]

def test_read_projects_api(client: TestClient):
    # Seed 2 projects
    client.post("/api/v1/projects/", json=create_mock_project_payload("P1"))
    client.post("/api/v1/projects/", json=create_mock_project_payload("P2"))
    
    response = client.get("/api/v1/projects/")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 2
    # Verify mapping output format
    assert "title" in data["data"][0]
    assert "ministry" in data["data"][0]

def test_read_single_project_api(client: TestClient):
    # Create first
    create_res = client.post("/api/v1/projects/", json=create_mock_project_payload("Single"))
    project_id = create_res.json()["project"]["id"]
    
    response = client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Single"
    assert data["id"] == project_id
    assert "publicAuthority" in data
    assert "period" in data

def test_update_project_api(client: TestClient):
    create_res = client.post("/api/v1/projects/", json=create_mock_project_payload("To Update"))
    project_id = create_res.json()["project"]["id"]
    
    update_payload = create_mock_project_payload("Updated API")
    response = client.put(f"/api/v1/projects/{project_id}", json=update_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["project"]["title"] == "Updated API"
    
    # Verify GET returns updated data
    get_res = client.get(f"/api/v1/projects/{project_id}")
    assert get_res.json()["title"] == "Updated API"

def test_delete_project_api(client: TestClient):
    create_res = client.post("/api/v1/projects/", json=create_mock_project_payload("To Delete"))
    project_id = create_res.json()["project"]["id"]
    
    response = client.delete(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Project deleted successfully"
    
    # Verify soft-delete hides it from GET
    get_res = client.get(f"/api/v1/projects/{project_id}")
    assert get_res.status_code == 404

def test_compare_projects_api(client: TestClient):
    r1 = client.post("/api/v1/projects/", json=create_mock_project_payload("Comp 1"))
    id1 = r1.json()["project"]["id"]
    
    r2 = client.post("/api/v1/projects/", json=create_mock_project_payload("Comp 2"))
    id2 = r2.json()["project"]["id"]

    response = client.get(f"/api/v1/projects/compare?ids={id1}&ids={id2}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert {p["title"] for p in data} == {"Comp 1", "Comp 2"}

# ==============================================================================
# API Tests for Other Features (Dashboard, Validation, Info, Risk)
# ==============================================================================

def test_dashboard_summary_api(client: TestClient):
    client.post("/api/v1/projects/", json=create_mock_project_payload("Dashboard P1"))
    
    response = client.get("/api/v1/summary")
    assert response.status_code == 200
    data = response.json()
    
    assert "summary" in data
    assert "totalProjects" in data["summary"]
    assert "ministryStats" in data
    assert "latestProjects" in data
    assert "projectScales" in data

def test_reference_data_info_api(client: TestClient):
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    
    assert "sector" in data
    assert "ministry" in data
    assert "projectType" in data
    assert "riskCategory" in data
    assert isinstance(data["sector"], list)

def test_risk_analysis_api(client: TestClient):
    response = client.get("/api/v1/risk")
    assert response.status_code == 200
    data = response.json()
    
    assert "heatmapRiskPhase" in data
    assert "sectorMinistryHeatmap" in data

def test_validation_error_missing_mandatory(client: TestClient):
    # Missing required `type` — Pydantic should reject before reaching the service
    payload = {"title": "Incomplete"}
    response = client.post("/api/v1/projects/", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    # The validation envelope from oc4ids_datastore_api/exceptions.py
    missing_fields = {err["loc"][-1] for err in body["details"] if err["type"] == "missing"}
    assert "type" in missing_fields
