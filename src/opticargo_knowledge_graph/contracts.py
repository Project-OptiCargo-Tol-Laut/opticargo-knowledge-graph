from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from importlib import import_module
from typing import Any, Callable

from .errors import ContractError


@dataclass(frozen=True)
class EventEnvelopeView:
    event_id: str
    event_type: str
    event_version: str
    occurred_at: datetime
    producer: str
    entity_type: str
    entity_id: str
    actor_id: str | None
    correlation_id: str
    idempotency_key: str
    payload: dict[str, Any]


def stream_fields_to_dict(fields: dict[str | bytes, str | bytes]) -> dict[str, Any]:
    decoded: dict[str, Any] = {}
    for raw_key, raw_value in fields.items():
        key = raw_key.decode() if isinstance(raw_key, bytes) else raw_key
        value = raw_value.decode() if isinstance(raw_value, bytes) else raw_value
        decoded[key] = value
    payload = decoded.get("payload")
    if isinstance(payload, str):
        try:
            decoded["payload"] = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ContractError("event payload is not valid JSON") from exc
    return decoded


def _load_shared_domain_event() -> type[Any]:
    try:
        module = import_module("opticargo_shared.events")
        return getattr(module, "DomainEvent")
    except (ImportError, AttributeError) as exc:
        raise ContractError("opticargo-shared==1.0.0 DomainEvent is unavailable") from exc


def validate_domain_event(
    raw: dict[str, Any],
    *,
    model_loader: Callable[[], type[Any]] | None = None,
) -> EventEnvelopeView:
    model = (model_loader or _load_shared_domain_event)()
    try:
        event = model.model_validate(raw)
        data = event.model_dump(mode="python")
    except Exception as exc:
        raise ContractError("DomainEvent validation failed") from exc
    occurred_at = data["occurred_at"]
    if isinstance(occurred_at, str):
        occurred_at = datetime.fromisoformat(occurred_at.replace("Z", "+00:00"))
    return EventEnvelopeView(
        event_id=str(data["event_id"]),
        event_type=str(data["event_type"]),
        event_version=str(data["event_version"]),
        occurred_at=occurred_at,
        producer=str(data["producer"]),
        entity_type=str(data["entity_type"]),
        entity_id=str(data["entity_id"]),
        actor_id=str(data["actor_id"]) if data.get("actor_id") else None,
        correlation_id=str(data["correlation_id"]),
        idempotency_key=str(data["idempotency_key"]),
        payload=dict(data.get("payload") or {}),
    )

from dataclasses import asdict as _asdict, field as _field
from datetime import timezone as _timezone

@dataclass(frozen=True)
class EntityChangedEvent:
    event_id: str
    entity_type: str
    entity_id: str
    operation: str
    payload: dict[str, Any] = _field(default_factory=dict)
    occurred_at: datetime = _field(default_factory=lambda: datetime.now(_timezone.utc))
    def to_dict(self) -> dict[str, Any]:
        return _asdict(self)

@dataclass(frozen=True)
class ProjectionResult:
    entity_type: str
    entity_id: str
    status: str
    detail: str | None = None
    def to_dict(self) -> dict[str, Any]:
        return _asdict(self)
