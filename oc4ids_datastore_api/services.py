from oc4ids_datastore_api.models import (
    Project, ProjectType, Sector, ProjectSectorLink, 
    ProjectLocation, ProjectParty, ProjectBudget, 
    ProjectPeriod, ProjectDocument, ProjectIdentifier,
    PeriodType, Agency, Ministry, ProjectContractingProcess, Currency,
    PartyAdditionalIdentifier, AdditionalClassification, ProjectRelatedProject,
    ProjectCostMeasurement, CostGroup, CostItem,
    ProjectForecast, ForecastObservation,
    ProjectMetric, MetricObservation,
    ContractingProcessMilestone, ContractingProcessTransaction,
    ContractingProcessModification, ContractingProcessDocument,
    ProjectSocial, SocialHealthSafetyMaterialTest, SocialConsultationMeeting,
    ProjectEnvironment, EnvironmentGoal, EnvironmentClimateOversightType,
    EnvironmentConservationMeasure, EnvironmentEnvironmentalMeasure,
    EnvironmentClimateMeasure, EnvironmentImpactCategory,
    ProjectBenefit, BenefitBeneficiary,
    ProjectCompletion, ProjectLobbyingMeeting, BudgetBreakdown, BudgetBreakdownItem
)
from oc4ids_datastore_api.daos import ProjectDAO, ReferenceDataDAO
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

def _create_breakdown_item(session: Session, breakdown_id: int, item_data: Dict[str, Any]):
    amt = item_data.get("amount", {})
    # Handle flat amount/currency if present
    val_amount = amt.get("amount") if isinstance(amt, dict) else amt
    val_currency = amt.get("currency") if isinstance(amt, dict) else None
    
    period = item_data.get("period", {})
    source = item_data.get("sourceParty", {})
    
    item = BudgetBreakdownItem(
        breakdown_id=breakdown_id,
        local_id=item_data.get("id", str(uuid.uuid4())),
        description=item_data.get("description"),
        amount=val_amount,
        currency=val_currency,
        period_start_date=_parse_date(period.get("startDate")),
        period_end_date=_parse_date(period.get("endDate")),
        source_party_id=source.get("id"),
        source_party_name=source.get("name")
    )
    session.add(item)

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

# --- Sub-object Creation Helpers ---

def _create_cost_measurements(session: Session, project_id: uuid.UUID, data_list: List[Dict]):
    for cm in data_list:
        lc_cost = cm.get("lifeCycleCost", {})
        cm_obj = ProjectCostMeasurement(
            project_id=project_id,
            local_id=cm.get("id", str(uuid.uuid4())),
            measurement_date=_parse_date(cm.get("date")),
            lifecycle_cost_amount=lc_cost.get("amount") if lc_cost else None,
            lifecycle_cost_currency=lc_cost.get("currency") if lc_cost else None,
        )
        session.add(cm_obj)
        session.flush()

        for cg_data in cm.get("costBreakdown", []):
            cg_obj = CostGroup(
                cost_measurement_id=cm_obj.id,
                local_id=cg_data.get("id", str(uuid.uuid4())),
                category=cg_data.get("description")
            )
            session.add(cg_obj)
            session.flush()

            for item_data in cg_data.get("breakdown", []):
                amt_data = item_data.get("amount", {})
                ci_obj = CostItem(
                    cost_group_id=cg_obj.id,
                    local_id=item_data.get("id", str(uuid.uuid4())),
                    classification_description=item_data.get("description"),
                    amount=amt_data.get("amount"),
                    currency=amt_data.get("currency")
                )
                session.add(ci_obj)

def _create_forecasts(session: Session, project_id: uuid.UUID, data_list: List[Dict]):
    for f in data_list:
        f_obj = ProjectForecast(
            project_id=project_id,
            local_id=f.get("id", str(uuid.uuid4())),
            title=f.get("title"),
            description=f.get("description")
        )
        session.add(f_obj)
        session.flush()

        for obs_data in f.get("observations", []):
            val_data = obs_data.get("value", {})
            unit_data = obs_data.get("unit", {})
            period_data = obs_data.get("period", {})
            
            obs_obj = ForecastObservation(
                forecast_id=f_obj.id,
                local_id=obs_data.get("id", str(uuid.uuid4())),
                measure=obs_data.get("measure"),
                value_amount=val_data.get("amount"),
                value_currency=val_data.get("currency"),
                unit_name=unit_data.get("name"),
                unit_scheme=unit_data.get("scheme"),
                unit_id=unit_data.get("id"),
                period_start_date=_parse_date(period_data.get("startDate")),
                period_end_date=_parse_date(period_data.get("endDate"))
            )
            session.add(obs_obj)

