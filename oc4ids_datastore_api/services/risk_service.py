"""
Risk Analysis Service — Business Logic

Builds the risk heatmap and sector/ministry matrix from the DB.
"""

from collections import defaultdict
from typing import Any, Dict
from sqlmodel import Session, select
from sqlalchemy.orm import aliased
from sqlalchemy import func

from oc4ids_datastore_api.models import (
    RiskCategory, RiskFactor, RiskPhase, RiskPattern, RiskSource,
    Risk, RiskCategoryAssignment, RiskFactorAssignment,
    Sector, ProjectSectorLink, Project,
)


def get_risk_analysis(session: Session) -> Dict[str, Any]:
    """Build risk analysis data: heatmapRiskPhase + sectorMinistryHeatmap."""

    # ------------------------------------------------------------------ #
    # Load reference data
    # ------------------------------------------------------------------ #
    all_categories = session.exec(select(RiskCategory).order_by(RiskCategory.risk_category_id)).all()
    all_factors = session.exec(select(RiskFactor).order_by(RiskFactor.risk_factor_id)).all()
    all_phases = session.exec(select(RiskPhase).order_by(RiskPhase.phase_id)).all()
    all_sources = session.exec(select(RiskSource).order_by(RiskSource.rs_id)).all()
    all_patterns = session.exec(select(RiskPattern)).all()

    cat_code_map = {c.risk_category_id: c.category_code for c in all_categories}
    factor_name_map = {f.risk_factor_id: f.factor_name for f in all_factors}

    phase_bit_map = {p.phase_id_from_bit_mask: p.phase_name for p in all_phases if p.phase_id_from_bit_mask}
    source_bit_map = {s.rs_id_from_bit_mask: (s.rs_id, s.country) for s in all_sources if s.rs_id_from_bit_mask}

    # ------------------------------------------------------------------ #
    # Build heatmapRiskPhase (project-level OTP data)
    # ------------------------------------------------------------------ #
    RiskAlias = aliased(Risk)
    RCAlias = aliased(RiskCategoryAssignment)
    RFAlias = aliased(RiskFactorAssignment)

    otp_results = session.exec(
        select(
            RCAlias.risk_category_id,
            RFAlias.risk_factor_id,
            RiskAlias.project_id,
            Project.title,
        )
        .join(RCAlias, RiskAlias.risk_id == RCAlias.risk_id)
        .join(RFAlias, RiskAlias.risk_id == RFAlias.risk_id)
        .join(Project, RiskAlias.project_id == Project.id)
        .where(Project.deleted_at.is_(None))
    ).all()

    otp_map: dict = defaultdict(list)
    for cat_id, fac_id, p_id, p_title in otp_results:
        otp_map[(cat_id, fac_id)].append({"projectId": str(p_id), "title": p_title})

    heatmap: dict = {}
    for pattern in all_patterns:
        cat_code = cat_code_map.get(pattern.risk_category_id)
        fac_name = factor_name_map.get(pattern.risk_factor_id)
        if not cat_code or not fac_name:
            continue

        phase_list = [
            phase_name
            for bit_val, phase_name in sorted(phase_bit_map.items())
            if (pattern.phase or 0) & bit_val
        ]

        source_dict: dict = defaultdict(list)
        for bit_val, (rs_id, country) in sorted(source_bit_map.items()):
            if (pattern.source or 0) & bit_val and country:
                source_dict[country].append(rs_id)
        source_dict.setdefault("global", [])
        source_dict.setdefault("thailand", [])

        otp_data = otp_map.get((pattern.risk_category_id, pattern.risk_factor_id), [])
        if otp_data:
            source_dict["thailand-otp"] = otp_data

        if cat_code not in heatmap:
            heatmap[cat_code] = {}
        heatmap[cat_code][fac_name] = {"phase": phase_list, "source": dict(source_dict)}

    # ------------------------------------------------------------------ #
    # Build sectorMinistryHeatmap
    # ------------------------------------------------------------------ #
    all_active_sectors = session.exec(select(Sector).where(Sector.is_active == True)).all()
    sector_codes = [s.code for s in all_active_sectors]
    if "others" not in sector_codes:
        sector_codes.append("others")

    SectorAlias = aliased(Sector)
    RCAlias2 = aliased(RiskCategoryAssignment)
    RiskAlias2 = aliased(Risk)

    sector_risk_results = session.exec(
        select(
            SectorAlias.code.label("sector"),
            RCAlias2.risk_category_id,
            func.count(func.distinct(RiskAlias2.risk_id)).label("cnt"),
        )
        .join(RCAlias2, RiskAlias2.risk_id == RCAlias2.risk_id)
        .join(Project, RiskAlias2.project_id == Project.id)
        .join(ProjectSectorLink, Project.id == ProjectSectorLink.project_id)
        .join(SectorAlias, ProjectSectorLink.sector_id == SectorAlias.id)
        .where(Project.deleted_at.is_(None))
        .group_by(SectorAlias.code, RCAlias2.risk_category_id)
    ).all()

    sr_count = {(s_code, c_id): cnt for s_code, c_id, cnt in sector_risk_results}

    sector_ministry_heatmap = [
        {
            "sector": s_code,
            "ministryList": [
                {"id": cat.risk_category_id, "value": sr_count.get((s_code, cat.risk_category_id), 0)}
                for cat in all_categories
            ],
        }
        for s_code in sector_codes
    ]

    return {"heatmapRiskPhase": heatmap, "sectorMinistryHeatmap": sector_ministry_heatmap}
