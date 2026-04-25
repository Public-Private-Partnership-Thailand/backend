"""
Reference Data Service — Business Logic

Fetches lookup / master data for dropdowns and filters.
"""

from typing import Any, Dict
from sqlmodel import Session

from oc4ids_datastore_api.repositories.reference_repository import ReferenceRepository


def get_reference_info(session: Session) -> Dict[str, Any]:
    """Fetch all reference/lookup data for dropdowns and filters."""
    dao = ReferenceRepository(session)

    sectors = dao.get_sectors()
    ministries = dao.get_ministries()
    project_types = dao.get_project_types()
    concession_forms = dao.get_concession_forms()
    contract_types = dao.get_contract_types()
    risk_categories = dao.get_risk_categories()
    risk_phase = dao.get_phase()
    risk_factors = dao.get_risk_factors()
    risk_sources = dao.get_risk_sources()

    return {
        "sector": [{"id": s.id, "value": s.code} for s in sectors],
        "ministry": [{"id": m.id, "value": m.name_th} for m in ministries],
        "projectType": [{"id": pt.id, "value": pt.name_th or pt.name_en or pt.code} for pt in project_types],
        "concessionForm": [{"id": cf.id, "value": cf.description or cf.code} for cf in concession_forms],
        "contractType": [{"id": ct.id, "value": ct.description or ct.code} for ct in contract_types],
        "riskCategory": [
            {
                "id": rc.risk_category_id,
                "code": rc.category_code,
                "value": rc.category_name,
                "description_en": rc.description_en,
                "description_th": rc.description_th,
            }
            for rc in risk_categories
        ],
        "riskPhase": [{"id": rp.phase_id, "value": rp.phase_name} for rp in risk_phase],
        "riskFactor": [
            {
                "id": rf.risk_factor_id,
                "value": rf.factor_name,
                "description_th": rf.description_th,
            }
            for rf in risk_factors
        ],
        "riskSource": {
            country: [
                {
                    "id": rs.rs_id,
                    "value": rs.meaning,
                    "reference": rs.reference,
                    "referenceFile": rs.reference_file,
                    "referenceFileUrl": f"/api/v1/risk-sources/{rs.rs_id}/reference" if rs.reference_file else None,
                    "referenceUrl": rs.reference_url,
                }
                for rs in risk_sources
                if rs.country == country
            ]
            for country in sorted({rs.country for rs in risk_sources if rs.country})
        }
        or {
            "global": [
                {"id": 1, "value": "GI hub"},
                {"id": 2, "value": "Yongjian Ke et al. (China)"},
                {"id": 3, "value": "Sy Tien Do (Vietnam)"},
                {"id": 4, "value": "Nur Alkaf Abd Karim (Malaysia)"},
            ],
            "thailand": [
                {"id": 1, "value": "SEPO"},
                {"id": 2, "value": "รายงาน สนข."},
            ],
        },
    }
