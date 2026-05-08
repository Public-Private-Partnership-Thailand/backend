"""
Service-layer tests for oc4ids_datastore_api/services/project_service.py

Covers the public functions (create/update/delete/get_project_by_id/
get_projects_comparison) plus the _parse_date pure helper. Aimed at
catching regressions in the orchestration logic that was extracted
into per-section helpers — the integration tests in test_api.py only
exercise the happy path with a single payload shape.
"""

from datetime import date
from typing import Optional

import pytest
import uuid
from fastapi import HTTPException
from sqlmodel import Session, select

from oc4ids_datastore_api.models import Project, Sector, ProjectIdentifier, ProjectPeriod, Agency
from oc4ids_datastore_api.services.project_service import (
    _parse_date,
    create_project_data,
    update_project_data,
    delete_project_data,
    get_project_by_id,
    get_projects_comparison,
)


def _minimal_payload(title: str = "Svc Test", project_id: Optional[str] = None) -> dict:
    """Smallest payload that create_project_data accepts."""
    payload = {
        "title": title,
        "type": "หมวดการขนส่ง",
    }
    if project_id is not None:
        payload["id"] = project_id
    return payload


# ---------------------------------------------------------------------------
# _parse_date — pure helper
# ---------------------------------------------------------------------------

def test_parse_date_none_returns_none():
    assert _parse_date(None) is None


def test_parse_date_empty_string_returns_none():
    assert _parse_date("") is None


def test_parse_date_iso_string_returns_date():
    assert _parse_date("2024-05-09") == date(2024, 5, 9)


def test_parse_date_iso_with_z_timezone_returns_date():
    # The "Z" suffix must be normalized to "+00:00" before fromisoformat
    assert _parse_date("2024-05-09T00:00:00Z") == date(2024, 5, 9)


def test_parse_date_invalid_string_returns_none_silently():
    # _parse_date swallows ValueError to keep importers tolerant of bad data
    assert _parse_date("not-a-date") is None


# ---------------------------------------------------------------------------
# create_project_data — core paths
# ---------------------------------------------------------------------------

def test_create_project_data_minimal_payload(session: Session):
    result = create_project_data(_minimal_payload("Minimal"), session)

    assert result["status"] == "success"
    assert result["project"]["title"] == "Minimal"
    new_id = result["project"]["id"]

    saved = session.get(Project, uuid.UUID(new_id))
    assert saved is not None
    assert saved.title == "Minimal"
    assert saved.deleted_at is None


def test_create_project_data_invalid_uuid_generates_new_id(session: Session):
    # Caller-supplied id that isn't a valid UUID — service should generate one
    result = create_project_data(_minimal_payload("Bad UUID", project_id="not-a-uuid"), session)

    new_id = result["project"]["id"]
    # Generated id must be a valid UUID, not the bad input
    parsed = uuid.UUID(new_id)
    assert str(parsed) != "not-a-uuid"


def test_create_project_data_valid_uuid_is_preserved(session: Session):
    fixed_id = str(uuid.uuid4())
    result = create_project_data(_minimal_payload("Fixed", project_id=fixed_id), session)

    assert result["project"]["id"] == fixed_id
    # And an OC4IDS identifier row is added when caller supplied an id
    identifier = session.exec(
        select(ProjectIdentifier).where(ProjectIdentifier.project_id == uuid.UUID(fixed_id))
    ).first()
    assert identifier is not None
    assert identifier.scheme == "OC4IDS"


def test_create_project_data_creates_periods(session: Session):
    payload = _minimal_payload("With Periods")
    payload["period"] = {"startDate": "2024-01-01", "endDate": "2029-12-31"}
    payload["preparationPeriod"] = {"startDate": "2023-06-01", "endDate": "2023-12-31"}

    result = create_project_data(payload, session)

    project_id = uuid.UUID(result["project"]["id"])
    periods = session.exec(
        select(ProjectPeriod).where(ProjectPeriod.project_id == project_id)
    ).all()
    period_types = {p.period_type for p in periods}
    assert "duration" in period_types
    assert "preparation" in period_types


def test_create_project_data_unknown_sector_is_skipped(session: Session, caplog):
    # No Sector rows exist in this clean test DB → lookup misses, helper logs and skips
    payload = _minimal_payload("Unknown Sector")
    payload["sector"] = [{"id": "DOES-NOT-EXIST"}]

    with caplog.at_level("WARNING"):
        result = create_project_data(payload, session)

    project_id = uuid.UUID(result["project"]["id"])
    saved = session.get(Project, project_id)
    assert saved is not None
    assert saved.sectors == []
    assert any("DOES-NOT-EXIST" in rec.message for rec in caplog.records)


