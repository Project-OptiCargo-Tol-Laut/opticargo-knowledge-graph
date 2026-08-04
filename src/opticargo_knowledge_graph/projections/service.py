"""Transactional, idempotent projection service."""

from __future__ import annotations

from typing import Any

from opticargo_knowledge_graph.contracts import EntityChangedEvent, ProjectionResult
from opticargo_knowledge_graph.metrics import record_projection
from opticargo_knowledge_graph.projections.registry import ProjectionRegistry
from opticargo_knowledge_graph.protocols import ProjectionSource

VALID_OPERATIONS = {"created", "updated", "deleted"}


class ProjectionService:
    def __init__(
        self,
        registry: ProjectionRegistry,
        source: ProjectionSource | None = None,
    ) -> None:
        self._registry = registry
        self._source = source

    def project(self, session, event: EntityChangedEvent) -> ProjectionResult:
        entity_type = event.entity_type.casefold()
        handler = self._registry.get(entity_type)
        if handler is None:
            return ProjectionResult(
                event.entity_type,
                event.entity_id,
                "skipped",
                "No projection handler registered",
            )
        operation = event.operation.casefold()
        if operation not in VALID_OPERATIONS:
            return ProjectionResult(
                event.entity_type,
                event.entity_id,
                "skipped",
                f"Unsupported operation: {operation}",
            )

        duplicate = session.run(
            "MATCH (e:_ProjectionEvent {event_id: $event_id}) RETURN e.event_id AS id",
            event_id=event.event_id,
        ).single()
        if duplicate is not None:
            record_projection(entity_type, "duplicate")
            return ProjectionResult(event.entity_type, event.entity_id, "duplicate")

        source_record = self._source.fetch(entity_type, event.entity_id) if self._source else None
        if operation != "deleted" and source_record is None:
            return ProjectionResult(
                event.entity_type,
                event.entity_id,
                "skipped",
                "Canonical PostgreSQL source is unavailable or entity does not exist",
            )
        record: dict[str, Any] = source_record or {}
        record["id"] = event.entity_id

        def project_transaction(tx):
            duplicate = tx.run(
                "MATCH (e:_ProjectionEvent {event_id: $event_id}) RETURN e.event_id AS id",
                event_id=event.event_id,
            ).single()
            if duplicate is not None:
                return "duplicate"
            handler(tx, record, operation)
            tx.run(
                """
                CREATE (e:_ProjectionEvent {
                    event_id: $event_id,
                    entity_type: $entity_type,
                    entity_id: $entity_id,
                    operation: $operation,
                    occurred_at: $occurred_at,
                    projected_at: datetime()
                })
                """,
                event_id=event.event_id,
                entity_type=entity_type,
                entity_id=event.entity_id,
                operation=operation,
                occurred_at=event.occurred_at,
            ).consume()
            return "deleted" if operation == "deleted" else "projected"

        status = session.execute_write(project_transaction)
        record_projection(entity_type, status)
        return ProjectionResult(event.entity_type, event.entity_id, status)

    def project_record(
        self,
        session,
        *,
        entity_type: str,
        entity_id: str,
        operation: str,
        record: dict[str, Any] | None = None,
    ) -> ProjectionResult:
        """Project a trusted source record without an event marker (reconciliation)."""
        handler = self._registry.get(entity_type)
        if handler is None:
            return ProjectionResult(entity_type, entity_id, "skipped", "No handler")
        normalized_operation = operation.casefold()
        payload = dict(record or {})
        payload["id"] = entity_id
        session.execute_write(handler, payload, normalized_operation)
        status = "deleted" if normalized_operation == "deleted" else "projected"
        record_projection(entity_type.casefold(), status)
        return ProjectionResult(entity_type, entity_id, status)


__all__ = ["VALID_OPERATIONS", "ProjectionService"]
