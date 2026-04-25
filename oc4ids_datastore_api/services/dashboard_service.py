"""
Dashboard Service — Business Logic

Aggregates statistics from the Project repository for the dashboard.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlmodel import Session

from oc4ids_datastore_api.repositories.project_repository import ProjectRepository
from oc4ids_datastore_api.utils import format_thai_amount


def get_dashboard_summary(
    session: Session,
    sector_id: Optional[List[int]] = None,
    ministry_id: Optional[List[int]] = None,
    agency_id: Optional[List[int]] = None,
    concession_form_id: Optional[List[int]] = None,
    contract_type_id: Optional[List[int]] = None,
    risk_category_id: Optional[List[int]] = None,
    risk_factor_id: Optional[List[int]] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    search: Optional[str] = None,
) -> Dict[str, Any]:
    """Build the full dashboard summary payload."""
    dao = ProjectRepository(session)

    # 1. Get aggregated stats
    stats = dao.get_dashboard_stats(
        title=search,
        sector_id=sector_id,
        ministry_id=ministry_id,
        agency_id=agency_id,
        concession_form_id=concession_form_id,
        contract_type_id=contract_type_id,
        risk_category_id=risk_category_id,
        risk_factor_id=risk_factor_id,
        year_from=year_from,
        year_to=year_to,
    )

    # 2. Get latest projects (small limit)
    latest_projects_results = dao.get_summaries(
        limit=5,
        title=search,
        sector_id=sector_id,
        ministry_id=ministry_id,
        agency_id=agency_id,
        concession_form_id=concession_form_id,
        contract_type_id=contract_type_id,
        risk_category_id=risk_category_id,
        risk_factor_id=risk_factor_id,
        year_from=year_from,
        year_to=year_to,
    )

    # Map latest projects
    latest_projects_data = []
    for p in latest_projects_results:
        p_ministries = []
        pm_names = getattr(p, "party_ministry_names", None)
        if pm_names:
            if isinstance(pm_names, list):
                p_ministries.extend([m.strip() for m in pm_names if m.strip()])
            elif isinstance(pm_names, str):
                p_ministries.extend([m.strip() for m in pm_names.split(",") if m.strip()])
        am_names = getattr(p, "agency_ministry_names", None)
        if am_names:
            if isinstance(am_names, list):
                p_ministries.extend([m.strip() for m in am_names if m.strip()])
            elif isinstance(am_names, str):
                p_ministries.extend([m.strip() for m in am_names.split(",") if m.strip()])
        p_ministries = list(set(p_ministries))
        latest_projects_data.append({
            "id": str(p.id),
            "title": p.title,
            "ministry": p_ministries,
            "public_authority": p.agency_name,
            "budget": {"amount": getattr(p, "budget_amount", 0) or 0},
            "status": "implementation",
            "type": "PPP",
            "updated": datetime.utcnow().isoformat(),
        })

    # Build ministerial stats lists
    ministry_counts = stats["ministry_counts"]
    ministry_investments = stats["ministry_investments"]

    ministry_stats_list = [
        {"ministry": k, "projectCount": v, "totalInvestment": ministry_investments.get(k, 0), "rank": 0}
        for k, v in ministry_counts.items()
    ]
    ministry_stats_list.sort(key=lambda x: (x["projectCount"], x["totalInvestment"]), reverse=True)
    for i, item in enumerate(ministry_stats_list):
        item["rank"] = i + 1

    top_ministries = ministry_stats_list[:10]
    other_ministries_list = ministry_stats_list[10:]
    other_ministries = {
        "projectCount": sum(x["projectCount"] for x in other_ministries_list),
        "totalInvestment": sum(x["totalInvestment"] for x in other_ministries_list),
    }
    ministry_stats_list = top_ministries

    ministry_investments_list = [
        {"ministry": k, "totalInvestment": v, "projectCount": ministry_counts.get(k, 0), "rank": 0}
        for k, v in ministry_investments.items()
    ]
    ministry_investments_list.sort(key=lambda x: (x["totalInvestment"], x["projectCount"]), reverse=True)
    for i, item in enumerate(ministry_investments_list):
        item["rank"] = i + 1
    top_ministries_invest = ministry_investments_list[:10]
    other_ministries_invest_list = ministry_investments_list[10:]
    other_ministries_investment = {
        "totalInvestment": sum(x["totalInvestment"] for x in other_ministries_invest_list),
        "projectCount": sum(x["projectCount"] for x in other_ministries_invest_list),
    }
    ministry_investments_list = top_ministries_invest

    # Business group stats
    sector_stats = stats["sector_stats"]
    business_group_stats = [
        {
            "groupName": k,
            "displayName": k,
            "total": v["total"],
            "small": v["small"],
            "medium": v["medium"],
            "big": v["big"],
        }
        for k, v in sector_stats.items()
    ]

    investment_by_year_data = stats.get("investment_by_year", {})
    investment_by_year_list = [
        {"year": k, "investment": v["investment"], "projectCount": v["count"]}
        for k, v in investment_by_year_data.items()
    ]
    investment_by_year_list.sort(key=lambda x: x["year"])

    # pieContractTypeCount mapping
    pie_contract_counts = []
    for ct in stats.get("contract_type_counts", []):
        pie_contract_counts.append({
            "id": ct["id"],
            "name": ct["name"],
            "fullName": ct["fullName"],
            "count": ct["count"]
        })

    return {
        "summary": {
            "totalProjects": stats["total_projects"],
            "uniqueContractors": stats["unique_contractors"],
            "uniquePublicAuthority": stats.get("unique_public_authority", 0),
            "totalInvestment": format_thai_amount(stats["total_investment"]),
            "maxBudget": format_thai_amount(stats["max_budget"]),
            "inprogressProjects": stats["inprogress_projects"],
        },
        "ministryStats": ministry_stats_list,
        "latestProjects": latest_projects_data,
        "otherMinistries": other_ministries,
        "ministryInvestments": ministry_investments_list,
        "otherMinistriesInvestment": other_ministries_investment,
        "projectScales": stats["project_scales"],
        "investmentByYear": investment_by_year_list,
        "businessGroupStats": business_group_stats,
        "sectorCounts": {k: v["total"]["count"] for k, v in sector_stats.items()},
        "countProjectGroupByPublicAuthority": stats.get("pa_stats", []),
        "sectorProjectValueBubble": stats.get("bubble_stats", []),
        "pieContractTypeCount": pie_contract_counts,
    }
