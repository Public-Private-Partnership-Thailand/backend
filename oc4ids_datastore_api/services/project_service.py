"""
Project Service — Business Logic

All write/read operations involving the Project aggregate:
create, update, delete, list, get by ID, compare.
"""

from typing import Any, Dict, List, Optional
import uuid
import logging
import json
from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session, select

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
    ProjectFinance, PartyRole, PartyPerson, PartyBeneficialOwner,
    BeneficialOwnerNationality, PartyClassification,
    ContractingTender, ContractingTenderTenderer, ContractingTenderEntity,
    ContractingTenderSustainability, ContractingSupplier, ContractingSocial,
    ContractingRelease, LocationGazetteer, LocationGazetteerIdentifier,
    ProjectPolicyAlignment, ProjectPolicyAlignmentPolicy, ProjectAssetLifetime,
    Risk, Mitigation, Impact, RiskCategory, RiskFactor,
    RiskCategoryAssignment, RiskFactorAssignment,
)
from oc4ids_datastore_api.repositories.project_repository import ProjectRepository

logger = logging.getLogger(__name__)


# ===========================================================================
# Helpers (private)
# ===========================================================================

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
        return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _get_or_create_ref(session: Session, model, code_field: str, code_value: str, defaults: Dict = None):
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


# ---------------------------------------------------------------------------
# Sub-object helpers
# ---------------------------------------------------------------------------

def _create_breakdown_item(session: Session, breakdown_id: int, item_data: Dict):
    amt = item_data.get("amount", {})
    val_amount = amt.get("amount") if isinstance(amt, dict) else amt
    val_currency = amt.get("currency") if isinstance(amt, dict) else None
    period = item_data.get("period", {})
    source = item_data.get("sourceParty", {})
    session.add(BudgetBreakdownItem(
        breakdown_id=breakdown_id,
        local_id=item_data.get("id", str(uuid.uuid4())),
        description=item_data.get("description"),
        amount=val_amount,
        currency=val_currency,
        period_start_date=_parse_date(period.get("startDate")),
        period_end_date=_parse_date(period.get("endDate")),
        source_party_id=source.get("id"),
        source_party_name=source.get("name"),
    ))


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
                category=cg_data.get("description"),
            )
            session.add(cg_obj)
            session.flush()
            for item_data in cg_data.get("breakdown", []):
                amt_data = item_data.get("amount", {})
                session.add(CostItem(
                    cost_group_id=cg_obj.id,
                    local_id=item_data.get("id", str(uuid.uuid4())),
                    classification_description=item_data.get("description"),
                    amount=amt_data.get("amount"),
                    currency=amt_data.get("currency"),
                ))


def _create_forecasts(session: Session, project_id: uuid.UUID, data_list: List[Dict]):
    for f in data_list:
        f_obj = ProjectForecast(
            project_id=project_id,
            local_id=f.get("id", str(uuid.uuid4())),
            title=f.get("title"),
            description=f.get("description"),
        )
        session.add(f_obj)
        session.flush()
        for obs_data in f.get("observations", []):
            val_data = obs_data.get("value", {})
            unit_data = obs_data.get("unit", {})
            period_data = obs_data.get("period", {})
            session.add(ForecastObservation(
                forecast_id=f_obj.id,
                local_id=obs_data.get("id", str(uuid.uuid4())),
                measure=obs_data.get("measure"),
                value_amount=val_data.get("amount"),
                value_currency=val_data.get("currency"),
                unit_name=unit_data.get("name"),
                unit_scheme=unit_data.get("scheme"),
                unit_id=unit_data.get("id"),
                period_start_date=_parse_date(period_data.get("startDate")),
                period_end_date=_parse_date(period_data.get("endDate")),
            ))


def _create_metrics(session: Session, project_id: uuid.UUID, data_list: List[Dict]):
    for m in data_list:
        m_obj = ProjectMetric(
            project_id=project_id,
            local_id=m.get("id", str(uuid.uuid4())),
            title=m.get("title"),
            description=m.get("description"),
        )
        session.add(m_obj)
        session.flush()
        for obs_data in m.get("observations", []):
            val_data = obs_data.get("value") or {}
            unit_data = obs_data.get("unit") or {}
            session.add(MetricObservation(
                metric_id=m_obj.id,
                local_id=obs_data.get("id", str(uuid.uuid4())),
                measure=obs_data.get("measure"),
                value_amount=val_data.get("amount"),
                value_currency=val_data.get("currency"),
                unit_name=unit_data.get("name"),
            ))


