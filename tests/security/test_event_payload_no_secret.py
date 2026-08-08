"""Untrusted event snapshots cannot inject secret properties into projections."""

from datetime import UTC, datetime

from opticargo_knowledge_graph.contracts import EntityChangedEvent
from opticargo_knowledge_graph.projections import ProjectionRegistry, ProjectionService
from tests.unit.projections.test_service import Session, Transaction


def test_projection_uses_canonical_source_instead_of_secret_event_payload() -> None:
    captured = []
    registry = ProjectionRegistry()
    registry.register("port", lambda tx, record, operation: captured.append(record))

    class Source:
        def fetch(self, entity_type, entity_id):
            return {"id": entity_id, "name": "Safe Port"}

    event = EntityChangedEvent(
        "evt-secret",
        "port",
        "port-1",
        "updated",
        {"password_hash": "should-never-project", "object_key": "private/key"},
        datetime.now(UTC),
    )
    result = ProjectionService(registry, Source()).project(Session(Transaction()), event)

    assert result.status == "projected"
    assert captured == [{"id": "port-1", "name": "Safe Port"}]
