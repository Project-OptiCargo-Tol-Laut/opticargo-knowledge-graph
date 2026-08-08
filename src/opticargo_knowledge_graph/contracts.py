"""Knowledge Graph internal event and query contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class EntityChangedEvent:
    event_id: str
    entity_type: str
    entity_id: str
    operation: str
    payload: dict[str, Any] = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProjectionResult:
    entity_type: str
    entity_id: str
    status: str
    detail: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


__all__ = ["EntityChangedEvent", "ProjectionResult"]