def _create_social(session: Session, project_id: uuid.UUID, data: Dict):
    comp_data = data.get("landCompensationBudget", {}) or data.get("landCompensation", {})
    social_obj = ProjectSocial(
        project_id=project_id,
        in_indigenous_land=data.get("inIndigenousLand"),
        land_compensation_amount=comp_data.get("amount"),
        land_compensation_currency=comp_data.get("currency"),
        health_safety_material_test_description=data.get("healthAndSafety", {}).get("materialTests", {}).get("description"),
    )
    session.add(social_obj)
    session.flush()
    hs_data = data.get("healthAndSafety", {})
    for test in hs_data.get("materialTests", {}).get("tests", []):
        session.add(SocialHealthSafetyMaterialTest(project_id=project_id, test=test))
    for mtg in data.get("consultationMeetings", []):
        addr = mtg.get("address", {})
        po = mtg.get("publicOffice", {})
        org = po.get("organization", {})
        session.add(SocialConsultationMeeting(
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
            job_title=po.get("jobTitle"),
        ))


def _create_environment(session: Session, project_id: uuid.UUID, data: Dict):
    abatement_cost = data.get("abatementCost", {})
    env_obj = ProjectEnvironment(
        project_id=project_id,
        has_impact_assessment=data.get("hasImpactAssessment"),
        in_protected_area=data.get("inProtectedArea"),
        abatement_cost_amount=abatement_cost.get("amount"),
        abatement_cost_currency=abatement_cost.get("currency"),
    )
    session.add(env_obj)
    session.flush()
    for g in data.get("goals", []):
        session.add(EnvironmentGoal(project_id=project_id, goal=g))
    for c in data.get("climateOversightTypes", []):
        session.add(EnvironmentClimateOversightType(project_id=project_id, oversight_type=c))
    for cm in data.get("conservationMeasures", []):
        session.add(EnvironmentConservationMeasure(project_id=project_id, type=cm.get("type"), description=cm.get("description")))
    for em in data.get("environmentalMeasures", []):
        session.add(EnvironmentEnvironmentalMeasure(project_id=project_id, type=em.get("type"), description=em.get("description")))
    for cm in data.get("climateMeasures", []):
        c_types = cm.get("type", [])
        c_type_str = ", ".join(c_types) if isinstance(c_types, list) else c_types
        session.add(EnvironmentClimateMeasure(project_id=project_id, type=c_type_str, description=cm.get("description")))
    for ic in data.get("impactCategories", []):
        session.add(EnvironmentImpactCategory(project_id=project_id, category_scheme=ic.get("scheme"), category_id=ic.get("id")))


def _create_benefits(session: Session, project_id: uuid.UUID, data_list: List[Dict]):
    for b in data_list:
        b_obj = ProjectBenefit(project_id=project_id, title=b.get("title"), description=b.get("description"))
        session.add(b_obj)
        session.flush()
        for ben in b.get("beneficiaries", []):
            session.add(BenefitBeneficiary(
                benefit_id=b_obj.id,
                description=ben.get("description"),
                number_of_people=ben.get("numberOfPeople"),
            ))


def _create_completion(session: Session, project_id: uuid.UUID, data: Dict):
    val_data = data.get("finalValue", {})
    session.add(ProjectCompletion(
        project_id=project_id,
        end_date=_parse_date(data.get("endDate")),
        final_scope=data.get("finalScope"),
        final_value_amount=val_data.get("amount"),
        final_value_currency=val_data.get("currency"),
    ))


def _create_lobbying(session: Session, project_id: uuid.UUID, meetings: List[Dict]):
    for m in meetings:
        addr = m.get("address", {})
        po = m.get("publicOffice", {})
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
            public_office_person_name=po.get("name"),
            public_office_org_name=po.get("organization", {}).get("name"),
            public_office_org_id=po.get("organization", {}).get("id"),
        ))


