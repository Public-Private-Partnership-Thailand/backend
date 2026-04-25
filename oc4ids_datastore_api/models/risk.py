"""
Risk-management Models

Separate from the main project tree to avoid circular imports and to keep the
domain boundary clear.
"""

import uuid
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


# ---------------------------------------------------------------------------
# Risk Reference Tables
# ---------------------------------------------------------------------------

class RiskCategory(SQLModel, table=True):
    __tablename__ = "risk_category"
    risk_category_id: Optional[int] = Field(default=None, primary_key=True)
    category_code: Optional[str] = Field(default=None, unique=True)
    category_name: Optional[str] = None
    description_en: Optional[str] = None
    description_th: Optional[str] = None

    # Relationships
    risk_assignments: List["RiskCategoryAssignment"] = Relationship(back_populates="category", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    factor_links: List["CategoryFactorLink"] = Relationship(back_populates="category", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    patterns: List["RiskPattern"] = Relationship(back_populates="category", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class RiskFactor(SQLModel, table=True):
    __tablename__ = "risk_factor"
    risk_factor_id: Optional[int] = Field(default=None, primary_key=True)
    factor_name: Optional[str] = Field(default=None, unique=True)
    description_th: Optional[str] = None

    # Relationships
    category_links: List["CategoryFactorLink"] = Relationship(back_populates="factor", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    risk_assignments: List["RiskFactorAssignment"] = Relationship(back_populates="factor", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    patterns: List["RiskPattern"] = Relationship(back_populates="factor", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class RiskSource(SQLModel, table=True):
    __tablename__ = "risk_source"
    rs_id: Optional[int] = Field(default=None, primary_key=True)
    rs_id_from_bit_mask: Optional[int] = None
    meaning: Optional[str] = None
    country: Optional[str] = None
    reference: Optional[str] = None
    reference_file: Optional[str] = None
    reference_url: Optional[str] = None


class RiskPhase(SQLModel, table=True):
    __tablename__ = "risk_phase"
    phase_id: Optional[int] = Field(default=None, primary_key=True)
    phase_id_from_bit_mask: Optional[int] = None
    phase_name: Optional[str] = None
    meaning: Optional[str] = None


class RiskPattern(SQLModel, table=True):
    __tablename__ = "risk_pattern"
    pattern_id: Optional[int] = Field(default=None, primary_key=True)
    risk_category_id: int = Field(foreign_key="risk_category.risk_category_id")
    risk_factor_id: int = Field(foreign_key="risk_factor.risk_factor_id")
    phase: int
    source: int

    # Relationships
    category: "RiskCategory" = Relationship(back_populates="patterns")
    factor: "RiskFactor" = Relationship(back_populates="patterns")


# ---------------------------------------------------------------------------
# Project-level Risk Models
# ---------------------------------------------------------------------------

class Risk(SQLModel, table=True):
    __tablename__ = "risk"
    risk_id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str] = None
    phase: Optional[str] = None
    project_id: uuid.UUID = Field(foreign_key="projects.id")

    # Relationships
    project: "Project" = Relationship(back_populates="risks")  # type: ignore[name-defined]
    mitigations: List["Mitigation"] = Relationship(back_populates="risk", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    impacts: List["Impact"] = Relationship(back_populates="risk", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    category_assignments: List["RiskCategoryAssignment"] = Relationship(back_populates="risk", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    factor_assignments: List["RiskFactorAssignment"] = Relationship(back_populates="risk", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class Mitigation(SQLModel, table=True):
    __tablename__ = "mitigation"
    mitigation_id: Optional[int] = Field(default=None, primary_key=True)
    action: Optional[str] = None
    status: Optional[str] = None
    risk_id: int = Field(foreign_key="risk.risk_id")

    # Relationships
    risk: "Risk" = Relationship(back_populates="mitigations")


class Impact(SQLModel, table=True):
    __tablename__ = "impact"
    impact_id: Optional[int] = Field(default=None, primary_key=True)
    description: Optional[str] = None
    risk_id: int = Field(foreign_key="risk.risk_id")

    # Relationships
    risk: "Risk" = Relationship(back_populates="impacts")


# ---------------------------------------------------------------------------
# Junction Tables
# ---------------------------------------------------------------------------

class RiskCategoryAssignment(SQLModel, table=True):
    """Junction: Risk ↔ RiskCategory (Many-to-Many)"""
    __tablename__ = "risk_category_assignment"
    risk_id: int = Field(foreign_key="risk.risk_id", primary_key=True)
    risk_category_id: int = Field(foreign_key="risk_category.risk_category_id", primary_key=True)

    # Relationships
    risk: "Risk" = Relationship(back_populates="category_assignments")
    category: "RiskCategory" = Relationship(back_populates="risk_assignments")


class CategoryFactorLink(SQLModel, table=True):
    """Junction: RiskCategory ↔ RiskFactor (Many-to-Many)"""
    __tablename__ = "category_factor_link"
    risk_category_id: int = Field(foreign_key="risk_category.risk_category_id", primary_key=True)
    risk_factor_id: int = Field(foreign_key="risk_factor.risk_factor_id", primary_key=True)

    # Relationships
    category: "RiskCategory" = Relationship(back_populates="factor_links")
    factor: "RiskFactor" = Relationship(back_populates="category_links")


class RiskFactorAssignment(SQLModel, table=True):
    """Junction: Risk ↔ RiskFactor (Many-to-Many)"""
    __tablename__ = "risk_factor_assignment"
    risk_id: int = Field(foreign_key="risk.risk_id", primary_key=True)
    risk_factor_id: int = Field(foreign_key="risk_factor.risk_factor_id", primary_key=True)

    # Relationships
    risk: "Risk" = Relationship(back_populates="factor_assignments")
    factor: "RiskFactor" = Relationship(back_populates="risk_assignments")



