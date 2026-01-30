from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Body, Query
from sqlmodel import Session
from typing import Dict, Any, List, Optional
import json
import pandas as pd
from io import BytesIO

from oc4ids_datastore_api.database import get_session
from oc4ids_datastore_api.services import (
    get_all_projects_summary,
    get_project_by_id,
    create_project_data,
    update_project_data,
    delete_project_data,
    get_reference_info
)

router = APIRouter()

@router.get("/projects")
def read_projects(
    page: int = 1, 
    page_size: int = 20,
    title: Optional[str] = None,
    sector_id: Optional[List[int]] = Query(None),
    ministry_id: Optional[List[int]] = Query(None),
    agency_id: Optional[List[int]] = Query(None),
    concession_form: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Get all projects with pagination and filters (supports multiple IDs)"""
    return get_all_projects_summary(
        session, 
        page, 
        page_size,
        title=title,
        sector_id=sector_id,
        ministry_id=ministry_id,
        agency_id=agency_id,
        concession_form=concession_form,
        year_from=year_from,
        year_to=year_to
    )


@router.get("/projects/{project_id}")
def read_project(project_id: str, session: Session = Depends(get_session)) -> Dict[str, Any]:
    """Get a single project by ID in frontend format"""
    project = get_project_by_id(session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), session: Session = Depends(get_session)):
    filename = file.filename
    ext = filename.split(".")[-1].lower()

    try:
        if ext == "json":
            contents = await file.read()
            data = json.loads(contents)
            
            # Handle OC4IDS Package format (has 'projects' list)
            if "projects" in data and isinstance(data["projects"], list):
                results = []
                for p_data in data["projects"]:
                    # Basic error handling for each project
                    try:
                        res = create_project_data(p_data, session)
                        results.append(res)
                    except Exception as e:
                        results.append({"error": str(e), "project_title": p_data.get("title")})
                return {"status": "success", "results": results}
            
            # Helper for single project file
            return create_project_data(data, session)

        elif ext == "csv":
            contents = await file.read()
            df = pd.read_csv(BytesIO(contents))
            return {"status": "success", "data": df.to_dict(orient="records")}

        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/projects")
def create_project(project_data: Dict[str, Any] = Body(...), session: Session = Depends(get_session)):
    """
    Create a new project.
    Using 'def' (Sync) instead of 'async def' to ensure blocking DB operations 
    run in a threadpool and don't block the main event loop.
    """
    return create_project_data(project_data, session)


@router.put("/projects/{project_id}")
def update_project(project_id: str, project_data: Dict[str, Any] = Body(...), session: Session = Depends(get_session)):
    """Update an existing project"""
    return update_project_data(project_id, project_data, session)


@router.delete("/projects/{project_id}")
def delete_project(project_id: str, session: Session = Depends(get_session)):
    """Delete a project"""
    return delete_project_data(project_id, session)

@router.get("/info")
def get_info(session: Session = Depends(get_session)) -> Dict[str, List[Dict[str, Any]]]:
    """Get reference data for dropdowns (sectors, ministries, etc.)"""
    return get_reference_info(session)
