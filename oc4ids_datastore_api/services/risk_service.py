"""
Risk Analysis Service — Business Logic

Builds the risk heatmap and sector/ministry matrix from the DB.
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional
from sqlmodel import Session, select
from sqlalchemy.orm import aliased
from sqlalchemy import func, exists

from oc4ids_datastore_api.models import (
    RiskCategory, RiskFactor, RiskPhase, RiskPattern, RiskSource,
    Risk, RiskCategoryAssignment, RiskFactorAssignment, CategoryFactorLink,
    Sector, ProjectSectorLink, Project, Mitigation, Impact,
)


def get_risk_analysis(session: Session, sector_ids: Optional[List[int]] = None) -> Dict[str, Any]:
    """Build risk analysis data: heatmapRiskPhase + sectorMinistryHeatmap + riskSectorWithProject."""

    # ------------------------------------------------------------------ #
    # Load reference data
    # ------------------------------------------------------------------ #
    all_categories = session.exec(select(RiskCategory).order_by(RiskCategory.risk_category_id)).all()
    all_factors = session.exec(select(RiskFactor).order_by(RiskFactor.risk_factor_id)).all()
    all_phases = session.exec(select(RiskPhase).order_by(RiskPhase.phase_id)).all()
    all_sources = session.exec(select(RiskSource).order_by(RiskSource.rs_id)).all()
    all_patterns = session.exec(select(RiskPattern)).all()

    category_id_set = {c.risk_category_id for c in all_categories}
    factor_id_set = {f.risk_factor_id for f in all_factors}

    phase_bit_map = {p.phase_id_from_bit_mask: p.phase_name for p in all_phases if p.phase_id_from_bit_mask}
    source_bit_map = {s.rs_id_from_bit_mask: (s.rs_id, s.country) for s in all_sources if s.rs_id_from_bit_mask}

    # ------------------------------------------------------------------ #
    # Build heatmapRiskPhase (project-level OTP data)
    # ------------------------------------------------------------------ #
    RiskAlias = aliased(Risk)
    RCAlias = aliased(RiskCategoryAssignment)
    RFAlias = aliased(RiskFactorAssignment)

    otp_stmt = (
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
    )

    if sector_ids:
        otp_stmt = otp_stmt.join(ProjectSectorLink, Project.id == ProjectSectorLink.project_id).where(
            ProjectSectorLink.sector_id.in_(sector_ids)
        )

    otp_results = session.exec(otp_stmt).all()

    otp_map: dict = defaultdict(list)
    for cat_id, fac_id, p_id, p_title in otp_results:
        otp_map[(cat_id, fac_id)].append({"projectId": str(p_id), "title": p_title})

    heatmap: dict = {}
    for pattern in all_patterns:
        if pattern.risk_category_id not in category_id_set or pattern.risk_factor_id not in factor_id_set:
            continue

        cat_key = f"C{pattern.risk_category_id}"
        fac_key = f"F{pattern.risk_factor_id}"

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

        if cat_key not in heatmap:
            heatmap[cat_key] = {}
        heatmap[cat_key][fac_key] = {"phase": phase_list, "source": dict(source_dict)}

    # ------------------------------------------------------------------ #
    # Build sectorMinistryHeatmap
    # ------------------------------------------------------------------ #
    ChildSector = aliased(Sector)
    has_children = exists().where(ChildSector.code.like(Sector.code + ".%"))
    sector_stmt = select(Sector).where(Sector.is_active == True, ~has_children)
    if sector_ids:
        sector_stmt = sector_stmt.where(Sector.id.in_(sector_ids))
    all_active_sectors = session.exec(sector_stmt).all()
    
    sector_codes = [s.code for s in all_active_sectors]
    if not sector_ids and "others" not in sector_codes:
        sector_codes.append("others")

    SectorAlias = aliased(Sector)
    RCAlias2 = aliased(RiskCategoryAssignment)
    RiskAlias2 = aliased(Risk)

    sector_risk_stmt = (
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
    )

    if sector_ids:
        sector_risk_stmt = sector_risk_stmt.where(SectorAlias.id.in_(sector_ids))

    sector_risk_stmt = sector_risk_stmt.group_by(SectorAlias.code, RCAlias2.risk_category_id)
    sector_risk_results = session.exec(sector_risk_stmt).all()

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

    # ------------------------------------------------------------------ #
    # Build riskSectorWithProject
    # ------------------------------------------------------------------ #

    # Query 1: one row per (sector, project, risk) — no category/factor join to avoid cartesian product.
    # func.min picks one representative impact/mitigation per risk.
    RCAlias3 = aliased(RiskCategoryAssignment)
    RFAlias3 = aliased(RiskFactorAssignment)
    ImpactAlias = aliased(Impact)
    MitigationAlias = aliased(Mitigation)

    risk_project_stmt = (
        select(
            SectorAlias.code.label("sector"),
            Project.id.label("projectId"),
            Project.title.label("projectName"),
            Risk.risk_id.label("risk_id"),
            Risk.title.label("problem"),
            Risk.phase.label("phase"),
            func.min(ImpactAlias.description).label("riskImpact"),
            func.min(MitigationAlias.action).label("riskResponse"),
        )
        .select_from(Project)
        .join(ProjectSectorLink, Project.id == ProjectSectorLink.project_id)
        .join(SectorAlias, ProjectSectorLink.sector_id == SectorAlias.id)
        .join(Risk, Project.id == Risk.project_id)
        .outerjoin(ImpactAlias, (Risk.risk_id == ImpactAlias.risk_id) & (ImpactAlias.kind == "description"))
        .outerjoin(MitigationAlias, Risk.risk_id == MitigationAlias.risk_id)
        .where(Project.deleted_at.is_(None))
        .group_by(SectorAlias.code, Project.id, Project.title, Risk.risk_id, Risk.title, Risk.phase)
    )

    if sector_ids:
        risk_project_stmt = risk_project_stmt.where(SectorAlias.id.in_(sector_ids))

    risk_project_results = session.exec(risk_project_stmt).all()

    # Query 2: for each risk, get category→[factors] using CategoryFactorLink
    # to ensure factors are correctly paired with their category.
    cat_factor_stmt = (
        select(
            RCAlias3.risk_id,
            RCAlias3.risk_category_id,
            RFAlias3.risk_factor_id,
        )
        .join(RFAlias3, RFAlias3.risk_id == RCAlias3.risk_id)
        .join(
            CategoryFactorLink,
            (CategoryFactorLink.risk_category_id == RCAlias3.risk_category_id) &
            (CategoryFactorLink.risk_factor_id == RFAlias3.risk_factor_id),
        )
    )
    cat_factor_results = session.exec(cat_factor_stmt).all()

    # Build: risk_id → {category_id: [factor_ids]}
    risk_cat_factors: dict = defaultdict(lambda: defaultdict(list))
    for r_id, cat_id, fac_id in cat_factor_results:
        if fac_id not in risk_cat_factors[r_id][cat_id]:
            risk_cat_factors[r_id][cat_id].append(fac_id)

    sector_grouped_projects: dict = defaultdict(list)

    for row in risk_project_results:
        s_code = row.sector
        risks_nested = [
            {"riskCategoryId": cat_id, "riskFactorId": fac_ids}
            for cat_id, fac_ids in risk_cat_factors.get(row.risk_id, {}).items()
        ]
        sector_grouped_projects[s_code].append({
            "projectId": str(row.projectId),
            "projectName": row.projectName,
            "problem": row.problem,
            "riskImpact": row.riskImpact,
            "riskResponse": row.riskResponse,
            "phase": row.phase,
            "risks": risks_nested,
        })
    
    # Calculate riskCount per sector
    sector_risk_count_stmt = (
        select(
            SectorAlias.code,
            func.count(func.distinct(Risk.risk_id))
        )
        .select_from(Project)
        .join(ProjectSectorLink, Project.id == ProjectSectorLink.project_id)
        .join(SectorAlias, ProjectSectorLink.sector_id == SectorAlias.id)
        .join(Risk, Project.id == Risk.project_id)
        .where(Project.deleted_at.is_(None))
    )
    if sector_ids:
        sector_risk_count_stmt = sector_risk_count_stmt.where(SectorAlias.id.in_(sector_ids))
    
    sector_risk_count_stmt = sector_risk_count_stmt.group_by(SectorAlias.code)
    sector_risk_count_results = session.exec(sector_risk_count_stmt).all()
    sector_risk_count = {row[0]: row[1] for row in sector_risk_count_results}

    risk_sector_with_project = [
        {
            "sector": s_code,
            "riskCount": sector_risk_count.get(s_code, 0),
            "projects": sector_grouped_projects.get(s_code, []),
        }
        for s_code in sector_codes
    ]

    return {
        "heatmapRiskPhase": heatmap,
        "sectorMinistryHeatmap": sector_ministry_heatmap,
        "riskSectorWithProject": risk_sector_with_project,
    }
