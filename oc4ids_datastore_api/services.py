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
    ProjectCompletion, ProjectLobbyingMeeting, BudgetBreakdown, BudgetBreakdownItem,
    ProjectFinance, PartyRole, PartyPerson, PartyBeneficialOwner, BeneficialOwnerNationality, PartyClassification,
    ContractingTender, ContractingTenderTenderer, ContractingTenderEntity, ContractingTenderSustainability, 
    ContractingSupplier, ContractingSocial, ContractingRelease, LocationGazetteer, LocationGazetteerIdentifier,
    ProjectPolicyAlignment, ProjectPolicyAlignmentPolicy, ProjectAssetLifetime
)
from oc4ids_datastore_api.daos import ProjectDAO, ReferenceDataDAO
from oc4ids_datastore_api.utils import format_thai_amount
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
    curr = session.get(Currency, code)
    if not curr:
        curr = Currency(code=code, name=code)
        session.add(curr)
        session.flush()

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
            val_data = obs_data.get("value") or {}
            unit_data = obs_data.get("unit") or {}
            
            obs_obj = MetricObservation(
                metric_id=m_obj.id,
                local_id=obs_data.get("id", str(uuid.uuid4())),
                measure=obs_data.get("measure"),
                value_amount=val_data.get("amount") if val_data else None,
                value_currency=val_data.get("currency") if val_data else None,
                unit_name=unit_data.get("name") if unit_data else None
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

def _create_party_details(session: Session, party_id: int, party_data: Dict[str, Any]):
    """Creates detailed party information (Roles, People, BOs, Classifications)"""
    
    # Roles
    for role in party_data.get("roles", []):
         r_obj = PartyRole(party_id=party_id, role=role)
         session.add(r_obj)

    # People (members)
    for person in party_data.get("memberOf", []): # 'memberOf' is often used for people in OC4IDS context or 'person' list?
         # Checking example.json structure for people... usually it's under 'persons' or similar extensions, 
         # but standard OC4IDS 0.9 defines 'memberOf' as organization memberships. 
         # Wait, looking at schema 'party_people'. 
         # Let's assume input data has 'person' list if it exists, or check 'members'.
         pass # OC4IDS standard 'parties' doesn't strictly have a 'people' list in core, might be an extension.
         # However, we have a table for it. Let's support 'persons' key if present.
    
    # Actually, let's implement based on common OCDS extensions or our schema.
    # Schema has: name, job_title.
    if "persons" in party_data:
        for p in party_data["persons"]:
             p_obj = PartyPerson(
                 party_id=party_id,
                 local_id=p.get("id", str(uuid.uuid4())),
                 name=p.get("name"),
                 job_title=p.get("jobTitle")
             )
             session.add(p_obj)

    # Beneficial Owners
    if "beneficialOwners" in party_data:
        for bo in party_data["beneficialOwners"]:
             bo_obj = PartyBeneficialOwner(
                 party_id=party_id,
                 local_id=bo.get("id", str(uuid.uuid4())),
                 name=bo.get("name"),
                 email=bo.get("email"),
                 telephone=bo.get("telephone"),
                 fax_number=bo.get("faxNumber"),
                 identifier_scheme=bo.get("identifier", {}).get("scheme"),
                 identifier_value=bo.get("identifier", {}).get("id"),
                 street_address=bo.get("address", {}).get("streetAddress"),
                 locality=bo.get("address", {}).get("locality"),
                 region=bo.get("address", {}).get("region"),
                 postal_code=bo.get("address", {}).get("postalCode"),
                 country_name=bo.get("address", {}).get("countryName")
             )
             session.add(bo_obj)
             session.flush()
             
             for nat in bo.get("nationalities", []):
                  session.add(BeneficialOwnerNationality(owner_id=bo_obj.id, nationality=nat))

    # Classifications
    if "details" in party_data and "classifications" in party_data["details"]:
         # OC4IDS parties details extension? Or direct 'details' object
         pass

    # Direct classifications list if exists
    if "additionalClassifications" in party_data: # We used this for PartyAdditionalIdentifier
         pass 
         
    # If there's a specific classifications field
    if "classifications" in party_data:
         for c in party_data["classifications"]:
              session.add(PartyClassification(
                  party_id=party_id,
                  scheme=c.get("scheme"),
                  classification_id=c.get("id")
              ))

# --- Service Functions ---

def _create_contracting_tenders(session: Session, process_id: int, summary_data: Dict[str, Any]):
    """Creates tender and supplier related data for a contracting process"""
    
    # Tender
    t_data = summary_data.get("tender", {})
    if t_data:
        tender = ContractingTender(
            process_id=process_id,
            procurement_method=t_data.get("procurementMethod"),
            procurement_method_details=t_data.get("procurementMethodDetails"),
            date_published=_parse_date(t_data.get("datePublished")),
            cost_estimate_amount=t_data.get("value", {}).get("amount"),
            cost_estimate_currency=t_data.get("value", {}).get("currency"),
            number_of_tenderers=t_data.get("numberOfTenderers")
        )
        session.add(tender)
        
        # Tenderers
        for tenderer in t_data.get("tenderers", []):
            session.add(ContractingTenderTenderer(
                process_id=process_id,
                local_id=tenderer.get("id", str(uuid.uuid4())),
                name=tenderer.get("name")
            ))
            
        # Procuring Entities (using 'tender_entities' table)
        if "procuringEntity" in t_data and isinstance(t_data["procuringEntity"], dict):
             ent = t_data["procuringEntity"]
             session.add(ContractingTenderEntity(
                 process_id=process_id,
                 role="procuringEntity",
                 name=ent.get("name")
             ))
        
        # Sustainability
        for s in t_data.get("sustainability", []):
                session.add(ContractingTenderSustainability(
                    process_id=process_id, 
                    strategies=s if isinstance(s, list) else [s] # Ensure list for JSONB
                ))

    # Suppliers
    for supp in summary_data.get("suppliers", []):
         session.add(ContractingSupplier(
             process_id=process_id,
             local_id=supp.get("id", str(uuid.uuid4())),
             name=supp.get("name")
         ))

def _create_contracting_details(session: Session, process_id: int, summary_data: Dict[str, Any]):
    """Creates other contracting details (Social, Releases)"""
    
    if "social" in summary_data:
         soc = summary_data["social"]
         lb = soc.get("laborBudget", {})
         
         session.add(ContractingSocial(
             process_id=process_id,
             labor_budget_amount=lb.get("amount"),
             labor_budget_currency=lb.get("currency"),
             labor_obligations=soc.get("laborObligations"), # JSONB
             labor_description=soc.get("description")
         ))
         
    # Releases
    for rel in summary_data.get("releases", []):
         session.add(ContractingRelease(
             process_id=process_id,
             local_id=rel.get("id", str(uuid.uuid4())),
             tag=rel.get("tag"), # List of strings
             date=_parse_date(rel.get("date")),
             url=rel.get("url")
         ))

def _create_project_finance(session: Session, budget_id: int, finance_list: List[Dict]):
    for fin in finance_list:
        val = fin.get("value", {})
        session.add(ProjectFinance(
             budget_id=budget_id,
             local_id=fin.get("id", str(uuid.uuid4())),
             asset_class=fin.get("assetClass"),
             type=fin.get("type"),
             concessional=fin.get("concessional"),
             value_amount=val.get("amount"),
             #(FIX)In the future I will change currency to a separate table, we already have a table for currency
             value_currency=val.get("currency"),
             source=fin.get("source"),
             financing_party_id=fin.get("financingParty", {}).get("id"),
             financing_party_name=fin.get("financingParty", {}).get("name"),
             period_start_date=_parse_date(fin.get("period", {}).get("startDate")),
             period_end_date=_parse_date(fin.get("period", {}).get("endDate")),
             payment_period_start_date=_parse_date(fin.get("paymentPeriod", {}).get("startDate")),
             payment_period_end_date=_parse_date(fin.get("paymentPeriod", {}).get("endDate")),
             interest_rate_margin=fin.get("interestRateMargin"),
             description=fin.get("description")
        ))

def _create_location_gazetteers(session: Session, location_id: uuid.UUID, gazetteers: List[Dict]):
    for gaz in gazetteers:
         g_obj = LocationGazetteer(
             location_id=location_id,
             scheme=gaz.get("scheme")
         )
         session.add(g_obj)
         session.flush()
         
         for ident in gaz.get("identifiers", []): # List of strings usually in OCDS
              if isinstance(ident, str):
                  session.add(LocationGazetteerIdentifier(gazetteer_id=g_obj.id, identifier=ident))

def _create_lobbying(session: Session, project_id: uuid.UUID, meetings: List[Dict]):
    for m in meetings:
        addr = m.get("address", {})
        po = m.get("publicOffice", {}) # Person/Org
        session.add(ProjectLobbyingMeeting(
            project_id=project_id,
            local_id=m.get("id", str(uuid.uuid4())),
            meeting_date=_parse_date(m.get("date")),
            number_of_participants=m.get("numberOfParticipants"),
            street_address=addr.get("streetAddress"),
            locality=addr.get("locality"),
            region=addr.get("region"),
            postal_code=addr.get("postalCode"),
            country_name=addr.get("countryName"),
            public_office_job_title=po.get("jobTitle"),
            public_office_person_name=po.get("name"), # If person object?
            public_office_org_name=po.get("organization", {}).get("name"),
            public_office_org_id=po.get("organization", {}).get("id")
        ))

def _create_policy(session: Session, project_id: uuid.UUID, policy_data: Any):
     if isinstance(policy_data, dict):
          pa = ProjectPolicyAlignment(
              project_id=project_id,
              description=policy_data.get("description")
          )
          session.add(pa)
          session.flush() # Ensure existence
          
          for p in policy_data.get("policies", []):
               session.add(ProjectPolicyAlignmentPolicy(project_id=project_id, policy=p))

def _create_asset_lifetime(session: Session, project_id: uuid.UUID, lifetime_data: Dict):
    if not lifetime_data:
        return
    session.add(ProjectAssetLifetime(
        project_id=project_id,
        period_start_date=_parse_date(lifetime_data.get("startDate")),
        period_end_date=_parse_date(lifetime_data.get("endDate")),
        period_max_extent_date=_parse_date(lifetime_data.get("maxExtentDate")),
        period_duration_days=lifetime_data.get("durationInDays")
    ))


def get_all_projects(
    session: Session, 
    page: int = 1, 
    page_size: int = 20,
    title: Optional[str] = None,
    sector_id: Optional[List[int]] = None,
    ministry_id: Optional[List[int]] = None,
    concession_form_id: Optional[List[int]] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None
) -> Dict[str, Any]:
    dao = ProjectDAO(session)
    skip = (page - 1) * page_size
    
    results = dao.get_projects(
        skip=skip, 
        limit=page_size,
        title=title,
        sector_id=sector_id,
        ministry_id=ministry_id,
        concession_form_id=concession_form_id,
        year_from=year_from,
        year_to=year_to
    )
    total = dao.count()
    
    data = []
    for row in results:
        ministries = set()
        if hasattr(row, 'party_ministry_names') and row.party_ministry_names:
            ministries.update([m.strip() for m in row.party_ministry_names.split(',') if m.strip()])
            
        ministry_list = list(ministries)
        
        # Process Private Parties
        private_parties = []
        if getattr(row, "private_party_name", None):
             private_parties = [p.strip() for p in row.private_party_name.split(",") if p.strip()]

        data.append({
            "id": str(row.id),
            "title": row.title,
            "ministry": ministry_list,
            "public_authority": row.agency_name, 
            "private_parties": private_parties,
            "sector": row.sector_names,
            "concession": row.concession_names,
            "start_date": row.start_date,
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
    """Get a single project by ID and convert to frontline format"""
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
    logger.info(f"Creating project data for {project_id_str}")

    # 1. Validation
    # wrapped = add_metadata(project_data)
    # try:
    #     validation_result = oc4ids_json_output(json_data=wrapped)
    #     if validation_result.get("validation_errors"):
    #         logger.warning(f"Validation errors for project {project_id_str}")
    # except Exception as e:
    #     logger.warning(f"Validation skipped due to error (likely network): {e}")

    missing_fields = []

    period_data = project_data.get("period", {})
    if not period_data or (not period_data.get("durationInDays") and not (period_data.get("startDate") and period_data.get("endDate"))):
         missing_fields.append("period")

    if "publicAuthority" not in project_data or not project_data.get("publicAuthority", {}).get("name"):
        missing_fields.append("publicAuthority")
    
    parties_list = project_data.get("parties", [])
    has_private_party = False
    
    for p in parties_list:
        identifier = p.get("identifier", {})
        if identifier.get("legalName"):
            has_private_party = True
            break
    
    if not has_private_party:
        missing_fields.append("privateParty")

    if missing_fields:
        error_msg = f"Missing mandatory fields: {', '.join(missing_fields)}"
        logger.error(f"Validation failed for project {project_id_str}: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)

    model_data = {}
    valid_columns = ["id", "title", "description", "status", "purpose"]
    for col in valid_columns:
        if col in project_data:
            model_data[col] = project_data[col]
    
    pt = _get_or_create_ref(session, ProjectType, "code", project_data["type"], {"name_en": project_data["type"]})
    model_data["project_type_id"] = pt.id

    if "publicAuthority" in project_data:
        pa_data = project_data["publicAuthority"]
        pa_name = pa_data.get("name")
        if pa_name:
            agency = _get_or_create_ref(session, Agency, "name_th", pa_name, {"name_en": pa_name})
            model_data["public_authority_id"] = agency.id
        else:
            raise HTTPException(status_code=400, detail="Public Authority exists but has no name.")

    db_project = Project(**model_data)

    session.add(db_project)
    session.flush()
    

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
        for s_data in project_data["sector"]:
            if isinstance(s_data, dict):
                s_code = s_data.get("id")
                s_description = s_data.get("description", "")
            else:
                s_code = s_data
                s_description = ""
            
            stmt = select(Sector).where(Sector.code == s_code)
            sector_obj = session.exec(stmt).first()
            
            #(FIX) In the future I will remove this part only allow existing sectors
            if not sector_obj:
                sector_obj = Sector(
                    code=s_code,
                    name_th=s_description,  # ใช้ description เป็น name_th
                    name_en=s_code,
                    description=s_description,
                    is_active=True,
                    category=s_data.get("category", "") if isinstance(s_data, dict) else ""
                )
                session.add(sector_obj)
                session.flush()
            
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
        session.flush()
        
        if "gazetteers" in loc:
            _create_location_gazetteers(session, l_obj.id, loc["gazetteers"])

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
        amt_val = None
        curr_code = None
        
        if "amount" in b_data:
            if isinstance(b_data["amount"], dict):
                amt_val = b_data["amount"].get("amount")
                curr_code = b_data["amount"].get("currency")
            else:
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

        # 3. Project Finance
        if "finance" in b_data:
            _create_project_finance(session, b_obj.id, b_data["finance"])

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

    # - Identifiers
    if "identifiers" in project_data and isinstance(project_data["identifiers"], list):
        for ident in project_data["identifiers"]:
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

    #(REVIEW) I will review this part later
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
        
    if "lobbyingMeetings" in project_data:
        _create_lobbying(session, db_project.id, project_data["lobbyingMeetings"])
        
    if "policyAlignment" in project_data:
        _create_policy(session, db_project.id, project_data["policyAlignment"])
        
    if "assetLifetime" in project_data:
        _create_asset_lifetime(session, db_project.id, project_data["assetLifetime"])
    #(end of REVIEW)


    # - Parties (Full Details)
    parties_list = project_data.get("parties", [])
    for party in parties_list:
        legal_name = party.get("identifier", {}).get("legalName")
    
        agency_id = None
        if legal_name:
            #(FIX) I this case agency should create if not exist ministry and add id to ministry_id in agency table
            agency_obj = _get_or_create_ref(session, Agency, "name_th", legal_name, {"name_en": legal_name})
            agency_id = agency_obj.id

        p_obj = ProjectParty(
            project_id=db_project.id,
            local_id=party.get("id", str(uuid.uuid4())),
            name=party.get("name"),
            identifier_scheme=party.get("identifier", {}).get("scheme"),
            identifier_value=party.get("identifier", {}).get("id"),
            identifier_uri=party.get("identifier", {}).get("uri"),
            identifier_legal_name_id=agency_id,
            street_address=party.get("address", {}).get("streetAddress"),
            locality=party.get("address", {}).get("locality"),
            region=party.get("address", {}).get("region"),
            postal_code=party.get("address", {}).get("postalCode"),
            country_name=party.get("address", {}).get("countryName"),
            contact_name=party.get("contactPoint", {}).get("name"),
            contact_email=party.get("contactPoint", {}).get("email"),
            contact_telephone=party.get("contactPoint", {}).get("telephone"),
            contact_fax=party.get("contactPoint", {}).get("fax"),
            contact_url=party.get("contactPoint", {}).get("url"),
            role=party.get("role")
            #(FIX) Add new field people beneficialOwner,Classification
            
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

        # Create nested party details
        _create_party_details(session, p_obj.id, party)

    #(REVIEW) I will review this part later
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

        # Tenders & Suppliers
        _create_contracting_tenders(session, cp_obj.id, summary)
        
        # Social & Releases
        _create_contracting_details(session, cp_obj.id, summary)
    #(end of REVIEW)

    # Commit all changes
    try:
        session.commit()
        logger.info(f"Successfully committed project {project_id_str}")
    except Exception as e:
        logger.error(f"Error committing project {project_id_str}: {e}")
        session.rollback()
        raise e
        
    session.refresh(db_project)
    
    return {"message": "Project created successfully", "project": {"id": str(db_project.id), "title": db_project.title}}

def update_project_data(project_id: str, project_data: Dict[str, Any], session: Session) -> Dict[str, Any]:
    """Updates an existing project by deleting and recreating it"""
    logger.info(f"Starting update for project {project_id}")
    # 1. Verify existence and consistency
    dao = ProjectDAO(session)
    existing_project = dao.get_by_id(project_id)
    
    if not existing_project:
        logger.error(f"Project {project_id} not found during update")
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    # 2. Delete existing project
    # This will cascade delete all related records due to ON DELETE CASCADE or manual cleanup in DAO
    # We call delete directly. delete() method handles existence check internally.
    try:
        logger.info(f"Deleting existing project {project_id}")
        dao.delete(project_id)
        logger.info(f"Deleted existing project {project_id}")
    except ValueError as e:
         logger.error(f"Error deleting project {project_id}: {e}")
         raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    except Exception as e:
         logger.error(f"Unexpected error deleting project {project_id}: {e}")
         raise e
    
    # Ensure session is clean for new insertion
    session.expire_all()
    
    # 3. Create new project with the same ID
    # Ensure ID in data matches the URL endpoint ID
    project_data["id"] = project_id
    
    logger.info(f"Re-creating project {project_id} with new data")
    try:
        return create_project_data(project_data, session)
    except Exception as e:
        logger.error(f"Error re-creating project {project_id}: {e}")
        raise e

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
        "projectType": [
            {"id": pt.id, "value": pt.name_th if pt.name_th else pt.code}
            for pt in project_types
        ],
        "concessionForm": [
            {"id": cf.id, "value": cf.description or cf.code}
            for cf in concession_forms
        ]
    }

def get_dashboard_summary(
    session: Session, 
    sector_id: Optional[List[int]] = None,
    ministry_id: Optional[List[int]] = None,
    agency_id: Optional[List[int]] = None,
    concession_form_id: Optional[List[int]] = None,
    contract_type_id: Optional[List[int]] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    search: Optional[str] = None
) -> Dict[str, Any]:
    """Get dashboard summary statistics and latest projects matching filters"""
    dao = ProjectDAO(session)
    projects = dao.get_summaries(
        limit=10000,
        title=search,
        sector_id=sector_id,
        ministry_id=ministry_id,
        agency_id=agency_id,
        concession_form_id=concession_form_id,
        contract_type_id=contract_type_id,
        year_from=year_from,
        year_to=year_to
    )
    
    total_projects = len(projects)
    unique_contractors = set()
    total_investment = 0
    max_budget = 0  # Track maximum budget
    ministry_counts = {}
    ministry_investments = {}
    
    # Project Scales Buckets (THB Million)
    # Small < 1,000M
    # Medium 1,000M - 5,000M
    # Big > 5,000M
    project_scales = {
        "small": {"count": 0, "investment": 0},
        "medium": {"count": 0, "investment": 0},
        "big": {"count": 0, "investment": 0}
    }
    
    investment_by_year = {} # year -> total_amount
    
    # Sector Stats with Scale Breakdown
    sector_stats = {} 
    # Structure: sector_name -> { total: {}, small: {}, medium: {}, big: {} }
    latest_projects_data = []

    for idx, p in enumerate(projects):
        # Budget
        amt = getattr(p, "budget_amount", 0) or 0
        total_investment += amt
        if amt > max_budget:
            max_budget = amt
        
        # Contractors
        if getattr(p, "private_party_name", None):
             for name in p.private_party_name.split(','):
                  unique_contractors.add(name.strip())

        # Ministries Data
        p_ministries = []
        if getattr(p, "party_ministry_names", None):
             p_ministries.extend([m.strip() for m in p.party_ministry_names.split(',') if m.strip()])
        if getattr(p, "agency_ministry_names", None):
             p_ministries.extend([m.strip() for m in p.agency_ministry_names.split(',') if m.strip()])
        
        p_ministries = list(set(p_ministries)) # Unique per project

        for m_name in p_ministries:
             ministry_counts[m_name] = ministry_counts.get(m_name, 0) + 1
             ministry_investments[m_name] = ministry_investments.get(m_name, 0) + amt 
        
        # Determine Scale
        scale_key = "small"
        if amt > 5_000_000_000:
            scale_key = "big"
        elif amt > 1_000_000_000:
            scale_key = "medium"
        
        # Update Overall Project Scales
        project_scales[scale_key]["count"] += 1
        project_scales[scale_key]["investment"] += amt

        # Sectors Calculation
        if getattr(p, "sector_names", None):
            for s_name in p.sector_names.split(','):
                s_name = s_name.strip()
                if s_name not in sector_stats:
                    sector_stats[s_name] = {
                        "total": {"count": 0, "investment": 0},
                        "small": {"count": 0, "investment": 0},
                        "medium": {"count": 0, "investment": 0},
                        "big": {"count": 0, "investment": 0}
                    }
                
                # Update Total
                sector_stats[s_name]["total"]["count"] += 1
                sector_stats[s_name]["total"]["investment"] += amt
                
                # Update Specific Scale
                sector_stats[s_name][scale_key]["count"] += 1
                sector_stats[s_name][scale_key]["investment"] += amt

        # Investment by Year
        if hasattr(p, 'period_start_date') and p.period_start_date:
            year = p.period_start_date.year
            investment_by_year[year] = investment_by_year.get(year, 0) + amt

        # Latest Projects (Top 5)
        if idx < 5:
             latest_projects_data.append({
                 "id": str(p.id),
                 "title": p.title,
                 "ministry": p_ministries,
                 "public_authority": p.agency_name,
                 "budget": {"amount": {"amount": amt, "currency": "THB"}},
                 "status": "implementation",  # Placeholder or map from p.status
                 "type": "PPP", # Placeholder
                 "updated": datetime.utcnow().isoformat()
             })

    # Format Output Lists
    ministry_stats_list = [
        {"ministry": k, "projectCount": v, "totalInvestment": ministry_investments.get(k, 0), "rank": 0}
        for k, v in ministry_counts.items()
    ]
    # Sort by project count
    ministry_stats_list.sort(key=lambda x: x["projectCount"], reverse=True)
    for i, item in enumerate(ministry_stats_list):
        item["rank"] = i + 1

    ministry_investments_list = [
        {"ministry": k, "totalInvestment": v}
        for k, v in ministry_investments.items()
    ]
    ministry_investments_list.sort(key=lambda x: x["totalInvestment"], reverse=True)

    business_group_stats = [
        {
            "groupName": k, 
            "total": v["total"],
            "small": v["small"],
            "medium": v["medium"],
            "big": v["big"]
        }
        for k, v in sector_stats.items()
    ]
    
    investment_by_year_list = [
        {"year": k, "value": v} for k,v in sorted(investment_by_year.items())
    ]

    return {
        "summary": {
            "totalProjects": total_projects,
            "uniqueContractors": len(unique_contractors),
            "totalInvestment": total_investment,
            "maxBudget": max_budget
        },
        "ministryStats": ministry_stats_list,
        "latestProjects": latest_projects_data,
        "otherMinistries": {"projectCount": 0, "totalInvestment": 0}, # Can implement "Others" logic if list too long
        "ministryInvestments": ministry_investments_list,
        "otherMinistriesInvestment": {"totalInvestment": 0, "projectCount": 0},
        "projectScales": project_scales,
        "investmentByYear": investment_by_year_list,
        "businessGroupStats": business_group_stats,
        "sectorCounts": {k: v["total"]["count"] for k,v in sector_stats.items()},
        "projectScope": {"domestic": {"count": total_projects, "investment": total_investment}, "international": {"count": 0, "investment": 0}}
    }