def _create_policy(session: Session, project_id: uuid.UUID, policy_data):
    if isinstance(policy_data, dict):
        pa = ProjectPolicyAlignment(project_id=project_id, description=policy_data.get("description"))
        session.add(pa)
        session.flush()
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
        period_duration_days=lifetime_data.get("durationInDays"),
    ))


def _create_party_details(session: Session, party_id: int, party_data: Dict):
    for role in party_data.get("roles", []):
        session.add(PartyRole(party_id=party_id, role=role))
    for p in party_data.get("persons", []):
        session.add(PartyPerson(
            party_id=party_id,
            local_id=p.get("id", str(uuid.uuid4())),
            name=p.get("name"),
            job_title=p.get("jobTitle"),
        ))
    for bo in party_data.get("beneficialOwners", []):
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
            country_name=bo.get("address", {}).get("countryName"),
        )
        session.add(bo_obj)
        session.flush()
        for nat in bo.get("nationalities", []):
            session.add(BeneficialOwnerNationality(owner_id=bo_obj.id, nationality=nat))
    for c in party_data.get("classifications", []):
        session.add(PartyClassification(
            party_id=party_id,
            scheme=c.get("scheme"),
            classification_id=c.get("id"),
        ))


def _create_contracting_tenders(session: Session, process_id: int, summary_data: Dict):
    t_data = summary_data.get("tender", {})
    if t_data:
        tender = ContractingTender(
            process_id=process_id,
            procurement_method=t_data.get("procurementMethod"),
            procurement_method_details=t_data.get("procurementMethodDetails"),
            date_published=_parse_date(t_data.get("datePublished")),
            cost_estimate_amount=t_data.get("value", {}).get("amount"),
            cost_estimate_currency=t_data.get("value", {}).get("currency"),
            number_of_tenderers=t_data.get("numberOfTenderers"),
        )
        session.add(tender)
        for tenderer in t_data.get("tenderers", []):
            session.add(ContractingTenderTenderer(
                process_id=process_id,
                local_id=tenderer.get("id", str(uuid.uuid4())),
                name=tenderer.get("name"),
            ))
        if "procuringEntity" in t_data and isinstance(t_data["procuringEntity"], dict):
            ent = t_data["procuringEntity"]
            session.add(ContractingTenderEntity(process_id=process_id, role="procuringEntity", name=ent.get("name")))
        for s in t_data.get("sustainability", []):
            session.add(ContractingTenderSustainability(
                process_id=process_id,
                strategies=s if isinstance(s, list) else [s],
            ))
    for supp in summary_data.get("suppliers", []):
        session.add(ContractingSupplier(
            process_id=process_id,
            local_id=supp.get("id", str(uuid.uuid4())),
            name=supp.get("name"),
        ))


def _create_contracting_details(session: Session, process_id: int, summary_data: Dict):
    if "social" in summary_data:
        soc = summary_data["social"]
        lb = soc.get("laborBudget", {})
        session.add(ContractingSocial(
            process_id=process_id,
            labor_budget_amount=lb.get("amount"),
            labor_budget_currency=lb.get("currency"),
            labor_obligations=soc.get("laborObligations"),
            labor_description=soc.get("description"),
        ))
    for rel in summary_data.get("releases", []):
        session.add(ContractingRelease(
            process_id=process_id,
            local_id=rel.get("id", str(uuid.uuid4())),
            tag=rel.get("tag"),
            date=_parse_date(rel.get("date")),
            url=rel.get("url"),
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
            value_currency=val.get("currency"),
            source=fin.get("source"),
            financing_party_id=fin.get("financingParty", {}).get("id"),
            financing_party_name=fin.get("financingParty", {}).get("name"),
            period_start_date=_parse_date(fin.get("period", {}).get("startDate")),
            period_end_date=_parse_date(fin.get("period", {}).get("endDate")),
            payment_period_start_date=_parse_date(fin.get("paymentPeriod", {}).get("startDate")),
            payment_period_end_date=_parse_date(fin.get("paymentPeriod", {}).get("endDate")),
            interest_rate_margin=fin.get("interestRateMargin"),
            description=fin.get("description"),
        ))