def _create_metrics(session: Session, project_id: uuid.UUID, data_list: List[Dict]):
    for m in data_list:
        m_obj = ProjectMetric(
            project_id=project_id,
            local_id=m.get("id", str(uuid.uuid4())),
            title=m.get("title"),
            description=m.get("description")
        )
        session.add(m_obj)
        session.flush()

        for obs_data in m.get("observations", []):
            val_data = obs_data.get("value", {})
            unit_data = obs_data.get("unit", {})
            
            obs_obj = MetricObservation(
                metric_id=m_obj.id,
                local_id=obs_data.get("id", str(uuid.uuid4())),
                measure=obs_data.get("measure"),
                value_amount=val_data.get("amount"),
                value_currency=val_data.get("currency"),
                unit_name=unit_data.get("name")
            )
            session.add(obs_obj)

def _create_social(session: Session, project_id: uuid.UUID, data: Dict):
    # Handle landCompensationBudget which is different from landCompensation
    comp_data = data.get("landCompensationBudget", {}) 
    if not comp_data:
         comp_data = data.get("landCompensation", {})

    social_obj = ProjectSocial(
        project_id=project_id,
        in_indigenous_land=data.get("inIndigenousLand"),
        land_compensation_amount=comp_data.get("amount"),
        land_compensation_currency=comp_data.get("currency"),
        health_safety_material_test_description=data.get("healthAndSafety", {}).get("materialTests", {}).get("description")
    )
    session.add(social_obj)
    session.flush()

    # Health and Safety Material Tests
    hs_data = data.get("healthAndSafety", {})
    if "materialTests" in hs_data:
        tests = hs_data["materialTests"].get("tests", [])
        for test in tests:
            t_obj = SocialHealthSafetyMaterialTest(
                project_id=project_id,
                test=test
            )
            session.add(t_obj)

    # Consultation Meetings
    for mtg in data.get("consultationMeetings", []):
        addr = mtg.get("address", {})
        po = mtg.get("publicOffice", {})
        org = po.get("organization", {})
        
        m_obj = SocialConsultationMeeting(
            project_id=project_id,
            local_id=mtg.get("id", str(uuid.uuid4())),
            date=_parse_date(mtg.get("date")),
            number_of_participants=mtg.get("numberOfParticipants"),
            street_address=addr.get("streetAddress"),
            locality=addr.get("locality"),
            region=addr.get("region"),
            postal_code=addr.get("postalCode"),
            country_name=addr.get("countryName"),
            person_name=po.get("person", {}).get("name"),
            organization_name=org.get("name"),
            organization_id=org.get("id"),
            job_title=po.get("jobTitle")
        )
        session.add(m_obj)

def _create_environment(session: Session, project_id: uuid.UUID, data: Dict):
    abatement_cost = data.get("abatementCost", {})
    env_obj = ProjectEnvironment(
        project_id=project_id,
        has_impact_assessment=data.get("hasImpactAssessment"),
        in_protected_area=data.get("inProtectedArea"),
        abatement_cost_amount=abatement_cost.get("amount"),
        abatement_cost_currency=abatement_cost.get("currency")
    )
    session.add(env_obj)
    session.flush()

    for g in data.get("goals", []):
        session.add(EnvironmentGoal(project_id=project_id, goal=g))
    
    for c in data.get("climateOversightTypes", []):
        session.add(EnvironmentClimateOversightType(project_id=project_id, oversight_type=c))

    for cm in data.get("conservationMeasures", []):
         session.add(EnvironmentConservationMeasure(
             project_id=project_id, 
             type=cm.get("type"),
             description=cm.get("description")
         ))

    for em in data.get("environmentalMeasures", []):
         session.add(EnvironmentEnvironmentalMeasure(
             project_id=project_id, 
             type=em.get("type"),
             description=em.get("description") 
         ))
    
    for cm in data.get("climateMeasures", []):
         # climateMeasures type is a list of strings in example.json!
         c_types = cm.get("type", [])
         if isinstance(c_types, list):
             c_type_str = ", ".join(c_types)
         else:
             c_type_str = c_types
             
         session.add(EnvironmentClimateMeasure(
             project_id=project_id, 
             type=c_type_str,
             description=cm.get("description")
         ))

    for ic in data.get("impactCategories", []):
        session.add(EnvironmentImpactCategory(
            project_id=project_id, 
            category_scheme=ic.get("scheme"),
            category_id=ic.get("id")
        ))

