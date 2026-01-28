from oc4ids_datastore_api.models import (
    Project, ProjectType, Sector, ProjectSectorLink, 
    ProjectLocation, ProjectParty, ProjectBudget, 
    ProjectPeriod, ProjectDocument, ProjectIdentifier,
    PeriodType, Agency, Ministry, ProjectContractingProcess, Currency
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

# --- Helper Functions ---

def _ensure_currency(session: Session, code: str):
    if not code:
        return
    # Check if exists
    curr = session.get(Currency, code)
    if not curr:
        # Create new currency reference
        curr = Currency(code=code, name=code)
        session.add(curr)
        session.flush() # Ensure it exists for FK constraints

def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        # Handle "2023-01-01T00:00:00Z" and "2023-01-01"
        return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
    except ValueError:
        return None

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
    """Convert DB Project to Frontend Dict"""
    return {
        "id": str(project.id),
        "title": project.title,
        "description": project.description,
        "status": project.status,
        "purpose": project.purpose,
        "updated": project.updated_at.isoformat() if project.updated_at else None,
    }

# --- Service Functions ---

def get_all_projects_summary(session: Session, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """Get project summaries for the list view (Optimized)"""
    dao = ProjectDAO(session)
    skip = (page - 1) * page_size
    
    results = dao.get_summaries(skip=skip, limit=page_size)
    total = dao.count()
    
    data = []
    for row in results:
        ministries = []
        if row.ministry_names:
             # Split string and remove duplicates if any (Postgres string_agg might duplicate if join is many-to-many before agg)
             ministries = list(set([m.strip() for m in row.ministry_names.split(',') if m.strip()]))

        data.append({
            "id": str(row.id),
            "title": row.title,
            "ministry": ministries,
            "public_authority": row.agency_name
        })
    
    return {
        "data": data,
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
        
    # If we do not store raw_data in the new schema (we removed it in the new models.py?), 
    # we must reconstruct it. But wait, new init.sql didn't have raw_data column!
    # So we must return what we have in DB columns.
    
    # Constructing response object from DB relations
    response = {
        "id": str(project.id),
        "title": project.title,
        "description": project.description,
        "status": project.status,
        "purpose": project.purpose,
        "date_updated": project.updated_at.isoformat(),
        # Add basic children for view
        "sectors": [s.code for s in project.sectors],
        "locations": [{"geometry": loc.geometry_coordinates, "description": loc.description} for loc in project.locations_list],
    }
    return response

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
    # Note: ID in input might be string, but DB uses UUID. 
    # If input ID is not UUID, we must generate a new one.
    input_id = project_data.get("id")
    pid = None
    if input_id:
        try:
            pid = uuid.UUID(input_id)
        except (ValueError, TypeError):
            pass # Invalid UUID string
    
    if not pid:
        pid = uuid.uuid4() # Generate new
        logger.warning(f"Project ID '{input_id}' is not a valid UUID. Generated new ID: {pid}")

    project_data["id"] = str(pid) # Update data for consistency
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

    # 4. Handle Parties & Public Authority
    parties_list = project_data.get("parties", [])
    
    # Check for Public Authority in parties role -> For Agency Name
    public_authority_party = None
    for p in parties_list:
        roles = p.get("roles", [])
        if "publicAuthority" in roles or "actingPublicAuthority" in roles:
            public_authority_party = p
            break
            
    if public_authority_party:
        pa_name = public_authority_party.get("name")
        if pa_name:
            # Map to Agency table for quick lookup (Agency Name)
            agency = _get_or_create_ref(session, Agency, "name_th", pa_name, {"name_en": pa_name})
            model_data["public_authority_id"] = agency.id

    db_project = Project(**model_data)

    # Save Project (to get ID for children)
    session.add(db_project)
    session.flush() # Flush to populate db_project.id if auto-generated
    
    # 3. Handle Relationships (Normalization for querying)
    
    # Sectors
    if "sector" in project_data and isinstance(project_data["sector"], list):
        for s_code in project_data["sector"]:
             sector_obj = _get_or_create_ref(session, Sector, "code", s_code, {"name_en": s_code, "category": "General", "name_th": s_code})
             db_project.sectors.append(sector_obj)

    # - Locations
    for loc in project_data.get("locations", []):
        l_obj = ProjectLocation(
            project_id=db_project.id,
                description=loc.get("description"),
            geometry_coordinates=loc.get("geometry"),
            # Flatten address if present in location
            street_address=loc.get("address", {}).get("streetAddress"),
            locality=loc.get("address", {}).get("locality"),
        )
        session.add(l_obj)

    # - Documents
    for doc in project_data.get("documents", []):
         d_obj = ProjectDocument(
             project_id=db_project.id,
             local_id=doc.get("id", str(uuid.uuid4())),
             document_type=doc.get("documentType"),
             title=doc.get("title"),
             description=doc.get("description"),
             url=doc.get("url"),
             date_published=_parse_date(doc.get("datePublished")),
             date_modified=_parse_date(doc.get("dateModified")),
             format=doc.get("format"),
             author=doc.get("author")
         )
         session.add(d_obj)

    # - Parties (Full Details & Ministry Mapping)
    for party in parties_list:
        legal_name = party.get("identifier", {}).get("legalName")
        ministry_id = None
        if legal_name:
            # Map legalName to Ministry table (Ministry Name)
            min_obj = _get_or_create_ref(session, Ministry, "name_th", legal_name, {"name_en": legal_name})
            ministry_id = min_obj.id

        p_obj = ProjectParty(
            project_id=db_project.id,
            local_id=party.get("id", str(uuid.uuid4())),
            name=party.get("name"),
            identifier_scheme=party.get("identifier", {}).get("scheme"),
            identifier_value=party.get("identifier", {}).get("id"),
            identifier_uri=party.get("identifier", {}).get("uri"),
            identifier_legal_name_id=ministry_id, # Linking Ministry here
            
            # Flattened fields
            street_address=party.get("address", {}).get("streetAddress"),
            locality=party.get("address", {}).get("locality"),
            region=party.get("address", {}).get("region"),
            postal_code=party.get("address", {}).get("postalCode"),
            country_name=party.get("address", {}).get("countryName"),
            contact_name=party.get("contactPoint", {}).get("name"),
            contact_email=party.get("contactPoint", {}).get("email"),
            contact_telephone=party.get("contactPoint", {}).get("telephone")
        )
        session.add(p_obj)

    # - Contracting Processes
    for cp in project_data.get("contractingProcesses", []):
        summary = cp.get("summary", {})
        
        c_amount = summary.get("contractValue", {}).get("amount")
        c_curr = summary.get("contractValue", {}).get("currency")
        _ensure_currency(session, c_curr) # Prevent FK Error
        
        # Flattened structure
        cp_obj = ProjectContractingProcess(
            project_id=db_project.id,
            local_id=cp.get("id", str(uuid.uuid4())),
            
            # Summary fields
            ocid=summary.get("ocid"),
            title=summary.get("title"),
            description=summary.get("description"),
            status=summary.get("status"),
            nature=summary.get("nature"), # dict/jsonb
            
            # Flatten Value (from summary.contractValue)
            contract_amount=c_amount,
            contract_currency=c_curr,
            
            # Flatten Period (from summary.contractPeriod)
            period_start_date=_parse_date(summary.get("contractPeriod", {}).get("startDate")),
            period_end_date=_parse_date(summary.get("contractPeriod", {}).get("endDate")),
            period_duration_days=summary.get("contractPeriod", {}).get("durationInDays")
        )
        session.add(cp_obj)

    # Commit all changes
    session.commit()
    session.refresh(db_project)
    
    return {"message": "Project created successfully", "project": {"id": str(db_project.id), "title": db_project.title}}

def update_project_data(project_id: str, project_data: Dict[str, Any], session: Session) -> Dict[str, Any]:
    # Placeholder for update logic (would require more complex diffing for child tables)
    raise NotImplementedError("Update logic needs to be refactored for new schema")

def delete_project_data(project_id: str, session: Session) -> Dict[str, Any]:
    """Deletes a project"""
    dao = ProjectDAO(session)
    db_project = dao.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    dao.delete(db_project)
    return {"message": "Project deleted successfully"}
