from fastapi import FastAPI, Depends, HTTPException, Request
from sqlmodel import Session
from oc4ids_datastore_api.database import get_session
from oc4ids_datastore_api.schemas import Dataset
from oc4ids_datastore_api.services import get_all_datasets, get_project_by_id
from oc4ids_datastore_api.models import ProjectSQLModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from datetime import datetime
import json
import logging
import uuid

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS configuration - allow Next.js frontend
origins = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/datasets")
def read_projects(session: Session = Depends(get_session)) -> list[Dict[str, Any]]:
    """Get all projects in frontend format"""
    return get_all_datasets(session)


@app.get("/api/datasets/{project_id}")
def read_project(project_id: str, session: Session = Depends(get_session)) -> Dict[str, Any]:
    """Get a single project by ID in frontend format"""
    project = get_project_by_id(session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.post("/api/datasets")
async def create_project(request: Request, session: Session = Depends(get_session)):
    """Create a new project from frontend data"""
    try:
        # Get request body as JSON
        project_data = await request.json()
        logger.info(f"Received project data: {json.dumps(project_data, indent=2, default=str)}")
        
        # Generate ID if not provided or empty
        project_id = project_data.get("id")
        if not project_id or project_id == "":
            project_id = f"project-{uuid.uuid4().hex[:12]}"
            logger.info(f"Generated new project ID: {project_id}")
        
        # Parse updated date
        updated_date = datetime.utcnow()
        if project_data.get("updated"):
            try:
                updated_str = project_data.get("updated")
                if "Z" in updated_str:
                    updated_str = updated_str.replace("Z", "+00:00")
                updated_date = datetime.fromisoformat(updated_str)
            except (ValueError, AttributeError) as e:
                logger.warning(f"Could not parse updated date: {e}, using current time")
                updated_date = datetime.utcnow()
        
        # Convert frontend format to database format
        db_project = ProjectSQLModel(
            id=project_id,
            title=project_data.get("title"),
            description=project_data.get("description"),
            status=project_data.get("status"),
            type=project_data.get("type"),
            purpose=project_data.get("purpose"),
            language=project_data.get("language", "th"),
            updated=updated_date,
            period=project_data.get("period"),
            identification_period=project_data.get("identificationPeriod"),
            preparation_period=project_data.get("preparationPeriod"),
            implementation_period=project_data.get("implementationPeriod"),
            completion_period=project_data.get("completionPeriod"),
            maintenance_period=project_data.get("maintenancePeriod"),
            decommissioning_period=project_data.get("decommissioningPeriod"),
            sector=project_data.get("sector"),
            locations=project_data.get("locations"),
            budget=project_data.get("budget"),
            parties=project_data.get("parties"),
            public_authority=project_data.get("publicAuthority"),
            identifiers=project_data.get("identifiers"),
            additional_classifications=project_data.get("additionalClassifications"),
            related_projects=project_data.get("relatedProjects"),
            asset_lifetime=project_data.get("assetLifetime"),
            documents=project_data.get("documents"),
            forecasts=project_data.get("forecasts"),
            metrics=project_data.get("metrics"),
            cost_measurements=project_data.get("costMeasurements"),
            contracting_processes=project_data.get("contractingProcesses"),
            milestones=project_data.get("milestones"),
            transactions=project_data.get("transactions"),
            completion=project_data.get("completion"),
            lobbying_meetings=project_data.get("lobbyingMeetings"),
            social=project_data.get("social"),
            environment=project_data.get("environment"),
            policy_alignment=project_data.get("policyAlignment"),
            benefits=project_data.get("benefits"),
        )
        
        logger.info(f"Attempting to create project with ID: {db_project.id}")
        session.add(db_project)
        session.commit()
        session.refresh(db_project)
        logger.info(f"Project created successfully with ID: {db_project.id}")
        
        # Return in frontend format
        created_project = get_project_by_id(session, db_project.id)
        if not created_project:
            raise HTTPException(status_code=500, detail="Project was created but could not be retrieved")
        
        return {"message": "Project created successfully", "project": created_project}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}", exc_info=True)
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating project: {str(e)}")


