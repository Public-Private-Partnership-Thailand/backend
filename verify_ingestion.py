import os
import json
import logging
from sqlmodel import Session, select, create_engine, text, func
from oc4ids_datastore_api.services import create_project_data, Project
from oc4ids_datastore_api.models import (
    PartyRole, PartyPerson, ContractingTender, LocationGazetteer, ProjectFinance
)
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

def run_verification():
    # Ensure tables exist
    from sqlmodel import SQLModel
    # Import all models to ensure they are registered
    import oc4ids_datastore_api.models 
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # 1. Clean up existing projects (which cascades to everything else hopefully, if recent fixes work)
        # Or just drop/create tables? No, let's trust our delete.
        try:
            projects = session.exec(select(Project)).all()
            for p in projects:
                 # We need the dao for cascade delete, but let's just create new ID and ignore old ones
                 # Or just wipe tables manualy for clean state
                 pass
        except Exception as e:
             logging.warning(f"Cleanup warning: {e}")

    # Load example.json
    with open("example.json", "r") as f:
        data = json.load(f)
    
    # Ingest
    with Session(engine) as session:
        logging.info("Starting ingestion...")
        # Wrap in transaction
        for p_data in data["projects"]:
             # Force new random ID to avoid conflicts
             if "id" in p_data: del p_data["id"] 
             create_project_data(p_data, session)
        session.commit()
        logging.info("Ingestion complete.")

    # Check Data
    with Session(engine) as session:
        # Check Party Roles
        roles_count = session.exec(select(func.count()).select_from(PartyRole)).one()
        logging.info(f"Party Roles count: {roles_count}")
        
        # Check Tenders
        tenders_count = session.exec(select(func.count()).select_from(ContractingTender)).one()
        logging.info(f"Contracting Tenders count: {tenders_count}")
        
        # Check Gazetteers
        gaz_count = session.exec(select(func.count()).select_from(LocationGazetteer)).one()
        logging.info(f"Gazetteers count: {gaz_count}")
        
        # Check Finance
        fin_count = session.exec(select(func.count()).select_from(ProjectFinance)).one()
        logging.info(f"Project Finance count: {fin_count}")

        # --- Test Serialization (to_oc4ids) ---
        logging.info("Testing Project Serialization...")
        from oc4ids_datastore_api.daos import ProjectDAO
        dao = ProjectDAO(session)
        
        projects = session.exec(select(Project)).all()
        for p in projects:
             try:
                 output = p.to_oc4ids()
                 # Basic checks for new fields
                 if output.get("budget", {}).get("finance"):
                      logging.info(f"Project {p.id}: Found Finance")
                 if output.get("lobbyingMeetings"):
                      logging.info(f"Project {p.id}: Found Lobbying")
                 if output.get("policyAlignment"):
                      logging.info(f"Project {p.id}: Found Policy")
                 if output.get("assetLifetime"):
                      logging.info(f"Project {p.id}: Found Asset Lifetime")
                      
                 # Check contracting tender
                 cps = output.get("contractingProcesses", [])
                 if any(cp.get("summary", {}).get("tender") for cp in cps):
                      logging.info(f"Project {p.id}: Found Tender in CP")
                 else:
                      logging.warning(f"Project {p.id}: NO TENDER IN CP OUTPUT. CP Count: {len(cps)}")
                      
             except Exception as e:
                 logging.error(f"Failed to serialize project {p.id}: {e}")
                 import traceback
                 traceback.print_exc()

if __name__ == "__main__":
    run_verification()
