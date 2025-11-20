from oc4ids_datastore_api.models import ProjectSQLModel
from oc4ids_datastore_api.schemas import Dataset, Download, License, Portal, Publisher

from sqlmodel import Session, select
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests


def _convert_project_to_dict(project: ProjectSQLModel) -> Dict[str, Any]:
    """Convert ProjectSQLModel to ProjectData format expected by frontend"""
    result: Dict[str, Any] = {
        "id": project.id or "",
        "updated": project.updated.isoformat() if project.updated else datetime.utcnow().isoformat(),
        "title": project.title or "",
        "description": project.description or "",
        "status": project.status or "active",
        "type": project.type or "",
        "purpose": project.purpose or "",
        "language": project.language or "th",
    }
    
    # Convert period
    if project.period:
        result["period"] = {
            "startDate": project.period.get("startDate", "") or "",
            "endDate": project.period.get("endDate", "") or "",
            "durationInDays": project.period.get("durationInDays"),
            "durationInMonths": project.period.get("durationInMonths"),
        }
    else:
        result["period"] = {
            "startDate": "",
            "endDate": "",
        }
    
    # Convert optional periods
    if project.identification_period:
        result["identificationPeriod"] = {
            "startDate": project.identification_period.get("startDate", "") or "",
            "endDate": project.identification_period.get("endDate", "") or "",
        }
    
    if project.preparation_period:
        result["preparationPeriod"] = {
            "startDate": project.preparation_period.get("startDate", "") or "",
            "endDate": project.preparation_period.get("endDate", "") or "",
        }
    
    if project.implementation_period:
        result["implementationPeriod"] = {
            "startDate": project.implementation_period.get("startDate", "") or "",
            "endDate": project.implementation_period.get("endDate", "") or "",
        }
    
    if project.completion_period:
        result["completionPeriod"] = {
            "startDate": project.completion_period.get("startDate", "") or "",
            "endDate": project.completion_period.get("endDate", "") or "",
        }
    
    if project.maintenance_period:
        result["maintenancePeriod"] = {
            "startDate": project.maintenance_period.get("startDate", "") or "",
            "endDate": project.maintenance_period.get("endDate", "") or "",
        }
    
    if project.decommissioning_period:
        result["decommissioningPeriod"] = {
            "startDate": project.decommissioning_period.get("startDate", "") or "",
            "endDate": project.decommissioning_period.get("endDate", "") or "",
        }
    
    # Convert sector (can be list or dict in database)
    if project.sector:
        if isinstance(project.sector, list):
            result["sector"] = project.sector
        else:
            result["sector"] = project.sector.get("sector", []) if isinstance(project.sector, dict) else []
    else:
        result["sector"] = []
    
    # Convert locations
    if project.locations:
        if isinstance(project.locations, list):
            result["locations"] = project.locations
        else:
            result["locations"] = project.locations.get("locations", []) if isinstance(project.locations, dict) else []
    else:
        result["locations"] = []
    
    # Convert budget - ensure it has the correct structure
    if project.budget:
        budget = project.budget
        # Ensure budget has amount field with correct structure
        if not isinstance(budget, dict):
            budget = {}
        
        # Ensure amount field exists and has correct structure
        if "amount" not in budget or not isinstance(budget.get("amount"), dict):
            budget["amount"] = {
                "amount": budget.get("amount", {}).get("amount", 0) if isinstance(budget.get("amount"), dict) else (
                    budget.get("amount", 0) if isinstance(budget.get("amount"), (int, float)) else 0
                ),
                "currency": budget.get("amount", {}).get("currency", "THB") if isinstance(budget.get("amount"), dict) else (
                    budget.get("currency", "THB")
                )
            }
        
        # Ensure amount.amount is a number
        if not isinstance(budget["amount"].get("amount"), (int, float)):
            try:
                budget["amount"]["amount"] = float(budget["amount"]["amount"]) if budget["amount"]["amount"] else 0
            except (ValueError, TypeError):
                budget["amount"]["amount"] = 0
        
        # Ensure amount.currency exists
        if "currency" not in budget["amount"] or not budget["amount"]["currency"]:
            budget["amount"]["currency"] = "THB"
        
        # Ensure description exists
        if "description" not in budget:
            budget["description"] = ""
        
        result["budget"] = budget
    else:
        result["budget"] = {
            "description": "",
            "amount": {
                "amount": 0,
                "currency": "THB"
            }
        }
    
    # Convert parties
    if project.parties:
        if isinstance(project.parties, list):
            result["parties"] = project.parties
        else:
            result["parties"] = project.parties.get("parties", []) if isinstance(project.parties, dict) else []
    else:
        result["parties"] = []
    
    # Convert public authority
    if project.public_authority:
        result["publicAuthority"] = project.public_authority
    else:
        result["publicAuthority"] = {
            "name": "",
            "id": ""
        }
    
    # Convert identifiers
    if project.identifiers:
        if isinstance(project.identifiers, list):
            result["identifiers"] = project.identifiers
        else:
            result["identifiers"] = project.identifiers.get("identifiers", []) if isinstance(project.identifiers, dict) else []
    else:
        result["identifiers"] = []
    
    # Convert optional fields
    if project.additional_classifications:
        result["additionalClassifications"] = project.additional_classifications if isinstance(project.additional_classifications, list) else []
    else:
        result["additionalClassifications"] = []
    
    if project.related_projects:
        result["relatedProjects"] = project.related_projects if isinstance(project.related_projects, list) else []
    
    if project.asset_lifetime:
        result["assetLifetime"] = project.asset_lifetime
    
    if project.documents:
        result["documents"] = project.documents if isinstance(project.documents, list) else []
    
    if project.forecasts:
        result["forecasts"] = project.forecasts if isinstance(project.forecasts, list) else []
    
    if project.metrics:
        result["metrics"] = project.metrics if isinstance(project.metrics, list) else []
    
    if project.cost_measurements:
        result["costMeasurements"] = project.cost_measurements if isinstance(project.cost_measurements, list) else []
    
    if project.contracting_processes:
        result["contractingProcesses"] = project.contracting_processes if isinstance(project.contracting_processes, list) else []
    
    if project.milestones:
        result["milestones"] = project.milestones if isinstance(project.milestones, list) else []
    
    if project.transactions:
        result["transactions"] = project.transactions if isinstance(project.transactions, list) else []
    
    if project.completion:
        result["completion"] = project.completion
    
    if project.lobbying_meetings:
        result["lobbyingMeetings"] = project.lobbying_meetings if isinstance(project.lobbying_meetings, list) else []
    
    if project.social:
        result["social"] = project.social
    
    if project.environment:
        result["environment"] = project.environment
    
    if project.policy_alignment:
        result["policyAlignment"] = project.policy_alignment
    
    if project.benefits:
        result["benefits"] = project.benefits if isinstance(project.benefits, list) else []
    
    return result


def get_all_datasets(session: Session) -> List[Dict[str, Any]]:
    """Get all projects and convert to frontend format"""
    projects = session.exec(select(ProjectSQLModel)).all()
    return [_convert_project_to_dict(p) for p in projects]


def get_project_by_id(session: Session, project_id: str) -> Optional[Dict[str, Any]]:
    """Get a single project by ID and convert to frontend format"""
    project = session.get(ProjectSQLModel, project_id)
    if not project:
        return None
    return _convert_project_to_dict(project)