def _create_location_gazetteers(session: Session, location_id: uuid.UUID, gazetteers: List[Dict]):
    for gaz in gazetteers:
        g_obj = LocationGazetteer(location_id=location_id, scheme=gaz.get("scheme"))
        session.add(g_obj)
        session.flush()
        for ident in gaz.get("identifiers", []):
            if isinstance(ident, str):
                session.add(LocationGazetteerIdentifier(gazetteer_id=g_obj.id, identifier=ident))


def _create_risks(session: Session, project_id: uuid.UUID, risks_list: List[Dict]):
    for r_data in risks_list:
        risk_obj = Risk(project_id=project_id, title=r_data.get("title"), phase=r_data.get("phase"))
        session.add(risk_obj)
        session.flush()

        for cd in r_data.get("category_drivers", []):
            cat_code = cd.get("risk_category_id") or cd.get("risk_category_code")
            rc_obj = None
            if cat_code:
                rc_obj = session.exec(select(RiskCategory).where(RiskCategory.category_code == cat_code)).first()
                if not rc_obj:
                    alt_code = cd.get("risk_category_code") or cd.get("risk_category_id")
                    if alt_code and alt_code != cat_code:
                        rc_obj = session.exec(select(RiskCategory).where(RiskCategory.category_code == alt_code)).first()
            if rc_obj:
                existing = session.exec(
                    select(RiskCategoryAssignment).where(
                        RiskCategoryAssignment.risk_id == risk_obj.risk_id,
                        RiskCategoryAssignment.risk_category_id == rc_obj.risk_category_id,
                    )
                ).first()
                if not existing:
                    session.add(RiskCategoryAssignment(risk_id=risk_obj.risk_id, risk_category_id=rc_obj.risk_category_id))
            else:
                logger.warning(f"RiskCategory '{cat_code}' not found. Skipping.")

            for rf_data in cd.get("driven_by_risk_factors", []):
                factor_name = rf_data.get("factor_name")
                rf_obj = None
                if factor_name:
                    rf_obj = session.exec(select(RiskFactor).where(RiskFactor.factor_name == factor_name)).first()
                if rf_obj:
                    existing_rfa = session.exec(
                        select(RiskFactorAssignment).where(
                            RiskFactorAssignment.risk_id == risk_obj.risk_id,
                            RiskFactorAssignment.risk_factor_id == rf_obj.risk_factor_id,
                        )
                    ).first()
                    if not existing_rfa:
                        session.add(RiskFactorAssignment(risk_id=risk_obj.risk_id, risk_factor_id=rf_obj.risk_factor_id))
                else:
                    logger.warning(f"RiskFactor '{factor_name}' not found. Skipping.")

        for mit in r_data.get("mitigation_handling", []):
            if isinstance(mit, dict):
                action, status = mit.get("action"), mit.get("status")
            else:
                action, status = str(mit), None
            session.add(Mitigation(risk_id=risk_obj.risk_id, action=action, status=status))

        desc_raw = r_data.get("description", [])
        if isinstance(desc_raw, list):
            for t in desc_raw:
                session.add(Impact(risk_id=risk_obj.risk_id, description=str(t), kind="description"))
        elif desc_raw:
            session.add(Impact(risk_id=risk_obj.risk_id, description=str(desc_raw), kind="description"))

        impact_raw = r_data.get("impact_statement", [])
        if isinstance(impact_raw, list):
            for t in impact_raw:
                session.add(Impact(risk_id=risk_obj.risk_id, description=str(t), kind="impact"))
        elif impact_raw:
            session.add(Impact(risk_id=risk_obj.risk_id, description=str(impact_raw), kind="impact"))


# ---------------------------------------------------------------------------
# Top-level section creators (used by create_project_data)
# ---------------------------------------------------------------------------

_PERIOD_KEY_MAP = {
    "period": "duration",
    "identificationPeriod": "identification",
    "preparationPeriod": "preparation",
    "implementationPeriod": "implementation",
    "completionPeriod": "completion",
    "maintenancePeriod": "maintenance",
    "decommissioningPeriod": "decommissioning",
    "assetLifetime": "assetLifetime",
}


