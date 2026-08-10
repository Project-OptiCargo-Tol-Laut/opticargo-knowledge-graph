from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..contracts import EventEnvelopeView
from ..errors import ContractError, UnsupportedEventError
from .models import ProjectionPlan
from .registry import get_projection_spec, normalize_entity_type


@dataclass(frozen=True)
class ProjectionOutcome:
    entity_type: str
    entity_id: str
    action: str
    source_hash: str | None = None


_EVENT_ENTITY_MAP = {
    "booking.created": "booking",
    "booking.status_changed": "booking",
    "payment.created": "payment",
    "payment.status_changed": "payment",
    "document.uploaded": "document",
    "document.ingestion_completed": "document",
    "document.ingestion_failed": "document",
    "recommendation.created": "recommendation",
    "review.created": "review",
}


def resolve_projection_target(event: EventEnvelopeView) -> tuple[str, str, str]:
    if event.event_type == "entity.changed":
        entity_type = normalize_entity_type(str(event.payload.get("entity_type") or event.entity_type))
        entity_id = str(event.payload.get("entity_id") or event.entity_id)
        action = str(event.payload.get("change_type") or "updated").lower()
        if action not in {"created", "updated", "deleted"}:
            raise ContractError(f"unsupported entity change type: {action}")
        return entity_type, entity_id, action

    mapped = _EVENT_ENTITY_MAP.get(event.event_type)
    if mapped is None:
        raise UnsupportedEventError(f"event type is not projected: {event.event_type}")
    return mapped, event.entity_id, "updated"


class ProjectionService:
    def __init__(self, postgres: Any, neo4j: Any | None = None) -> None:
        # Final mode: ProjectionService(PostgresClient, Neo4jClient).
        # Develop compatibility: ProjectionService(ProjectionRegistry, source=None).
        if hasattr(postgres, "get"):
            self._legacy_registry = postgres
            self._legacy_source = neo4j
            self._postgres = None
            self._source = None
            self._neo4j = None
        else:
            self._legacy_registry = None
            self._legacy_source = None
            self._postgres = postgres
            self._source = postgres
            self._neo4j = neo4j

    def project(self, session: Any, event: Any):
        if self._legacy_registry is not None:
            from opticargo_knowledge_graph.contracts import ProjectionResult
            handler = self._legacy_registry.get(str(event.entity_type))
            if handler is None:
                return ProjectionResult(event.entity_type, event.entity_id, "skipped", "No projection handler registered")
            operation = str(getattr(event, "operation", "updated")).casefold()
            if operation not in {"created", "updated", "deleted"}:
                return ProjectionResult(event.entity_type, event.entity_id, "skipped", f"Unsupported operation: {operation}")
            duplicate = session.run("MATCH (e:_ProjectionEvent {event_id: $event_id}) RETURN e.event_id AS id", event_id=event.event_id).single()
            if duplicate is not None:
                return ProjectionResult(event.entity_type, event.entity_id, "duplicate")
            source_record = self._legacy_source.fetch(str(event.entity_type).casefold(), event.entity_id) if self._legacy_source else None
            if operation != "deleted" and self._legacy_source is not None and source_record is None:
                return ProjectionResult(event.entity_type, event.entity_id, "skipped", "Canonical PostgreSQL source is unavailable or entity does not exist")
            record = dict(source_record or getattr(event, "payload", {}) or {})
            record["id"] = event.entity_id
            def tx_project(tx):
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
                        event_id: $event_id, entity_type: $entity_type, entity_id: $entity_id,
                        operation: $operation, occurred_at: $occurred_at, projected_at: datetime()
                    })
                    """,
                    event_id=event.event_id, entity_type=str(event.entity_type).casefold(),
                    entity_id=event.entity_id, operation=operation, occurred_at=event.occurred_at,
                ).consume()
                return "deleted" if operation == "deleted" else "projected"
            status = session.execute_write(tx_project) if hasattr(session, "execute_write") else tx_project(session)
            return ProjectionResult(event.entity_type, event.entity_id, status)

        entity_type = normalize_entity_type(str(event.entity_type))
        if hasattr(self._source, "fetch"):
            self._source.fetch(entity_type, event.entity_id)
        operation = str(getattr(event, "operation", "updated")).lower()
        if operation == "deleted":
            return self.delete_entity(entity_type, str(event.entity_id))
        return self.project_entity(entity_type, str(event.entity_id))

    def project_record(self, session: Any, *, entity_type: str, entity_id: str, operation: str, record: dict[str, Any] | None = None):
        if self._legacy_registry is None:
            if operation.casefold() == "deleted":
                return self.delete_entity(entity_type, entity_id)
            return self.project_entity(entity_type, entity_id)
        from opticargo_knowledge_graph.contracts import ProjectionResult
        handler = self._legacy_registry.get(entity_type)
        if handler is None:
            return ProjectionResult(entity_type, entity_id, "skipped", "No handler")
        payload = dict(record or {})
        payload["id"] = entity_id
        normalized = operation.casefold()
        if hasattr(session, "execute_write"):
            session.execute_write(handler, payload, normalized)
        else:
            handler(session, payload, normalized)
        return ProjectionResult(entity_type, entity_id, "deleted" if normalized == "deleted" else "projected")

    def build_plan(self, entity_type: str, entity_id: str) -> ProjectionPlan | None:
        spec = get_projection_spec(entity_type)
        row = self._postgres.fetch_one(spec.select_sql, entity_id=entity_id)
        return spec.builder(row) if row is not None else None

    def project_entity(self, entity_type: str, entity_id: str) -> ProjectionOutcome:
        spec = get_projection_spec(entity_type)
        plan = self.build_plan(entity_type, entity_id)
        if plan is None:
            self._neo4j.delete_projection(spec.entity_type, entity_id, spec.label)
            return ProjectionOutcome(spec.entity_type, entity_id, "deleted")
        self._neo4j.apply_projection(plan)
        return ProjectionOutcome(
            spec.entity_type,
            entity_id,
            "projected",
            source_hash=plan.source_hash,
        )

    def delete_entity(self, entity_type: str, entity_id: str) -> ProjectionOutcome:
        spec = get_projection_spec(entity_type)
        self._neo4j.delete_projection(spec.entity_type, entity_id, spec.label)
        return ProjectionOutcome(spec.entity_type, entity_id, "deleted")

    def process_event(self, event: EventEnvelopeView) -> ProjectionOutcome:
        entity_type, entity_id, action = resolve_projection_target(event)
        if action == "deleted":
            return self.delete_entity(entity_type, entity_id)
        return self.project_entity(entity_type, entity_id)
