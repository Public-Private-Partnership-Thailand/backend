import json
import requests
import sys

def import_data():
    try:
        with open('example.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: example.json not found.")
        return

    projects = data.get('projects', [])
    print(f"Found {len(projects)} projects to import.")

    url = 'http://localhost:8000/api/v1/datasets'
    
    for i, project in enumerate(projects):
        print(f"Importing project {i+1}/{len(projects)}: {project.get('id', 'Unknown ID')}")
        try:
            response = requests.post(url, json=project)
            if response.status_code == 200:
                print(f"Success! Response: {json.dumps(response.json(), indent=2)}")
            else:
                print(f"Failed ({response.status_code}): {response.text}")
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    import_data()