def _create_sectors(session: Session, project: Project, sector_list: List) -> None:
    for s_data in sector_list:
        s_code = s_data.get("id") if isinstance(s_data, dict) else s_data
        if not s_code:
            continue
        sector_obj = session.exec(select(Sector).where(Sector.code == s_code)).first()
        if not sector_obj:
            logger.warning(f"Sector '{s_code}' not found. Skipping.")
            continue
        project.sectors.append(sector_obj)


def _create_additional_classifications(session: Session, project: Project, ac_list: List[Dict]) -> None:
    for ac in ac_list:
        scheme = ac.get("scheme")
        if not scheme:
            continue

        ac_obj = None
        raw_id = ac.get("id")

        # 1. Numeric id → look up by DB primary key (reference endpoint sends id as int)
        if isinstance(raw_id, int):
            ac_obj = session.get(AdditionalClassification, raw_id)
            if ac_obj and ac_obj.scheme != scheme:
                ac_obj = None  # wrong scheme, ignore

        # 2. String id/code → look up by code
        if not ac_obj:
            code = (str(raw_id) if raw_id and not isinstance(raw_id, int) else None) or ac.get("code")
            if code:
                ac_obj = session.exec(
                    select(AdditionalClassification).where(
                        AdditionalClassification.scheme == scheme,
                        AdditionalClassification.code == code,
                    )
                ).first()

        # 3. Fallback: look up by description
        if not ac_obj:
            desc = ac.get("description")
            if desc:
                ac_obj = session.exec(
                    select(AdditionalClassification).where(
                        AdditionalClassification.scheme == scheme,
                        AdditionalClassification.description == desc,
                    )
                ).first()

        # 3.5. description value might be the code (e.g. data.json stores "BTO" in description
        #      while the DB record has code="BTO", description="Build-Transfer-Operate (BTO)")
        if not ac_obj:
            desc_as_code = ac.get("description")
            if desc_as_code:
                ac_obj = session.exec(
                    select(AdditionalClassification).where(
                        AdditionalClassification.scheme == scheme,
                        AdditionalClassification.code == desc_as_code,
                    )
                ).first()

        # 4. Create only when an explicit string code is provided (never create from numeric id)
        if not ac_obj:
            code = ac.get("code") or (str(raw_id) if raw_id and not isinstance(raw_id, int) else None) or ac.get("description")
            if not code:
                continue
            ac_obj = AdditionalClassification(
                scheme=scheme,
                code=code,
                description=ac.get("description"),
            )
            session.add(ac_obj)
            session.flush()
            session.refresh(ac_obj)
        else:
            if ac.get("description") and ac_obj.description != ac.get("description"):
                ac_obj.description = ac.get("description")
                session.add(ac_obj)

        if ac_obj not in project.additional_classifications:
            project.additional_classifications.append(ac_obj)


def _create_locations(session: Session, project_id: uuid.UUID, locations: List[Dict]) -> None:
    for loc in locations:
        l_obj = ProjectLocation(
            project_id=project_id,
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


def _create_documents(session: Session, project_id: uuid.UUID, documents: List[Dict]) -> None:
    for doc in documents:
        session.add(ProjectDocument(
            project_id=project_id,
            local_id=doc.get("id", str(uuid.uuid4())),
            document_type=doc.get("documentType"),
            title=doc.get("title"),
            description=doc.get("description"),
            url=doc.get("url"),
            date_published=_parse_date(doc.get("datePublished")),
            date_modified=_parse_date(doc.get("dateModified")),
            format=doc.get("format"),
            author=doc.get("author"),
        ))


def _create_budget(session: Session, project_id: uuid.UUID, b_data: Dict) -> None:
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
        project_id=project_id,
        description=b_data.get("description"),
        total_amount=amt_val,
        currency=curr_code,
        request_date=_parse_date(b_data.get("requestDate")),
        approval_date=_parse_date(b_data.get("approvalDate")),
    )
    session.add(b_obj)
    session.flush()
    for group in b_data.get("budgetBreakdowns", []):
        group_obj = BudgetBreakdown(
            budget_id=b_obj.id,
            local_id=group.get("id", str(uuid.uuid4())),
            description=group.get("description"),
        )
        session.add(group_obj)
        session.flush()
        for item_data in group.get("budgetBreakdown", []):
            _create_breakdown_item(session, group_obj.id, item_data)
    if "finance" in b_data:
        _create_project_finance(session, b_obj.id, b_data["finance"])


