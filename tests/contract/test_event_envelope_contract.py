"""DomainEvent carries UTC correlation/idempotency fields and explicit version."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from opticargo_shared.events import EVENT_VERSION, DomainEvent, EventType
from pydantic import ValidationError


def make_event(**overrides) -> DomainEvent:
    values = {
        "event_id": uuid4(),
        "event_type": EventType.entity_changed,
        "event_version": EVENT_VERSION,
        "occurred_at": datetime.now(UTC),
        "producer": "contract-test",
        "entity_type": "port",
        "entity_id": uuid4(),
        "correlation_id": uuid4(),
        "idempotency_key": "entity:port:1",
        "payload": {"operation": "updated"},
    }
    values.update(overrides)
    return DomainEvent(**values)


def test_event_roundtrip_preserves_contract_fields() -> None:
    event = make_event()
    decoded = DomainEvent.model_validate_json(event.model_dump_json())
    assert decoded == event
    assert decoded.occurred_at.tzinfo is not None
    assert decoded.correlation_id and decoded.idempotency_key


def test_event_rejects_naive_timestamp() -> None:
    with pytest.raises(ValidationError):
        make_event(occurred_at=datetime.now())