@app.put("/api/datasets/{project_id}")
async def update_project(project_id: str, request: Request, session: Session = Depends(get_session)):
    """Update an existing project"""
    db_project = session.get(ProjectSQLModel, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Get request body as JSON
        project_data = await request.json()
        logger.info(f"Updating project {project_id} with data: {json.dumps(project_data, indent=2, default=str)}")
        
        # Update fields from frontend data
        if "title" in project_data:
            db_project.title = project_data["title"]
        if "description" in project_data:
            db_project.description = project_data["description"]
        if "status" in project_data:
            db_project.status = project_data["status"]
        if "type" in project_data:
            db_project.type = project_data["type"]
        if "purpose" in project_data:
            db_project.purpose = project_data["purpose"]
        if "period" in project_data:
            db_project.period = project_data["period"]
        if "identificationPeriod" in project_data:
            db_project.identification_period = project_data["identificationPeriod"]
        if "preparationPeriod" in project_data:
            db_project.preparation_period = project_data["preparationPeriod"]
        if "implementationPeriod" in project_data:
            db_project.implementation_period = project_data["implementationPeriod"]
        if "completionPeriod" in project_data:
            db_project.completion_period = project_data["completionPeriod"]
        if "maintenancePeriod" in project_data:
            db_project.maintenance_period = project_data["maintenancePeriod"]
        if "decommissioningPeriod" in project_data:
            db_project.decommissioning_period = project_data["decommissioningPeriod"]
        if "sector" in project_data:
            db_project.sector = project_data["sector"]
        if "locations" in project_data:
            db_project.locations = project_data["locations"]
        if "budget" in project_data:
            db_project.budget = project_data["budget"]
        if "parties" in project_data:
            db_project.parties = project_data["parties"]
        if "publicAuthority" in project_data:
            db_project.public_authority = project_data["publicAuthority"]
        if "identifiers" in project_data:
            db_project.identifiers = project_data["identifiers"]
        if "additionalClassifications" in project_data:
            db_project.additional_classifications = project_data["additionalClassifications"]
        if "relatedProjects" in project_data:
            db_project.related_projects = project_data["relatedProjects"]
        if "assetLifetime" in project_data:
            db_project.asset_lifetime = project_data["assetLifetime"]
        if "documents" in project_data:
            db_project.documents = project_data["documents"]
        if "forecasts" in project_data:
            db_project.forecasts = project_data["forecasts"]
        if "metrics" in project_data:
            db_project.metrics = project_data["metrics"]
        if "costMeasurements" in project_data:
            db_project.cost_measurements = project_data["costMeasurements"]
        if "contractingProcesses" in project_data:
            db_project.contracting_processes = project_data["contractingProcesses"]
        if "milestones" in project_data:
            db_project.milestones = project_data["milestones"]
        if "transactions" in project_data:
            db_project.transactions = project_data["transactions"]
        if "completion" in project_data:
            db_project.completion = project_data["completion"]
        if "lobbyingMeetings" in project_data:
            db_project.lobbying_meetings = project_data["lobbyingMeetings"]
        if "social" in project_data:
            db_project.social = project_data["social"]
        if "environment" in project_data:
            db_project.environment = project_data["environment"]
        if "policyAlignment" in project_data:
            db_project.policy_alignment = project_data["policyAlignment"]
        if "benefits" in project_data:
            db_project.benefits = project_data["benefits"]
        
        db_project.updated = datetime.utcnow()
        
        session.add(db_project)
        session.commit()
        session.refresh(db_project)
        logger.info(f"Project {project_id} updated successfully")
        
        # Return in frontend format
        updated_project = get_project_by_id(session, db_project.id)
        return {"message": "Project updated successfully", "project": updated_project}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {str(e)}", exc_info=True)
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating project: {str(e)}")


@app.delete("/api/datasets/{project_id}")
def delete_project(project_id: str, session: Session = Depends(get_session)):
    """Delete a project"""
    db_project = session.get(ProjectSQLModel, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        session.delete(db_project)
        session.commit()
        return {"message": "Project deleted successfully"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Error deleting project: {str(e)}")
