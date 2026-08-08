"""Synthetic canonical source and cleanup helpers for graph E2E journeys."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from opticargo_knowledge_graph.contracts import EntityChangedEvent


class DictSource:
    def __init__(self) -> None:
        self.records: dict[tuple[str, str], dict[str, Any]] = {}

    def put(self, entity_type: str, record: dict[str, Any]) -> str:
        entity_id = str(record["id"])
        self.records[(entity_type, entity_id)] = dict(record)
        return entity_id

    def fetch(self, entity_type: str, entity_id: str) -> dict[str, Any] | None:
        record = self.records.get((entity_type, entity_id))
        return dict(record) if record else None


def project(session, service, entity_type: str, entity_id: str, operation: str = "created"):
    event = EntityChangedEvent(
        str(uuid4()),
        entity_type,
        entity_id,
        operation,
        occurred_at=datetime.now(UTC),
    )
    return service.project(session, event)


def cleanup_entities(session, entity_ids: list[str]) -> None:
    session.run(
        "MATCH (n) WHERE n.id IN $ids DETACH DELETE n",
        ids=entity_ids,
    ).consume()
    session.run(
        "MATCH (e:_ProjectionEvent) WHERE e.entity_id IN $ids DELETE e",
        ids=entity_ids,
    ).consume()