def _create_periods(session: Session, project_id: uuid.UUID, project_data: Dict) -> None:
    for p_key, p_type in _PERIOD_KEY_MAP.items():
        if p_key in project_data and isinstance(project_data[p_key], dict):
            per = project_data[p_key]
            _get_or_create_ref(session, PeriodType, "code", p_type, {"name_en": p_type.capitalize() + " Period"})
            session.add(ProjectPeriod(
                project_id=project_id,
                period_type=p_type,
                start_date=_parse_date(per.get("startDate")),
                end_date=_parse_date(per.get("endDate")),
                duration_days=per.get("durationInDays"),
                max_extent_date=_parse_date(per.get("maxExtentDate")),
            ))


def _create_identifiers_list(session: Session, project_id: uuid.UUID, identifiers: List[Dict]) -> None:
    for ident in identifiers:
        session.add(ProjectIdentifier(
            project_id=project_id,
            identifier_value=ident.get("id"),
            scheme=ident.get("scheme"),
        ))


def _create_related_projects(session: Session, project_id: uuid.UUID, rp_list: List[Dict]) -> None:
    for rp in rp_list:
        rels = rp.get("relationship")
        rel_str = "related"
        if isinstance(rels, list) and rels:
            rel_str = rels[0]
        elif isinstance(rels, str):
            rel_str = rels
        rp_identifier = rp.get("identifier")
        resolved_project_id = None
        if rp_identifier:
            pi_obj = session.exec(
                select(ProjectIdentifier).where(ProjectIdentifier.identifier_value == rp_identifier)
            ).first()
            if pi_obj:
                resolved_project_id = pi_obj.project_id
        session.add(ProjectRelatedProject(
            project_id=project_id,
            related_project_id=resolved_project_id,
            scheme=rp.get("scheme"),
            identifier=rp_identifier or rp.get("id", ""),
            relationship=rel_str,
            title=rp.get("title"),
            uri=rp.get("uri"),
        ))


