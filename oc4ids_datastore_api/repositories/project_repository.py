"""
Project Repository (Data Access Layer)

Wraps all SQLModel/SQLAlchemy queries for the Project aggregate.
Previously lived in daos.py as ProjectDAO — renamed to match
Repository pattern nomenclature.
"""

from typing import List, Optional
import uuid
from sqlmodel import Session, select, func, or_
from sqlalchemy.orm import aliased

from oc4ids_datastore_api.models import (
    Project, Ministry, Agency, ProjectParty, PartyAdditionalIdentifier,
    Sector, ProjectSectorLink, ProjectPeriod, AdditionalClassification,
    ProjectAdditionalClassificationLink, ProjectBudget,
    Risk, RiskCategoryAssignment, RiskFactorAssignment,
)

# Keep the old name as an alias for backward compatibility
ProjectDAO = None  # set at bottom of file


class ProjectRepository:
    def __init__(self, session: Session):
        self.session = session

    # ------------------------------------------------------------------ #
    # Basic getters
    # ------------------------------------------------------------------ #

    def get_by_id(self, project_id: str) -> Optional[Project]:
        project = self.session.get(Project, project_id)
        if project and project.deleted_at:
            return None
        return project

    def get_by_ids(self, project_ids: List[str]) -> List[Project]:
        statement = (
            select(Project)
            .where(Project.id.in_(project_ids))
            .where(Project.deleted_at.is_(None))
        )
        return self.session.exec(statement).all()

    def count(self) -> int:
        return self.session.exec(
            select(func.count())
            .select_from(Project)
            .where(Project.deleted_at.is_(None))
        ).one()

    # ------------------------------------------------------------------ #
    # Filtered list query
    # ------------------------------------------------------------------ #

    def get_projects(
        self,
        skip: int = 0,
        limit: int = 20,
        title: Optional[str] = None,
        sector_id: Optional[List[int]] = None,
        ministry_id: Optional[List[int]] = None,
        agency_id: Optional[List[int]] = None,
        concession_form_id: Optional[List[int]] = None,
        contract_type_id: Optional[List[int]] = None,
        risk_category_id: Optional[List[int]] = None,
        risk_factor_id: Optional[List[int]] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
    ):
        FilterLastPeriod = aliased(ProjectPeriod)
        FilterSectorLink = aliased(ProjectSectorLink)
        FilterLinkConcession = aliased(ProjectAdditionalClassificationLink)
        FilterAgency = aliased(Agency)

        id_query = select(Project.id).where(Project.deleted_at.is_(None))

        if title:
            id_query = id_query.where(Project.title.ilike(f"%{title}%"))

        if sector_id:
            id_query = id_query.join(FilterSectorLink, Project.id == FilterSectorLink.project_id)
            id_query = id_query.where(FilterSectorLink.sector_id.in_(sector_id))

        if ministry_id:
            id_query = id_query.join(FilterAgency, Project.public_authority_id == FilterAgency.id, isouter=True)
            PartyMinistryFilter = aliased(Ministry)
            PartyIdentifierFilter = aliased(PartyAdditionalIdentifier)
            ProjectPartyFilter = aliased(ProjectParty)
            id_query = id_query.outerjoin(ProjectPartyFilter, Project.id == ProjectPartyFilter.project_id)
            id_query = id_query.outerjoin(PartyIdentifierFilter, ProjectPartyFilter.id == PartyIdentifierFilter.party_id)
            id_query = id_query.outerjoin(PartyMinistryFilter, PartyIdentifierFilter.legal_name_id == PartyMinistryFilter.id)
            id_query = id_query.where(
                or_(
                    PartyMinistryFilter.id.in_(ministry_id),
                    FilterAgency.ministry_id.in_(ministry_id),
                )
            )

        if concession_form_id:
            id_query = id_query.join(FilterLinkConcession, Project.id == FilterLinkConcession.project_id)
            id_query = id_query.where(FilterLinkConcession.classification_id.in_(concession_form_id))

        if contract_type_id:
            FilterLinkContract = aliased(ProjectAdditionalClassificationLink)
            id_query = id_query.join(FilterLinkContract, Project.id == FilterLinkContract.project_id)
            id_query = id_query.where(FilterLinkContract.classification_id.in_(contract_type_id))

        if risk_category_id:
            FilterRiskForCat = aliased(Risk)
            FilterRiskCatAssign = aliased(RiskCategoryAssignment)
            id_query = id_query.join(FilterRiskForCat, Project.id == FilterRiskForCat.project_id)
            id_query = id_query.join(FilterRiskCatAssign, FilterRiskForCat.risk_id == FilterRiskCatAssign.risk_id)
            id_query = id_query.where(FilterRiskCatAssign.risk_category_id.in_(risk_category_id))

        if risk_factor_id:
            FilterRiskForFactor = aliased(Risk)
            FilterRiskFactorAssign = aliased(RiskFactorAssignment)
            if not risk_category_id:
                id_query = id_query.join(FilterRiskForFactor, Project.id == FilterRiskForFactor.project_id)
            else:
                FilterRiskForFactor = FilterRiskForCat  # noqa: F821 — reuse alias
            id_query = id_query.join(FilterRiskFactorAssign, FilterRiskForFactor.risk_id == FilterRiskFactorAssign.risk_id)
            id_query = id_query.where(FilterRiskFactorAssign.risk_factor_id.in_(risk_factor_id))

        if year_from or year_to:
            id_query = id_query.join(
                FilterLastPeriod,
                (Project.id == FilterLastPeriod.project_id) & (FilterLastPeriod.period_type == "duration"),
            )
            if year_from and year_to:
                id_query = id_query.where(func.extract("year", FilterLastPeriod.start_date) <= year_to)
                id_query = id_query.where(func.extract("year", FilterLastPeriod.end_date) >= year_from)
            elif year_from:
                id_query = id_query.where(func.extract("year", FilterLastPeriod.end_date) >= year_from)
            elif year_to:
                id_query = id_query.where(func.extract("year", FilterLastPeriod.start_date) <= year_to)

        id_query = id_query.distinct().offset(skip).limit(limit)
        project_ids = self.session.exec(id_query).all()

        if not project_ids:
            return []

        PartyAgency = aliased(Agency)
        AgencyMinistry = aliased(Ministry)

        statement = (
            select(
                Project.id,
                Project.title,
                Agency.name_en.label("agency_name"),
                func.string_agg(Ministry.name_en.distinct(), ", ").label("party_ministry_names"),
                func.string_agg(PartyAgency.name_en.distinct(), ", ").label("private_party_name"),
                func.array_agg(Sector.name_en.distinct()).label("sector_names"),
                func.array_agg(AdditionalClassification.description.distinct()).filter(
                    AdditionalClassification.scheme == "รูปแบบสัมปทานหรือค่าตอบแทน"
                ).label("concession_names"),
                func.array_agg(AdditionalClassification.description.distinct()).filter(
                    AdditionalClassification.scheme == "รูปแบบการจัดสรรกรรมสิทธิ์"
                ).label("contract_type_names"),
                func.min(ProjectPeriod.start_date).label("start_date"),
                func.sum(ProjectBudget.total_amount).label("budget_amount"),
            )
            .filter(Project.id.in_(project_ids))
            .join(Agency, Project.public_authority_id == Agency.id, isouter=True)
            .join(ProjectBudget, Project.id == ProjectBudget.project_id, isouter=True)
            .join(ProjectParty, Project.id == ProjectParty.project_id, isouter=True)
            .join(PartyAdditionalIdentifier, ProjectParty.id == PartyAdditionalIdentifier.party_id, isouter=True)
            .join(Ministry, PartyAdditionalIdentifier.legal_name_id == Ministry.id, isouter=True)
            .join(PartyAgency, ProjectParty.identifier_legal_name_id == PartyAgency.id, isouter=True)
            .join(ProjectSectorLink, Project.id == ProjectSectorLink.project_id, isouter=True)
            .join(Sector, ProjectSectorLink.sector_id == Sector.id, isouter=True)
            .join(ProjectAdditionalClassificationLink, Project.id == ProjectAdditionalClassificationLink.project_id, isouter=True)
            .join(AdditionalClassification, ProjectAdditionalClassificationLink.classification_id == AdditionalClassification.id, isouter=True)
            .join(ProjectPeriod, Project.id == ProjectPeriod.project_id, isouter=True)
            .group_by(Project.id, Project.title, Agency.name_en)
        )
        return self.session.exec(statement).all()

    def get_summaries(self, *args, **kwargs):
        return self.get_projects(*args, **kwargs)

    # ------------------------------------------------------------------ #
    # Write operations
    # ------------------------------------------------------------------ #

    def create(self, project: Project) -> Project:
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def update(self, project: Project) -> Project:
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def delete(self, project_id: str, hard_delete: bool = False, auto_commit: bool = True) -> None:
        from datetime import datetime

        project = self.session.get(Project, project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")

        if hard_delete:
            self.session.delete(project)
        else:
            project.deleted_at = datetime.utcnow()
            self.session.add(project)

        if auto_commit:
            self.session.commit()
        else:
            self.session.flush()

    # ------------------------------------------------------------------ #
    # Dashboard aggregations
    # ------------------------------------------------------------------ #

    def get_dashboard_stats(
        self,
        title: Optional[str] = None,
        sector_id: Optional[List[int]] = None,
        ministry_id: Optional[List[int]] = None,
        agency_id: Optional[List[int]] = None,
        concession_form_id: Optional[List[int]] = None,
        contract_type_id: Optional[List[int]] = None,
        risk_category_id: Optional[List[int]] = None,
        risk_factor_id: Optional[List[int]] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
    ) -> dict:
        from sqlalchemy import func, case, and_, or_

        FilterLastPeriod = aliased(ProjectPeriod)
        FilterSectorLink = aliased(ProjectSectorLink)
        FilterLinkConcession = aliased(ProjectAdditionalClassificationLink)
        FilterAgency = aliased(Agency)

        id_query = select(Project.id).where(Project.deleted_at.is_(None))

        if title:
            id_query = id_query.where(Project.title.ilike(f"%{title}%"))
        if sector_id:
            id_query = id_query.join(FilterSectorLink, Project.id == FilterSectorLink.project_id)
            id_query = id_query.where(FilterSectorLink.sector_id.in_(sector_id))
        if ministry_id:
            id_query = id_query.join(FilterAgency, Project.public_authority_id == FilterAgency.id, isouter=True)
            PartyMinistryFilter = aliased(Ministry)
            PartyIdentifierFilter = aliased(PartyAdditionalIdentifier)
            ProjectPartyFilter = aliased(ProjectParty)
            id_query = id_query.outerjoin(ProjectPartyFilter, Project.id == ProjectPartyFilter.project_id)
            id_query = id_query.outerjoin(PartyIdentifierFilter, ProjectPartyFilter.id == PartyIdentifierFilter.party_id)
            id_query = id_query.outerjoin(PartyMinistryFilter, PartyIdentifierFilter.legal_name_id == PartyMinistryFilter.id)
            id_query = id_query.where(
                or_(
                    PartyMinistryFilter.id.in_(ministry_id),
                    FilterAgency.ministry_id.in_(ministry_id),
                )
            )
        if concession_form_id:
            id_query = id_query.join(FilterLinkConcession, Project.id == FilterLinkConcession.project_id)
            id_query = id_query.where(FilterLinkConcession.classification_id.in_(concession_form_id))
        if contract_type_id:
            FilterLinkContract = aliased(ProjectAdditionalClassificationLink)
            id_query = id_query.join(FilterLinkContract, Project.id == FilterLinkContract.project_id)
            id_query = id_query.where(FilterLinkContract.classification_id.in_(contract_type_id))
        if risk_category_id:
            FilterRiskForCat = aliased(Risk)
            FilterRiskCatAssign = aliased(RiskCategoryAssignment)
            id_query = id_query.join(FilterRiskForCat, Project.id == FilterRiskForCat.project_id)
            id_query = id_query.join(FilterRiskCatAssign, FilterRiskForCat.risk_id == FilterRiskCatAssign.risk_id)
            id_query = id_query.where(FilterRiskCatAssign.risk_category_id.in_(risk_category_id))
        if risk_factor_id:
            FilterRiskForFactor = aliased(Risk)
            FilterRiskFactorAssign = aliased(RiskFactorAssignment)
            if not risk_category_id:
                id_query = id_query.join(FilterRiskForFactor, Project.id == FilterRiskForFactor.project_id)
            else:
                FilterRiskForFactor = FilterRiskForCat  # noqa: F821
            id_query = id_query.join(FilterRiskFactorAssign, FilterRiskForFactor.risk_id == FilterRiskFactorAssign.risk_id)
            id_query = id_query.where(FilterRiskFactorAssign.risk_factor_id.in_(risk_factor_id))
        if year_from or year_to:
            id_query = id_query.join(
                FilterLastPeriod,
                (Project.id == FilterLastPeriod.project_id) & (FilterLastPeriod.period_type == "duration"),
            )
            if year_from and year_to:
                id_query = id_query.where(func.extract("year", FilterLastPeriod.start_date) <= year_to)
                id_query = id_query.where(func.extract("year", FilterLastPeriod.end_date) >= year_from)
            elif year_from:
                id_query = id_query.where(func.extract("year", FilterLastPeriod.end_date) >= year_from)
            elif year_to:
                id_query = id_query.where(func.extract("year", FilterLastPeriod.start_date) <= year_to)

        filtered_project_ids = id_query.distinct().subquery()
        total_projects = self.session.exec(select(func.count()).select_from(filtered_project_ids)).one()

        if total_projects == 0:
            all_active_sectors = self.session.exec(
                select(Sector.name_en).where(Sector.is_active == True)
            ).all()
            empty_sector_stats = {
                s: {"total": {"count": 0, "investment": 0}, "small": {"count": 0, "investment": 0},
                    "medium": {"count": 0, "investment": 0}, "big": {"count": 0, "investment": 0}}
                for s in all_active_sectors
            }
            return {
                "total_projects": 0, "total_investment": 0, "max_budget": 0,
                "unique_contractors": 0, "unique_public_authority": 0, "inprogress_projects": 0,
                "ministry_counts": {}, "ministry_investments": {},
                "project_scales": {"big": {"count": 0, "investment": 0}, "medium": {"count": 0, "investment": 0}, "small": {"count": 0, "investment": 0}},
                "sector_stats": empty_sector_stats, "investment_by_year": {}, "project_ids": [],
            }

        ProjectBudgetAlias = aliased(ProjectBudget)

        total_investment = self.session.exec(
            select(func.sum(ProjectBudgetAlias.total_amount))
            .where(ProjectBudgetAlias.project_id.in_(select(filtered_project_ids.c.id)))
        ).one() or 0

        max_budget = self.session.exec(
            select(func.max(ProjectBudgetAlias.total_amount))
            .where(ProjectBudgetAlias.project_id.in_(select(filtered_project_ids.c.id)))
        ).one() or 0

        AgencyCountAlias = aliased(Agency)
        unique_contractors = self.session.exec(
            select(func.count(AgencyCountAlias.id)).where(AgencyCountAlias.ministry_id.is_(None))
        ).one()

        unique_public_authority = self.session.exec(
            select(func.count(func.distinct(Project.public_authority_id)))
            .where(Project.id.in_(select(filtered_project_ids.c.id)))
        ).one() or 0

        ProjectPartyAlias = aliased(ProjectParty)
        MinistryAlias = aliased(Ministry)
        AgencyAlias = aliased(Agency)
        IdentifierAlias = aliased(PartyAdditionalIdentifier)

        stats_query = (
            select(
                MinistryAlias.name_en,
                func.count(func.distinct(Project.id)),
                func.sum(ProjectBudgetAlias.total_amount),
            )
            .join(ProjectPartyAlias, Project.id == ProjectPartyAlias.project_id)
            .join(IdentifierAlias, ProjectPartyAlias.id == IdentifierAlias.party_id)
            .join(MinistryAlias, IdentifierAlias.legal_name_id == MinistryAlias.id)
            .outerjoin(ProjectBudgetAlias, Project.id == ProjectBudgetAlias.project_id)
            .where(Project.id.in_(select(filtered_project_ids.c.id)))
            .group_by(MinistryAlias.id, MinistryAlias.name_en)
        )
        ministry_stats_results = self.session.exec(stats_query).all()
        ministry_counts = {row[0]: row[1] for row in ministry_stats_results}
        ministry_investments = {row[0]: (row[2] or 0) for row in ministry_stats_results}

        scale_query = (
            select(
                func.sum(case((ProjectBudgetAlias.total_amount >= 5000000000, 1), else_=0)).label("big_count"),
                func.sum(case((ProjectBudgetAlias.total_amount >= 5000000000, ProjectBudgetAlias.total_amount), else_=0)).label("big_investment"),
                func.sum(case((and_(ProjectBudgetAlias.total_amount >= 1000000000, ProjectBudgetAlias.total_amount < 5000000000), 1), else_=0)).label("medium_count"),
                func.sum(case((and_(ProjectBudgetAlias.total_amount >= 1000000000, ProjectBudgetAlias.total_amount < 5000000000), ProjectBudgetAlias.total_amount), else_=0)).label("medium_investment"),
                func.sum(case((ProjectBudgetAlias.total_amount < 1000000000, 1), else_=0)).label("small_count"),
                func.sum(case((ProjectBudgetAlias.total_amount < 1000000000, ProjectBudgetAlias.total_amount), else_=0)).label("small_investment"),
            )
            .where(ProjectBudgetAlias.project_id.in_(select(filtered_project_ids.c.id)))
        )
        scale_results = self.session.exec(scale_query).first()
        project_scales = {
            "big": {"count": scale_results[0] or 0, "investment": scale_results[1] or 0},
            "medium": {"count": scale_results[2] or 0, "investment": scale_results[3] or 0},
            "small": {"count": scale_results[4] or 0, "investment": scale_results[5] or 0},
        }

        SectorAlias = aliased(Sector)
        ProjectSectorLinkAlias = aliased(ProjectSectorLink)
        sector_query = (
            select(
                SectorAlias.name_en,
                func.count(func.distinct(Project.id)),
                func.sum(ProjectBudgetAlias.total_amount),
                func.sum(case((ProjectBudgetAlias.total_amount < 1000000000, 1), else_=0)),
                func.sum(case((ProjectBudgetAlias.total_amount < 1000000000, ProjectBudgetAlias.total_amount), else_=0)),
                func.sum(case((and_(ProjectBudgetAlias.total_amount >= 1000000000, ProjectBudgetAlias.total_amount < 5000000000), 1), else_=0)),
                func.sum(case((and_(ProjectBudgetAlias.total_amount >= 1000000000, ProjectBudgetAlias.total_amount < 5000000000), ProjectBudgetAlias.total_amount), else_=0)),
                func.sum(case((ProjectBudgetAlias.total_amount >= 5000000000, 1), else_=0)),
                func.sum(case((ProjectBudgetAlias.total_amount >= 5000000000, ProjectBudgetAlias.total_amount), else_=0)),
            )
            .join(ProjectSectorLinkAlias, Project.id == ProjectSectorLinkAlias.project_id)
            .join(SectorAlias, ProjectSectorLinkAlias.sector_id == SectorAlias.id)
            .outerjoin(ProjectBudgetAlias, Project.id == ProjectBudgetAlias.project_id)
            .where(Project.id.in_(select(filtered_project_ids.c.id)))
            .group_by(SectorAlias.id, SectorAlias.name_en)
        )
        all_active_sectors_query = select(Sector.name_en).where(Sector.is_active == True)
        all_active_sectors = self.session.exec(all_active_sectors_query).all()
        sector_stats = {
            s: {"total": {"count": 0, "investment": 0}, "small": {"count": 0, "investment": 0},
                "medium": {"count": 0, "investment": 0}, "big": {"count": 0, "investment": 0}}
            for s in all_active_sectors
        }
        for row in self.session.exec(sector_query).all():
            sector_stats[row[0]] = {
                "total": {"count": row[1], "investment": row[2] or 0},
                "small": {"count": row[3] or 0, "investment": row[4] or 0},
                "medium": {"count": row[5] or 0, "investment": row[6] or 0},
                "big": {"count": row[7] or 0, "investment": row[8] or 0},
            }

        from datetime import date as date_cls
        today = date_cls.today()
        ProjectPeriodInProgress = aliased(ProjectPeriod)
        inprogress_projects = self.session.exec(
            select(func.count(func.distinct(Project.id)))
            .join(ProjectPeriodInProgress,
                  (Project.id == ProjectPeriodInProgress.project_id) &
                  (ProjectPeriodInProgress.period_type == "duration"))
            .where(
                Project.id.in_(select(filtered_project_ids.c.id)),
                ProjectPeriodInProgress.end_date >= today,
            )
        ).one() or 0

        ProjectPeriodAlias = aliased(ProjectPeriod)
        year_results = self.session.exec(
            select(
                func.extract("year", ProjectPeriodAlias.start_date).label("year"),
                func.count(func.distinct(Project.id)),
                func.sum(ProjectBudgetAlias.total_amount),
            )
            .join(ProjectPeriodAlias, Project.id == ProjectPeriodAlias.project_id)
            .outerjoin(ProjectBudgetAlias, Project.id == ProjectBudgetAlias.project_id)
            .where(
                Project.id.in_(select(filtered_project_ids.c.id)),
                ProjectPeriodAlias.period_type == "duration",
                ProjectPeriodAlias.start_date.is_not(None),
            )
            .group_by("year")
            .order_by("year")
        ).all()
        investment_by_year = {
            int(y): {"count": c, "investment": i or 0}
            for y, c, i in year_results if y
        }

        PublicAuthAgency = aliased(Agency)
        pa_results = self.session.exec(
            select(
                PublicAuthAgency.name_th.label("publicAuthorityName"),
                func.count(Project.id).label("projectCount"),
            )
            .join(PublicAuthAgency, Project.public_authority_id == PublicAuthAgency.id)
            .where(Project.id.in_(select(filtered_project_ids.c.id)))
            .group_by(PublicAuthAgency.id, PublicAuthAgency.name_th)
            .order_by(func.count(Project.id).desc())
        ).all()
        pa_stats = [{"publicAuthorityName": row[0], "projectCount": row[1]} for row in pa_results]

        SectorBubbleAlias = aliased(Sector)
        bubble_results = self.session.exec(
            select(
                SectorBubbleAlias.code.label("sector"),
                func.count(func.distinct(Project.id)).label("projectCount"),
                func.sum(ProjectBudgetAlias.total_amount).label("totalValue"),
                func.count(func.distinct(Project.public_authority_id)).label("authorityCount"),
            )
            .join(ProjectSectorLink, Project.id == ProjectSectorLink.project_id)
            .join(SectorBubbleAlias, ProjectSectorLink.sector_id == SectorBubbleAlias.id)
            .outerjoin(ProjectBudgetAlias, Project.id == ProjectBudgetAlias.project_id)
            .where(Project.id.in_(select(filtered_project_ids.c.id)))
            .group_by(SectorBubbleAlias.id, SectorBubbleAlias.code)
        ).all()
        all_active_sectors_objs = self.session.exec(select(Sector).where(Sector.is_active == True)).all()
        bubble_map = {
            s.code: {"sector": s.code, "projectCount": 0, "totalValue": 0, "authorityCount": 0}
            for s in all_active_sectors_objs
        }
        if "others" not in bubble_map:
            bubble_map["others"] = {"sector": "others", "projectCount": 0, "totalValue": 0, "authorityCount": 0}
        for row in bubble_results:
            s_code = row[0]
            if s_code in bubble_map:
                bubble_map[s_code].update({"projectCount": row[1], "totalValue": float(row[2] or 0), "authorityCount": row[3]})
            else:
                bubble_map[s_code] = {"sector": s_code, "projectCount": row[1], "totalValue": float(row[2] or 0), "authorityCount": row[3]}

        ContractTypeAlias = aliased(AdditionalClassification)
        ProjectClassificationLinkAlias = aliased(ProjectAdditionalClassificationLink)
        contract_type_results = self.session.exec(
            select(
                ContractTypeAlias.id,
                ContractTypeAlias.code.label("name"),
                ContractTypeAlias.description.label("fullName"),
                func.count(func.distinct(Project.id)).label("count"),
            )
            .select_from(ContractTypeAlias)
            .outerjoin(ProjectClassificationLinkAlias, ContractTypeAlias.id == ProjectClassificationLinkAlias.classification_id)
            .outerjoin(Project, Project.id == ProjectClassificationLinkAlias.project_id)
            .where(
                ContractTypeAlias.scheme == "รูปแบบการจัดสรรกรรมสิทธิ์",
                or_(
                    Project.id.is_(None),
                    Project.id.in_(select(filtered_project_ids.c.id))
                )
            )
            .group_by(ContractTypeAlias.id, ContractTypeAlias.code, ContractTypeAlias.description)
        ).all()
        contract_types_list = [
            {"id": row[0], "name": row[1], "fullName": row[2] or row[1], "count": row[3]}
            for row in contract_type_results
        ]

        return {
            "total_projects": total_projects,
            "total_investment": total_investment,
            "max_budget": max_budget,
            "unique_contractors": unique_contractors,
            "unique_public_authority": unique_public_authority,
            "inprogress_projects": inprogress_projects,
            "ministry_counts": ministry_counts,
            "ministry_investments": ministry_investments,
            "project_scales": project_scales,
            "sector_stats": sector_stats,
            "investment_by_year": investment_by_year,
            "pa_stats": pa_stats,
            "bubble_stats": list(bubble_map.values()),
            "contract_type_counts": contract_types_list,
            "project_ids": [row for row in self.session.exec(select(filtered_project_ids)).all()],
        }


# Backward-compat alias (old code that still uses ProjectDAO will still work)
ProjectDAO = ProjectRepository