def _create_benefits(session: Session, project_id: uuid.UUID, data_list: List[Dict]):
    for b in data_list:
        b_obj = ProjectBenefit(
            project_id=project_id,
            title=b.get("title"),
            description=b.get("description")
        )
        session.add(b_obj)
        session.flush()
        
        for ben in b.get("beneficiaries", []):
            ben_obj = BenefitBeneficiary(
                benefit_id=b_obj.id,
                description=ben.get("description"),
                number_of_people=ben.get("numberOfPeople")
            )
            session.add(ben_obj)

def _create_completion(session: Session, project_id: uuid.UUID, data: Dict):
    val_data = data.get("finalValue", {})
    comp_obj = ProjectCompletion(
        project_id=project_id,
        end_date=_parse_date(data.get("endDate")),
        final_scope=data.get("finalScope"),
        final_value_amount=val_data.get("amount"),
        final_value_currency=val_data.get("currency")
    )
    session.add(comp_obj)

# --- Service Functions ---

def get_all_projects_summary(
    session: Session, 
    page: int = 1, 
    page_size: int = 20,
    title: Optional[str] = None,
    sector_id: Optional[List[int]] = None,
    ministry_id: Optional[List[int]] = None,
    agency_id: Optional[List[int]] = None,
    concession_form: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None
) -> Dict[str, Any]:
    """Get project summaries for the list view (Optimized)"""
    dao = ProjectDAO(session)
    skip = (page - 1) * page_size
    
    results = dao.get_summaries(
        skip=skip, 
        limit=page_size,
        title=title,
        sector_id=sector_id,
        ministry_id=ministry_id,
        agency_id=agency_id,
        concession_form=concession_form,
        year_from=year_from,
        year_to=year_to
    )
    total = dao.count()
    
    data = []
    for row in results:
        ministries = []
        if row.ministry_names:
             ministries = list(set([m.strip() for m in row.ministry_names.split(',') if m.strip()]))
        
        private_parties = []
        if getattr(row, "private_party_name", None):
             private_parties = list(set([p.strip() for p in row.private_party_name.split(',') if p.strip()]))

        data.append({
            "id": str(row.id),
            "title": row.title,
            "ministry": ministries,
            "public_authority": row.agency_name,
            "private_parties": private_parties
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
    return project.to_oc4ids()

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
        "projects": [project_data]
    }

def create_project_data(project_data: Dict[str, Any], session: Session) -> Dict[str, Any]:
    """Validates and stores project data"""
    input_id = project_data.get("id")
    pid = None
    if input_id:
        try:
            pid = uuid.UUID(input_id)
        except (ValueError, TypeError):
            pass 
    
    if not pid:
        pid = uuid.uuid4()
        logger.warning(f"Project ID '{input_id}' is not a valid UUID. Generated new ID: {pid}")

    project_data["id"] = str(pid)
    project_id_str = project_data["id"]
    logger.info(f"Creating project {project_id_str}")

    # 1. Validation
    wrapped = add_metadata(project_data)
    validation_result = oc4ids_json_output(json_data=wrapped)
    if validation_result.get("validation_errors"):
       logger.warning(f"Validation errors for project {project_id_str}")

    # 2. Main Model Data
    model_data = {}
    valid_columns = ["id", "title", "description", "status", "purpose"]
    for col in valid_columns:
        if col in project_data:
            model_data[col] = project_data[col]
    
    if "type" in project_data:
        pt = _get_or_create_ref(session, ProjectType, "code", project_data["type"], {"name_en": project_data["type"]})
        model_data["project_type_id"] = pt.id

    # 4. Handle Parties & Public Authority
    parties_list = project_data.get("parties", [])
    
    public_authority_party = None
    for p in parties_list:
        roles = p.get("roles", [])
        if "publicAuthority" in roles or "actingPublicAuthority" in roles:
            public_authority_party = p
            break
            
    if public_authority_party:
        pa_name = public_authority_party.get("name")
        if pa_name:
            agency = _get_or_create_ref(session, Agency, "name_th", pa_name, {"name_en": pa_name})
            model_data["public_authority_id"] = agency.id

    db_project = Project(**model_data)

    # Save Project
    session.add(db_project)
    session.flush()
    
    # 3. Handle Relationships
    
    # - Identifiers
    if input_id:
        pid_obj = ProjectIdentifier(
            project_id=db_project.id,
            identifier_value=str(input_id),
            scheme="OC4IDS" 
        )
        session.add(pid_obj)

    # - Sectors
    if "sector" in project_data and isinstance(project_data["sector"], list):
        for s_code in project_data["sector"]:
             sector_obj = _get_or_create_ref(session, Sector, "code", s_code, {"name_en": s_code, "category": "General", "name_th": s_code})
             db_project.sectors.append(sector_obj)

    # - Additional Classifications
    if "additionalClassifications" in project_data:
        for ac in project_data["additionalClassifications"]:
            stmt = select(AdditionalClassification).where(
                AdditionalClassification.scheme == ac.get("scheme"),
                AdditionalClassification.code == ac.get("id")
            )
            ac_obj = session.exec(stmt).first()
            if not ac_obj:
                ac_obj = AdditionalClassification(
                    scheme=ac.get("scheme"),
                    code=ac.get("id"),
                    description=ac.get("description"),
                    uri=ac.get("uri")
                )
                session.add(ac_obj)
                session.flush()
            
            db_project.additional_classifications.append(ac_obj)

    # - Locations
    for loc in project_data.get("locations", []):
        l_obj = ProjectLocation(
            project_id=db_project.id,
                description=loc.get("description"),
            geometry_coordinates=loc.get("geometry"),
            street_address=loc.get("address", {}).get("streetAddress"),
            locality=loc.get("address", {}).get("locality"),
            region=loc.get("address", {}).get("region"),
            postal_code=loc.get("address", {}).get("postalCode"),
            country_name=loc.get("address", {}).get("countryName"),
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

    # - Budget
    if "budget" in project_data:
        b_data = project_data["budget"]
        # Handle 'amount' which might be an object
        amt_val = None
        curr_code = None
        
        if "amount" in b_data:
            if isinstance(b_data["amount"], dict):
                amt_val = b_data["amount"].get("amount")
                curr_code = b_data["amount"].get("currency")
            else:
                 # Flattened input?
                 amt_val = b_data.get("amount")
                 curr_code = b_data.get("currency")

        if curr_code:
            _ensure_currency(session, curr_code)

        b_obj = ProjectBudget(
            project_id=db_project.id,
            description=b_data.get("description"),
            total_amount=amt_val,
            currency=curr_code,
            request_date=_parse_date(b_data.get("requestDate")),
            approval_date=_parse_date(b_data.get("approvalDate"))
        )
        session.add(b_obj)
        session.flush()

        # Handle Breakdowns if present
        
        # 1. Flattened "breakdown" list (Legacy/Flat format)
        flat_breakdown = b_data.get("breakdown", [])
        if flat_breakdown:
             # Create a default group for flat items
             default_group = BudgetBreakdown(
                 budget_id=b_obj.id,
                 local_id=str(uuid.uuid4()),
                 description="Breakdown"
             )
             session.add(default_group)
             session.flush()
             
             for item_data in flat_breakdown:
                 _create_breakdown_item(session, default_group.id, item_data)

        # 2. Nested "budgetBreakdowns" (OC4IDS 0.9 format)
        if "budgetBreakdowns" in b_data:
             for group in b_data["budgetBreakdowns"]:
                  group_obj = BudgetBreakdown(
                      budget_id=b_obj.id,
                      local_id=group.get("id", str(uuid.uuid4())),
                      description=group.get("description")
                  )
                  session.add(group_obj)
                  session.flush()

                  # Process items in this group
                  items = group.get("budgetBreakdown", [])
                  for item_data in items:
                       _create_breakdown_item(session, group_obj.id, item_data)

    # - Periods (General & Lifecycle)
    period_keys = {
        "period": "duration", 
        "identificationPeriod": "identification", 
        "preparationPeriod": "preparation",
        "implementationPeriod": "implementation", 
        "completionPeriod": "completion", 
        "maintenancePeriod": "maintenance", 
        "decommissioningPeriod": "decommissioning",
        "assetLifetime": "assetLifetime"
    }

    for p_key, p_type in period_keys.items():
        if p_key in project_data and isinstance(project_data[p_key], dict):
             per = project_data[p_key]
             _get_or_create_ref(session, PeriodType, "code", p_type, {"name_en": p_type.capitalize() + " Period"})
             p_obj = ProjectPeriod(
                 project_id=db_project.id,
                 period_type=p_type,
                 start_date=_parse_date(per.get("startDate")),
                 end_date=_parse_date(per.get("endDate")),
                 duration_days=per.get("durationInDays"),
                 max_extent_date=_parse_date(per.get("maxExtentDate"))
             )
             session.add(p_obj)

    # - Identifiers (Original List)
    if "identifiers" in project_data and isinstance(project_data["identifiers"], list):
        for ident in project_data["identifiers"]:
            # Skip if matched previously? No, OC4IDS allows multiple
            pid_obj = ProjectIdentifier(
                project_id=db_project.id,
                identifier_value=ident.get("id"),
                scheme=ident.get("scheme")
            )
            session.add(pid_obj)

    # - Related Projects
    if "relatedProjects" in project_data:
        for rp in project_data["relatedProjects"]:
            rels = rp.get("relationship")
            rel_str = "related"
            if isinstance(rels, list) and rels:
                rel_str = rels[0]
            elif isinstance(rels, str):
                rel_str = rels
            
            rp_obj = ProjectRelatedProject(
                project_id=db_project.id,
                relationship_id=str(uuid.uuid4()),
                scheme=rp.get("scheme"),
                identifier=rp.get("id"),
                relationship=rel_str,
                title=rp.get("title"),
                uri=rp.get("uri")
            )
            session.add(rp_obj)

    # - Nested Objects
    if "costMeasurements" in project_data:
        _create_cost_measurements(session, db_project.id, project_data["costMeasurements"])
    
    if "forecasts" in project_data:
        _create_forecasts(session, db_project.id, project_data["forecasts"])
        
    if "metrics" in project_data:
        _create_metrics(session, db_project.id, project_data["metrics"])
    
    if "social" in project_data:
        _create_social(session, db_project.id, project_data["social"])
        
    if "environment" in project_data:
        _create_environment(session, db_project.id, project_data["environment"])
        
    if "benefits" in project_data:
        _create_benefits(session, db_project.id, project_data["benefits"])
        
    if "completion" in project_data:
        _create_completion(session, db_project.id, project_data["completion"])

    # - Parties (Full Details)
    for party in parties_list:
        legal_name = party.get("identifier", {}).get("legalName")
        if not legal_name and "additionalIdentifiers" in party:
            for ai in party["additionalIdentifiers"]:
                if ai.get("legalName"):
                    legal_name = ai.get("legalName")
                    break
        ministry_id = None
        if legal_name:
            agency_obj = _get_or_create_ref(session, Agency, "name_th", legal_name, {"name_en": legal_name})
            ministry_id = agency_obj.id

        p_obj = ProjectParty(
            project_id=db_project.id,
            local_id=party.get("id", str(uuid.uuid4())),
            name=party.get("name"),
            identifier_scheme=party.get("identifier", {}).get("scheme"),
            identifier_value=party.get("identifier", {}).get("id"),
            identifier_uri=party.get("identifier", {}).get("uri"),
            identifier_legal_name_id=ministry_id,
            street_address=party.get("address", {}).get("streetAddress"),
            locality=party.get("address", {}).get("locality"),
            region=party.get("address", {}).get("region"),
            postal_code=party.get("address", {}).get("postalCode"),
            country_name=party.get("address", {}).get("countryName"),
            contact_name=party.get("contactPoint", {}).get("name"),
            contact_email=party.get("contactPoint", {}).get("email"),
            contact_telephone=party.get("contactPoint", {}).get("telephone"),
            contact_fax=party.get("contactPoint", {}).get("fax"),
            contact_url=party.get("contactPoint", {}).get("url")
        )
        session.add(p_obj)
        session.flush()

        if "additionalIdentifiers" in party:
            for ai in party["additionalIdentifiers"]:
                ai_legal_name = ai.get("legalName")
                ai_ministry_id = None
                if ai_legal_name:
                     min_obj = _get_or_create_ref(session, Ministry, "name_th", ai_legal_name, {"name_en": ai_legal_name})
                     ai_ministry_id = min_obj.id
                
                ai_obj = PartyAdditionalIdentifier(
                    party_id=p_obj.id,
                    scheme=ai.get("scheme"),
                    identifier=ai.get("id"),
                    legal_name_id=ai_ministry_id,
                    uri=ai.get("uri")
                )
                session.add(ai_obj)

    # - Contracting Processes
    for cp in project_data.get("contractingProcesses", []):
        summary = cp.get("summary", {})
        
        c_amount = summary.get("contractValue", {}).get("amount")
        c_curr = summary.get("contractValue", {}).get("currency")
        _ensure_currency(session, c_curr)
        
        cp_obj = ProjectContractingProcess(
            project_id=db_project.id,
            local_id=cp.get("id", str(uuid.uuid4())),
            ocid=summary.get("ocid"),
            title=summary.get("title"),
            description=summary.get("description"),
            status=summary.get("status"),
            nature=summary.get("nature"), # dict/jsonb
            contract_amount=c_amount,
            contract_currency=c_curr,
            period_start_date=_parse_date(summary.get("contractPeriod", {}).get("startDate")),
            period_end_date=_parse_date(summary.get("contractPeriod", {}).get("endDate")),
            period_duration_days=summary.get("contractPeriod", {}).get("durationInDays")
        )
        session.add(cp_obj)
        session.flush()
        
        # Children
        for m in summary.get("milestones", []):
            val = m.get("value", {})
            m_obj = ContractingProcessMilestone(
                process_id=cp_obj.id,
                local_id=m.get("id", str(uuid.uuid4())),
                title=m.get("title"),
                type=m.get("type"),
                description=m.get("description"),
                code=m.get("code"),
                date=_parse_date(m.get("date")),
                date_met=_parse_date(m.get("dateMet")),
                date_modified=_parse_date(m.get("dateModified")),
                status=m.get("status"),
                value_amount=val.get("amount"),
                value_currency=val.get("currency")
            )
            session.add(m_obj)

        for t in summary.get("transactions", []):
            val = t.get("value", {})
            t_obj = ContractingProcessTransaction(
                process_id=cp_obj.id,
                local_id=t.get("id", str(uuid.uuid4())),
                source=t.get("source"),
                date=_parse_date(t.get("date")),
                amount=val.get("amount"),
                currency=val.get("currency"),
                payer_name=t.get("payer", {}).get("name"),
                payee_name=t.get("payee", {}).get("name"),
                uri=t.get("uri")
            )
            session.add(t_obj)
            
        for mod in summary.get("modifications", []):
             cv = mod.get("contractValue", {})
             orig = cv.get("originalAmount", {})
             new_val = cv.get("amount", {})
             mod_obj = ContractingProcessModification(
                process_id=cp_obj.id,
                local_id=mod.get("id", str(uuid.uuid4())),
                date=_parse_date(mod.get("date")),
                description=mod.get("description"),
                rationale=mod.get("rationale"),
                type=mod.get("type"),
                release_id=mod.get("releaseID"),
                old_amount=orig.get("amount"),
                old_currency=orig.get("currency"),
                new_amount=new_val.get("amount"),
                new_currency=new_val.get("currency")
            )
             session.add(mod_obj)
            
        for d in summary.get("documents", []):
            d_obj = ContractingProcessDocument(
                process_id=cp_obj.id,
                local_id=d.get("id", str(uuid.uuid4())),
                document_type=d.get("documentType"),
                title=d.get("title"),
                description=d.get("description"),
                url=d.get("url"),
                date_published=_parse_date(d.get("datePublished")),
                format=d.get("format"),
                language=d.get("language")
            )
            session.add(d_obj)

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

    dao.delete(project_id)
    return {"message": "Project deleted successfully"}

def get_reference_info(session: Session) -> Dict[str, List[Dict[str, Any]]]:
    """Fetch reference/lookup data for dropdowns and filters"""
    dao = ReferenceDataDAO(session)
    
    # Fetch from database
    sectors = dao.get_sectors()
    ministries = dao.get_ministries()
    contract_types = dao.get_contract_types()
    project_types = dao.get_project_types()
    concession_forms = dao.get_concession_forms()
    
    return {
        "sector": [
            {"id": s.id, "value": s.name_th}
            for s in sectors
        ],
        "ministry": [
            {"id": m.id, "value": m.name_th}
            for m in ministries
        ],
        "contractType": [
            {"id": ct.id, "value": ct.description or ct.code}
            for ct in contract_types
        ],
        "projectType": [
            {"id": pt.id, "value": pt.name_th if pt.name_th else pt.code}
            for pt in project_types
        ],
        "concessionForm": [
            {"id": cf.id, "value": cf.description or cf.code}
            for cf in concession_forms
        ]
    }
