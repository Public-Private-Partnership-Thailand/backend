import json
import logging
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
logger = logging.getLogger(__name__)

def import_new_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, 'data', 'data.json')
    
    if not os.path.exists(json_path):
        logger.error(f"Error: {json_path} not found.")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            projects = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON: {e}")
        return

    if not isinstance(projects, list):
        logger.error("JSON data must be a list of projects.")
        return

    logger.info(f"Found {len(projects)} projects to import.")

    with Session(engine) as session:
        for i, project in enumerate(projects):
            title = project.get('title', 'Unknown Title')
            logger.info(f"Importing project {i+1}/{len(projects)}: {title}")
            try:
                # Call service function directly
                result = create_project_data(project, session)
                logger.info(f"Success! ID: {result['project']['id']}")
            except Exception as e:
                logger.error(f"Failed to import project '{title}': {e}")
        
        try:
            session.commit()
            logger.info("Import completed and committed.")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to commit import: {e}")

if __name__ == "__main__":
    import_new_data()