def test_create_project_data_known_sector_is_linked(session: Session):
    # Seed a sector so the lookup hits
    session.add(Sector(code="TRANS", name_th="ขนส่ง", category="infrastructure"))
    session.commit()

    payload = _minimal_payload("With Sector")
    payload["sector"] = [{"id": "TRANS"}]

    result = create_project_data(payload, session)
    project_id = uuid.UUID(result["project"]["id"])
    saved = session.get(Project, project_id)
    assert len(saved.sectors) == 1
    assert saved.sectors[0].code == "TRANS"


def test_create_project_data_creates_public_authority_agency(session: Session):
    payload = _minimal_payload("With PA")
    payload["publicAuthority"] = {"name": "กรมทางหลวง"}

    result = create_project_data(payload, session)
    project_id = uuid.UUID(result["project"]["id"])
    saved = session.get(Project, project_id)
    assert saved.public_authority_id is not None

    agency = session.get(Agency, saved.public_authority_id)
    assert agency is not None
    assert agency.name_th == "กรมทางหลวง"


def test_create_project_data_auto_commit_false_does_not_commit(session: Session):
    # When auto_commit=False the caller is expected to manage the transaction.
    # Service should flush so subsequent reads see the data within the same
    # session, but should not commit.
    result = create_project_data(_minimal_payload("Deferred"), session, auto_commit=False)

    project_id = uuid.UUID(result["project"]["id"])
    # Visible within the session (flush issued the INSERT)
    assert session.get(Project, project_id) is not None

    # But not yet committed: rolling back should drop the row
    session.rollback()
    assert session.get(Project, project_id) is None


# ---------------------------------------------------------------------------
# get_project_by_id / get_projects_comparison
# ---------------------------------------------------------------------------

def test_get_project_by_id_returns_dict(session: Session):
    result = create_project_data(_minimal_payload("Get By ID"), session)
    project_id = result["project"]["id"]

    fetched = get_project_by_id(session, project_id)
    assert fetched is not None
    assert fetched["title"] == "Get By ID"
    assert fetched["id"] == project_id


def test_get_project_by_id_returns_none_for_missing(session: Session):
    assert get_project_by_id(session, str(uuid.uuid4())) is None


def test_get_projects_comparison_returns_one_dict_per_id(session: Session):
    r1 = create_project_data(_minimal_payload("Cmp 1"), session)
    r2 = create_project_data(_minimal_payload("Cmp 2"), session)
    ids = [r1["project"]["id"], r2["project"]["id"]]

    comparison = get_projects_comparison(session, ids)
    assert len(comparison) == 2
    titles = {p["title"] for p in comparison}
    assert titles == {"Cmp 1", "Cmp 2"}


# ---------------------------------------------------------------------------
# update_project_data
# ---------------------------------------------------------------------------

def test_update_project_data_replaces_fields(session: Session):
    created = create_project_data(_minimal_payload("Old"), session)
    project_id = created["project"]["id"]

    new_payload = _minimal_payload("New")
    update_project_data(project_id, new_payload, session)

    refreshed = session.get(Project, uuid.UUID(project_id))
    assert refreshed is not None
    assert refreshed.title == "New"
    # ID is preserved across the delete-and-recreate
    assert str(refreshed.id) == project_id


def test_update_project_data_not_found_raises_404(session: Session):
    with pytest.raises(HTTPException) as exc_info:
        update_project_data(str(uuid.uuid4()), _minimal_payload("X"), session)
    assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# delete_project_data
# ---------------------------------------------------------------------------

def test_delete_project_data_soft_deletes(session: Session):
    created = create_project_data(_minimal_payload("To Delete"), session)
    project_id = created["project"]["id"]

    result = delete_project_data(project_id, session)
    assert "deleted" in result["message"].lower()

    # Soft delete: row is still in DB but deleted_at is set
    raw = session.get(Project, uuid.UUID(project_id))
    assert raw is not None
    assert raw.deleted_at is not None
    # And the public getter hides it
    assert get_project_by_id(session, project_id) is None


def test_delete_project_data_not_found_raises_404(session: Session):
    with pytest.raises(HTTPException) as exc_info:
        delete_project_data(str(uuid.uuid4()), session)
    assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Reference data TTL cache
# ---------------------------------------------------------------------------

def test_reference_info_cache_hits_on_second_call(session: Session):
    from oc4ids_datastore_api.services.reference_service import (
        get_reference_info,
        invalidate_reference_cache,
    )

    # First call populates the cache
    first = get_reference_info(session)
    initial_sector_count = len(first["sector"])

    # Mutate the DB *after* the cache is warm — second call must NOT see it
    session.add(Sector(code="LATE-INSERT", name_th="ทดสอบ", category="infrastructure"))
    session.commit()

    cached = get_reference_info(session)
    assert len(cached["sector"]) == initial_sector_count
    assert cached is first  # same object — confirms cache hit, not just equal contents

    # After explicit invalidation we requery and the new row appears
    invalidate_reference_cache()
    fresh = get_reference_info(session)
    assert len(fresh["sector"]) == initial_sector_count + 1
