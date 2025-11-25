from fastapi import FastAPI, Depends, HTTPException, Request,FastAPI, UploadFile, File
from sqlmodel import Session
from oc4ids_datastore_api.database import get_session
from oc4ids_datastore_api.schemas import Dataset
from oc4ids_datastore_api.services import get_all_datasets, get_project_by_id
from oc4ids_datastore_api.models import ProjectSQLModel
from fastapi.middleware.cors import CORSMiddleware
from libcoveoc4ids.api import oc4ids_json_output
from typing import Dict, Any
from datetime import datetime
import json
import logging
import uuid
import pandas as pd


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

def extract_messages(errors):
    messages = []
    for error_json_str, locations in errors:
        error = json.loads(error_json_str)
        messages.append(error.get("message"))
    return messages


def check_keys_exist_and_clean(project_data: Dict[str, Any]):
    model_keys = set(ProjectSQLModel.__annotations__.keys())
    input_keys = set(project_data.keys())

    missing_keys = model_keys - input_keys
    extra_keys = input_keys - model_keys

    errors = []
    if missing_keys:
        errors.extend([f"Missing key: {k}" for k in missing_keys])
    if extra_keys:
        errors.extend([f"Unexpected key: {k}" for k in extra_keys])

    if errors:
        raise HTTPException(status_code=400, detail={"validation_errors": errors})
    cleaned_data = {
    key: value
    for key, value in project_data.items()
    if not (isinstance(value, str) and value.strip() == "")
    }

    
    return cleaned_data


def add_metadata(project_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "version": "0.9",
        "uri": "https://standard.open-contracting.org/infrastructure/0.9/en/_static/example.json",
        "publishedDate": "2018-12-10T15:53:00Z",
        "publisher": {
            "name": "Open Data Services Co-operative Limited",
            "scheme": "GB-COH",
            "uid": "9506232",
            "uri": "http://data.companieshouse.gov.uk/doc/company/09506232"
        },
        "license": "http://opendatacommons.org/licenses/pddl/1.0/",
        "publicationPolicy": "https://standard.open-contracting.org/1.1/en/implementation/publication_policy/",
        "projects": [
            project_data
        ]
    }
def create_new_data(project_data: Dict[str, Any], session: Session) -> Dict[str, Any]:
    if not project_data.get("id"):
        project_data["id"] = str(uuid.uuid4())
    logger.info(f"Creating new project with ID {project_data['id']}: {json.dumps(project_data, indent=2, default=str)}")


    project_data = check_keys_exist_and_clean(project_data)

    wrapped = add_metadata(project_data)

    validation_result = oc4ids_json_output(json_data=wrapped)
    validation_errors = validation_result.get("validation_errors", [])
    if validation_errors:
        messages = extract_messages(validation_errors)
        raise HTTPException(status_code=400, detail={"validation_errors": messages})


    db_project = ProjectSQLModel(**project_data)  
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return {"message": "Project created successfully", "project": db_project}



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


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), session: Session = Depends(get_session)):
    filename = file.filename
    ext = filename.split(".")[-1].lower()

    try:
        if ext == "json":
            contents = await file.read()
            data = json.loads(contents)
            return create_new_data(data, session)

        elif ext == "csv":
            contents = await file.read()
            from io import BytesIO
            df = pd.read_csv(BytesIO(contents))
            return {"status": "success", "data": df.to_dict(orient="records")}

        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/datasets")
async def create_project(request: Request, session: Session = Depends(get_session)):
    project_data = await request.json()
    return create_new_data(project_data, session)


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
