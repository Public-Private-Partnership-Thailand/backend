from oc4ids_datastore_api.models import (
    Project, ProjectType, Sector, ProjectSectorLink, 
    ProjectLocation, ProjectParty, ProjectBudget, 
    ProjectPeriod, ProjectDocument, ProjectIdentifier,
    PeriodType
)
from oc4ids_datastore_api.daos import ProjectDAO

from sqlmodel import Session, select
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import uuid
import logging
from fastapi import HTTPException
from libcoveoc4ids.api import oc4ids_json_output

logger = logging.getLogger(__name__)

def _get_or_create_ref(session: Session, model: Any, code_field: str, code_value: str, defaults: Dict[str, Any] = None) -> Any:
    stmt = select(model).where(getattr(model, code_field) == code_value)
    obj = session.exec(stmt).first()
    if not obj:
        data = {code_field: code_value}
        if defaults:
            data.update(defaults)
        obj = model(**data)
        session.add(obj)
        session.flush()
        session.refresh(obj)
    return obj

def _convert_project_to_dict(project: Project) -> Dict[str, Any]:
    """Convert Project to ProjectData format expected by frontend.
    Returns the original full JSON if stored in raw_data, otherwise constructed dict.
    """
    if project.raw_data:
        try:
             return json.loads(project.raw_data)
        except Exception:
             logger.error(f"Failed to parse raw_data JSON for project {project.id}", exc_info=True)

    # Fallback/Safety dictionary
    result: Dict[str, Any] = {
        "id": str(project.id) if project.id else "",
        "updated": project.updated_at.isoformat() if project.updated_at else datetime.utcnow().isoformat(),
        "title": project.title or "",
        "description": project.description or "",
        "status": project.status or "active",
        "purpose": project.purpose or "",
        "language": "th",
        "sector": [s.code for s in project.sectors] if project.sectors else [],
    }
    return result

def get_all_datasets(session: Session, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """Get all projects with pagination"""
    dao = ProjectDAO(session)
    skip = (page - 1) * page_size
    projects = dao.get_all(skip=skip, limit=page_size)
    total = dao.count()
    
    return {
        "data": [_convert_project_to_dict(p) for p in projects],
        "pagination": {
            "page": page,
            "pageSize": page_size,
            "total": total,
            "totalPages": (total + page_size - 1) // page_size
        }
    }

def get_project_by_id(session: Session, project_id: str) -> Optional[Dict[str, Any]]:
    """Get a single project by ID and convert to frontend format"""
    dao = ProjectDAO(session)
    project = dao.get_by_id(project_id)
    if not project:
        return None
    return _convert_project_to_dict(project)

def add_metadata(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """Wraps project data for validation"""
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
        "projects": [project_data]
    }

def create_project_data(project_data: Dict[str, Any], session: Session) -> Dict[str, Any]:
    """Validates and stores project data"""
    if not project_data.get("id"):
        project_data["id"] = str(uuid.uuid4())
    
    project_id = project_data["id"]
    logger.info(f"Creating project {project_id}")

    # 1. Validation
    wrapped = add_metadata(project_data)
    validation_result = oc4ids_json_output(json_data=wrapped)
    # We log errors but proceed (soft validation as per previously established logic)
    if validation_result.get("validation_errors"):
       logger.warning(f"Validation errors for project {project_id}")

    # 2. Main Model Data
    model_data = {}
    valid_columns = ["id", "title", "description", "status", "purpose"]
    for col in valid_columns:
        if col in project_data:
            model_data[col] = project_data[col]
    
    # Crucial: Save the full original JSON string
    model_data["raw_data"] = json.dumps(project_data)

    if "type" in project_data:
        pt = _get_or_create_ref(session, ProjectType, "code", project_data["type"], {"name_en": project_data["type"]})
        model_data["project_type_id"] = pt.id

    db_project = Project(**model_data)

    # 3. Handle Relationships (Normalization for querying)
    
    # Sectors
    if "sector" in project_data and isinstance(project_data["sector"], list):
        for s_code in project_data["sector"]:
             sector_obj = _get_or_create_ref(session, Sector, "code", s_code, {"name_en": s_code, "category": "General", "name_th": s_code})
             db_project.sectors.append(sector_obj)

    # Locations
    if "locations" in project_data:
        for loc in project_data["locations"]:
             db_project.locations_list.append(ProjectLocation(
                description=loc.get("description"),
                street_address=loc.get("address", {}).get("streetAddress") if "address" in loc else None,
                locality=loc.get("address", {}).get("locality") if "address" in loc else None,
                geometry_coordinates=loc.get("geometry")
             ))

    # Parties
    if "parties" in project_data:
        for party in project_data["parties"]:
            db_project.parties_list.append(ProjectParty(
                local_id=party.get("id", str(uuid.uuid4())),
                name=party.get("name")
            ))

    # Period
    if "period" in project_data:
        pd = project_data["period"]
        _get_or_create_ref(session, PeriodType, "code", "duration", {"name_en": "Duration"})
        start_date = None
        if pd.get("startDate"):
            try: start_date = datetime.fromisoformat(pd["startDate"].replace("Z", "+00:00")).date()
            except: pass
        end_date = None
        if pd.get("endDate"):
             try: end_date = datetime.fromisoformat(pd["endDate"].replace("Z", "+00:00")).date()
             except: pass
             
        if start_date or end_date:
            pp = ProjectPeriod(period_type="duration", start_date=start_date, end_date=end_date)
            db_project.periods.append(pp)

    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    
    return {"message": "Project created successfully", "project": _convert_project_to_dict(db_project)}

def update_project_data(project_id: str, project_data: Dict[str, Any], session: Session) -> Dict[str, Any]:
    """Updates an existing project"""
    dao = ProjectDAO(session)
    db_project = dao.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    logger.info(f"Updating project {project_id}")
    
    # Update relational fields
    valid_columns = ["title", "description", "status", "purpose"]
    for key in valid_columns:
        if key in project_data:
            setattr(db_project, key, project_data[key])
    
    db_project.updated_at = datetime.utcnow()
    
    # If full data provided, update raw_data too
    if len(project_data) > len(valid_columns):
        # We might want to merge instead of overwrite, but for simplicity:
        db_project.raw_data = json.dumps(project_data)

    dao.update(db_project)
    return {"message": "Project updated successfully", "project": _convert_project_to_dict(db_project)}

def delete_project_data(project_id: str, session: Session) -> Dict[str, Any]:
    """Deletes a project"""
    dao = ProjectDAO(session)
    db_project = dao.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    dao.delete(db_project)
    return {"message": "Project deleted successfully"}