def _create_parties(session: Session, project_id: uuid.UUID, parties: List[Dict]) -> None:
    for party in parties:
        legal_name = party.get("identifier", {}).get("legalName")
        agency_id = None
        if legal_name:
            ministry = session.exec(select(Ministry).where(Ministry.name_th == legal_name)).first()
            agency_defaults = {"name_en": legal_name}
            if ministry:
                agency_defaults["ministry_id"] = ministry.id
            agency_obj = _get_or_create_ref(session, Agency, "name_th", legal_name, agency_defaults)
            if ministry and agency_obj.ministry_id != ministry.id:
                agency_obj.ministry_id = ministry.id
                session.add(agency_obj)
                session.flush()
            agency_id = agency_obj.id
        p_obj = ProjectParty(
            project_id=project_id,
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
            role=party.get("role"),
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
                session.add(PartyAdditionalIdentifier(
                    party_id=p_obj.id,
                    scheme=ai.get("scheme"),
                    identifier=ai.get("id"),
                    legal_name_id=ai_ministry_id,
                    uri=ai.get("uri"),
                ))
        _create_party_details(session, p_obj.id, party)


def _create_contracting_processes(session: Session, project_id: uuid.UUID, cp_list: List[Dict]) -> None:
    for cp in cp_list:
        summary = cp.get("summary", {})
        c_curr = summary.get("contractValue", {}).get("currency")
        _ensure_currency(session, c_curr)
        cp_obj = ProjectContractingProcess(
            project_id=project_id,
            local_id=cp.get("id", str(uuid.uuid4())),
            ocid=summary.get("ocid"),
            title=summary.get("title"),
            description=summary.get("description"),
            status=summary.get("status"),
            nature=summary.get("nature"),
            contract_amount=summary.get("contractValue", {}).get("amount"),
            contract_currency=c_curr,
            period_start_date=_parse_date(summary.get("contractPeriod", {}).get("startDate")),
            period_end_date=_parse_date(summary.get("contractPeriod", {}).get("endDate")),
            period_duration_days=summary.get("contractPeriod", {}).get("durationInDays"),
        )
        session.add(cp_obj)
        session.flush()
        for m in summary.get("milestones", []):
            val = m.get("value", {})
            session.add(ContractingProcessMilestone(
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
                value_currency=val.get("currency"),
            ))
        for t in summary.get("transactions", []):
            val = t.get("value", {})
            session.add(ContractingProcessTransaction(
                process_id=cp_obj.id,
                local_id=t.get("id", str(uuid.uuid4())),
                source=t.get("source"),
                date=_parse_date(t.get("date")),
                amount=val.get("amount"),
                currency=val.get("currency"),
                payer_name=t.get("payer", {}).get("name"),
                payee_name=t.get("payee", {}).get("name"),
                uri=t.get("uri"),
            ))
        for mod in summary.get("modifications", []):
            cv = mod.get("contractValue", {})
            orig = cv.get("originalAmount", {})
            new_val = cv.get("amount", {})
            session.add(ContractingProcessModification(
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
                new_currency=new_val.get("currency"),
            ))
        for d in summary.get("documents", []):
            session.add(ContractingProcessDocument(
                process_id=cp_obj.id,
                local_id=d.get("id", str(uuid.uuid4())),
                document_type=d.get("documentType"),
                title=d.get("title"),
                description=d.get("description"),
                url=d.get("url"),
                date_published=_parse_date(d.get("datePublished")),
                format=d.get("format"),
                language=d.get("language"),
            ))
        _create_contracting_tenders(session, cp_obj.id, summary)
        _create_contracting_details(session, cp_obj.id, summary)


# ===========================================================================
# Public Service Functions
# ===========================================================================

def get_all_projects(
    session: Session,
    page: int = 1,
    page_size: int = 20,
    title: Optional[str] = None,
    sector_id: Optional[List[int]] = None,
    ministry_id: Optional[List[int]] = None,
    concession_form_id: Optional[List[int]] = None,
    contract_type_id: Optional[List[int]] = None,
    risk_category_id: Optional[List[int]] = None,
    risk_factor_id: Optional[List[int]] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    sort_by: Optional[str] = "period",
) -> Dict[str, Any]:
    repo = ProjectRepository(session)
    skip = (page - 1) * page_size
    # map public param names to internal order_by values
    order_by = "start_date" if sort_by == "period" else sort_by
    results = repo.get_projects(
        skip=skip, limit=page_size, title=title,
        sector_id=sector_id, ministry_id=ministry_id,
        concession_form_id=concession_form_id, contract_type_id=contract_type_id,
        risk_category_id=risk_category_id, risk_factor_id=risk_factor_id,
        year_from=year_from, year_to=year_to,
        order_by=order_by,
    )
    total = repo.count_filtered(
        title=title, sector_id=sector_id, ministry_id=ministry_id,
        concession_form_id=concession_form_id, contract_type_id=contract_type_id,
        risk_category_id=risk_category_id, risk_factor_id=risk_factor_id,
        year_from=year_from, year_to=year_to,
    )
    data = []
    for row in results:
        ministries = set()
        if hasattr(row, "party_ministry_names") and row.party_ministry_names:
            ministries.update([m.strip() for m in row.party_ministry_names.split(",") if m.strip()])
        private_parties = []
        if getattr(row, "private_party_name", None):
            private_parties = [p.strip() for p in row.private_party_name.split(",") if p.strip()]
        
        data.append({
            "id": str(row.id),
            "title": row.title,
            "ministry": list(ministries),
            "public_authority": row.agency_name,
            "private_parties": private_parties,
            "sector": [s for s in row.sector_names if s] if getattr(row, "sector_names", None) else [],
            "concession": [c for c in row.concession_names if c] if getattr(row, "concession_names", None) else [],
            "start_date": row.start_date,
        })
    return {
        "data": data,
        "pagination": {
            "page": page,
            "pageSize": page_size,
            "total": total,
            "totalPages": (total + page_size - 1) // page_size,
        },
    }


def get_project_by_id(session: Session, project_id: str) -> Optional[Dict[str, Any]]:
    repo = ProjectRepository(session)
    project = repo.get_by_id(project_id)
    if not project:
        return None
    return project.to_oc4ids()


def get_projects_comparison(session: Session, project_ids: List[str]) -> List[Dict[str, Any]]:
    repo = ProjectRepository(session)
    projects = repo.get_by_ids(project_ids)
    return [p.to_oc4ids() for p in projects]


def create_project_data(
    project_data: Dict[str, Any],
    session: Session,
    auto_commit: bool = True,
) -> Dict[str, Any]:
    """Validates and stores project data."""
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
    logger.info(f"Skipping strict validation for project {project_id_str}")

    # Build core project (project_type + public_authority resolution)
    model_data = {k: project_data[k] for k in ["id", "title", "description", "status", "purpose"] if k in project_data}
    pt = _get_or_create_ref(session, ProjectType, "code", project_data["type"], {"name_en": project_data["type"]})
    model_data["project_type_id"] = pt.id

    if "publicAuthority" in project_data:
        pa_name = project_data["publicAuthority"].get("name")
        if pa_name:
            ministry = session.exec(select(Ministry).where(Ministry.name_th == pa_name)).first()
            agency_defaults = {"name_en": pa_name}
            if ministry:
                agency_defaults["ministry_id"] = ministry.id
            agency = _get_or_create_ref(session, Agency, "name_th", pa_name, agency_defaults)
            if ministry and agency.ministry_id != ministry.id:
                agency.ministry_id = ministry.id
                session.add(agency)
                session.flush()
            model_data["public_authority_id"] = agency.id

    db_project = Project(**model_data)
    session.add(db_project)
    session.flush()

    # Top-level OC4IDS identifier (from caller-supplied id)
    if input_id:
        session.add(ProjectIdentifier(project_id=db_project.id, identifier_value=str(input_id), scheme="OC4IDS"))

    # Children — order preserved from previous implementation
    _create_sectors(session, db_project, project_data.get("sector", []))
    _create_additional_classifications(session, db_project, project_data.get("additionalClassifications", []))
    _create_locations(session, db_project.id, project_data.get("locations", []))
    _create_documents(session, db_project.id, project_data.get("documents", []))
    if "budget" in project_data:
        _create_budget(session, db_project.id, project_data["budget"])
    _create_periods(session, db_project.id, project_data)
    _create_identifiers_list(session, db_project.id, project_data.get("identifiers", []))
    _create_related_projects(session, db_project.id, project_data.get("relatedProjects", []))

    # Optional sub-objects (already-extracted helpers)
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
    if "risks" in project_data and isinstance(project_data["risks"], list):
        _create_risks(session, db_project.id, project_data["risks"])

    _create_parties(session, db_project.id, project_data.get("parties", []))
    _create_contracting_processes(session, db_project.id, project_data.get("contractingProcesses", []))

    # Commit / flush
    if auto_commit:
        try:
            session.commit()
            logger.info(f"Successfully committed project {project_id_str}")
        except Exception as e:
            logger.error(f"Error committing project {project_id_str}: {e}")
            session.rollback()
            raise e
    else:
        session.flush()
        logger.info(f"Flushed project {project_id_str} (commit deferred)")

    session.refresh(db_project)
    return {"status": "success", "message": "Project created successfully", "project": {"id": str(db_project.id), "title": db_project.title}}


def update_project_data(project_id: str, project_data: Dict[str, Any], session: Session) -> Dict[str, Any]:
    """Updates an existing project by deleting and recreating it in a single transaction."""
    logger.info(f"Starting update for project {project_id}")
    repo = ProjectRepository(session)
    existing = repo.get_by_id(project_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    try:
        repo.delete(project_id, hard_delete=True, auto_commit=False)
        session.expire_all()
        project_data["id"] = project_id
        result = create_project_data(project_data, session, auto_commit=False)
        session.commit()
        logger.info(f"Successfully committed update for project {project_id}")
        return result
    except ValueError as e:
        session.rollback()
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating project {project_id}: {e}")
        session.rollback()
        raise


def delete_project_data(project_id: str, session: Session) -> Dict[str, Any]:
    repo = ProjectRepository(session)
    db_project = repo.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    repo.delete(project_id)
    return {"message": "Project deleted successfully"}
