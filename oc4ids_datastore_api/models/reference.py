"""
Reference / Lookup Tables

These are the master-data tables that other tables reference (Ministry, Sector,
Agency, Currency, etc.).  They are intentionally kept separate so that they can
be imported early without triggering circular-import issues with the larger
project tree.
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


# ---------------------------------------------------------------------------
# Project Type
# ---------------------------------------------------------------------------

class ProjectType(SQLModel, table=True):
    __tablename__ = "project_type"
    id: Optional[int] = Field(default=None, primary_key=True)
    scheme: Optional[str] = None
    code: str
    name_th: Optional[str] = None
    name_en: Optional[str] = None
    description: Optional[str] = None


# ---------------------------------------------------------------------------
# Ministry & Agency
# ---------------------------------------------------------------------------

class Ministry(SQLModel, table=True):
    __tablename__ = "ministry"
    id: Optional[int] = Field(default=None, primary_key=True)
    name_th: str
    name_en: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class Agency(SQLModel, table=True):
    __tablename__ = "agency"
    id: Optional[int] = Field(default=None, primary_key=True)
    name_th: str
    name_en: Optional[str] = None
    ministry_id: Optional[int] = Field(default=None, foreign_key="ministry.id")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Period Types
# ---------------------------------------------------------------------------

class PeriodType(SQLModel, table=True):
    __tablename__ = "period_types"
    code: str = Field(primary_key=True)
    name_en: str
    name_th: Optional[str] = None
    description: Optional[str] = None
    sequence: Optional[int] = None
    is_active: bool = Field(default=True)


# ---------------------------------------------------------------------------
# Sector
# ---------------------------------------------------------------------------

class Sector(SQLModel, table=True):
    __tablename__ = "sector"
    id: Optional[int] = Field(default=None, primary_key=True)
    id_from_bit_mask: Optional[int] = Field(default=None, unique=True)
    code: str = Field(unique=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="sector.id")
    name_th: str
    name_en: Optional[str] = None
    category: str
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Currency
# ---------------------------------------------------------------------------

class Currency(SQLModel, table=True):
    __tablename__ = "currencies"
    code: str = Field(primary_key=True, max_length=3)
    name: str
    symbol: Optional[str] = None
    is_active: bool = Field(default=True)


# ---------------------------------------------------------------------------
# Additional Classification
# ---------------------------------------------------------------------------

class AdditionalClassification(SQLModel, table=True):
    __tablename__ = "additional_classifications"
    id: Optional[int] = Field(default=None, primary_key=True)
    scheme: str
    code: str
    description: Optional[str] = None
    uri: Optional[str] = None
