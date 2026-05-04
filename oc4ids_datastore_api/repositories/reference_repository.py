"""
Reference Data Repository (Data Access Layer)

Wraps all read queries for master/lookup tables.
Previously lived in daos.py as ReferenceDataDAO.
"""

from typing import List
from sqlmodel import Session, select

from oc4ids_datastore_api.models import (
    Sector, Ministry, AdditionalClassification,
)
from oc4ids_datastore_api.models.reference import ProjectType


class ReferenceRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_sectors(self) -> List[Sector]:
        return self.session.exec(
            select(Sector).where(Sector.is_active == True, Sector.parent_id.is_not(None))
        ).all()

    def get_ministries(self) -> List[Ministry]:
        return self.session.exec(select(Ministry)).all()

    def get_project_types(self):
        return self.session.exec(select(ProjectType)).all()

    def get_concession_forms(self) -> List:
        return self.session.exec(
            select(AdditionalClassification)
            .where(AdditionalClassification.scheme == "รูปแบบสัมปทานหรือค่าตอบแทน")
            .distinct()
        ).all()

    def get_contract_types(self) -> List:
        return self.session.exec(
            select(AdditionalClassification)
            .where(AdditionalClassification.scheme == "รูปแบบการจัดสรรกรรมสิทธิ์")
            .distinct()
        ).all()

    def get_risk_categories(self) -> List:
        from oc4ids_datastore_api.models import RiskCategory
        return self.session.exec(
            select(RiskCategory).order_by(RiskCategory.risk_category_id)
        ).all()

    def get_phase(self) -> List:
        from oc4ids_datastore_api.models import RiskPhase
        return self.session.exec(select(RiskPhase).order_by(RiskPhase.phase_id)).all()

    def get_risk_factors(self) -> List:
        from oc4ids_datastore_api.models import RiskFactor
        return self.session.exec(
            select(RiskFactor).order_by(RiskFactor.risk_factor_id)
        ).all()

    def get_risk_sources(self) -> List:
        from oc4ids_datastore_api.models import RiskSource
        return self.session.exec(select(RiskSource).order_by(RiskSource.rs_id)).all()


# Backward-compat alias
ReferenceDataDAO = ReferenceRepository
