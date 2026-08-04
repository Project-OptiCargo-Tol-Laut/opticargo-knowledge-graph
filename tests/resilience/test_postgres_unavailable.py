"""Canonical-source outage leaves the stream entry pending for bounded retry."""

from opticargo_knowledge_graph.projections import ProjectionRegistry, ProjectionService
from opticargo_knowledge_graph.worker import process_entry
from tests.unit.projections.test_service import Session, Transaction
from tests.unit.test_worker import FakeRedis, _event


def test_postgres_failure_is_retryable_and_not_acked() -> None:
    registry = ProjectionRegistry()
    registry.register("port", lambda tx, record, operation: None)

    class Source:
        def fetch(self, entity_type, entity_id):
            raise ConnectionError("postgres unavailable")

    redis = FakeRedis()
    result = process_entry(
        redis,
        stream="events",
        group="graph",
        dlq_stream="dlq",
        entry_id="1-0",
        fields={"event": _event("entity.changed", "port")},
        projection_service=ProjectionService(registry, Source()),
        session_factory=lambda: Session(Transaction()),
        delivery_attempt=1,
        max_attempts=3,
    )
    assert result == "retry"
    assert redis.acked == [] and redis.dlq == []
