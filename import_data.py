import json
import logging
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from sqlmodel import Session
from oc4ids_datastore_api.database import engine
from oc4ids_datastore_api.services import create_project_data

# Setup basic logging
logging.basicConfig(level=logging.INFO)

def import_data_direct():
    try:
        with open('example.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: example.json not found.")
        return

    projects = data.get('projects', [])
    print(f"Found {len(projects)} projects to import directly into DB.")

    with Session(engine) as session:
        for i, project in enumerate(projects):
            print(f"Importing project {i+1}/{len(projects)}: {project.get('id', 'Unknown ID')}")
            try:
                # Call service function directly
                result = create_project_data(project, session)
                print(f"Success! ID: {result['project']['id']}")
            except Exception as e:
                print(f"Failed to import project: {e}")

if __name__ == "__main__":
    import_data_direct()
