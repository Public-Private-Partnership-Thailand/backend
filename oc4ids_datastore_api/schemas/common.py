"""
Common / Shared Pydantic Schemas

Primitive building blocks reused across all feature schemas.
"""

import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Money & Period
# ---------------------------------------------------------------------------

class AmountResponse(BaseModel):
    """Represents a monetary amount with currency"""
    amount: Optional[float] = Field(None, description="Monetary amount", examples=[1500000000.0])
    currency: Optional[str] = Field(None, description="ISO 4217 currency code", examples=["THB"])


class AmountFormattedResponse(AmountResponse):
    """Monetary amount with a Thai-formatted string"""
    amountFormatted: Optional[str] = Field(
        None,
        description="Human-readable formatted amount (Thai)",
        examples=["1,500,000,000.00"],
    )


class PeriodResponse(BaseModel):
    """A date period"""
    startDate: Optional[str] = Field(None, description="Start date (ISO 8601)", examples=["2023-01-01"])
    endDate: Optional[str] = Field(None, description="End date (ISO 8601)", examples=["2028-12-31"])
    durationInDays: Optional[int] = Field(None, description="Duration in days", examples=[2190])
    maxExtentDate: Optional[str] = Field(None, description="Maximum extent date (ISO 8601)")


class AddressResponse(BaseModel):
    """Physical address"""
    streetAddress: Optional[str] = None
    locality: Optional[str] = None
    region: Optional[str] = None
    postalCode: Optional[str] = None
    countryName: Optional[str] = None


class IdentifierResponse(BaseModel):
    """Organization identifier"""
    scheme: Optional[str] = None
    id: Optional[str] = None
    legalName: Optional[str] = None
    uri: Optional[str] = None


class ContactPointResponse(BaseModel):
    """Contact information"""
    name: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    fax: Optional[str] = None
    url: Optional[str] = None


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

class PaginationResponse(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., description="Current page number", examples=[1])
    pageSize: int = Field(..., description="Number of items per page", examples=[20])
    total: int = Field(..., description="Total number of items", examples=[150])
    totalPages: int = Field(..., description="Total number of pages", examples=[8])


# ---------------------------------------------------------------------------
# Error Responses
# ---------------------------------------------------------------------------

class ErrorDetail(BaseModel):
    """Standard error detail"""
    detail: str = Field(..., description="Error description")


class ValidationErrorResponse(BaseModel):
    """422 Validation error response"""
    detail: List[Dict[str, Any]] = Field(..., description="List of validation errors")
