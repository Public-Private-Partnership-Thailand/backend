import requests
import json
import uuid

BASE_URL = "http://localhost:8000/api/v1"

def create_dummy_project():
    data = {
        "title": "Debug Project",
        "description": "Created for debugging update",
        "status": "active",
        "type": "PPP",
        "purpose": "Testing",
        "parties": []
    }
    print("Creating dummy project...")
    try:
        resp = requests.post(f"{BASE_URL}/projects", json=data)
        if resp.status_code == 200:
            pid = resp.json()["project"]["id"]
            print(f"Created project: {pid}")
            return pid
        else:
            print(f"Failed to create project: {resp.status_code} {resp.text}")
            return None
    except Exception as e:
        print(f"Error creating project: {e}")
        return None

def update_project(pid):
    data = {
        "id": pid,
        "title": "Debug Project Updated",
        "description": "Updated description",
        "status": "active",
        "type": "PPP",
        "purpose": "Testing Updated",
        "parties": []
    }
    print(f"Updating project {pid}...")
    try:
        resp = requests.put(f"{BASE_URL}/projects/{pid}", json=data)
        if resp.status_code == 200:
            print(f"Successfully updated project: {pid}")
            print(resp.json())
            return True
        else:
            print(f"Failed to update project: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        print(f"Error updating project: {e}")
        return False

if __name__ == "__main__":
    pid = create_dummy_project()
    if pid:
        success = update_project(pid)
        if success:
            print("Update test PASSED")
        else:
            print("Update test FAILED")
