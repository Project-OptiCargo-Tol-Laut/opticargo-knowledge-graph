import json
from datetime import datetime, timezone
from uuid import uuid4

from opticargo_knowledge_graph.projections import ProjectionRegistry, ProjectionService
from opticargo_knowledge_graph.worker import process_entry


class FakeRedis:
    def __init__(self):
        self.acked = []
        self.dlq = []

    def xack(self, stream, group, entry_id):
        self.acked.append((stream, group, entry_id))

    def xadd(self, stream, fields):
        self.dlq.append((stream, fields))


def _event(event_type: str, entity_type: str = "document") -> str:
    return json.dumps(
        {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "event_version": "1.0",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "producer": "test",
            "entity_type": entity_type,
            "entity_id": str(uuid4()),
            "correlation_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "payload": {},
        }
    )


def test_non_graph_event_is_acknowledged_without_dlq():
    redis = FakeRedis()

    result = process_entry(
        redis,
        stream="events",
        group="graph-sync",
        dlq_stream="dlq",
        entry_id="1-0",
        fields={"event": _event("report.requested")},
        projection_service=ProjectionService(ProjectionRegistry()),
        session_factory=lambda: None,
    )

    assert result == "ignored"
    assert redis.acked == [("events", "graph-sync", "1-0")]
    assert redis.dlq == []


def test_entity_event_without_handler_is_recorded_in_dlq():
    redis = FakeRedis()

    class Session:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

    result = process_entry(
        redis,
        stream="events",
        group="graph-sync",
        dlq_stream="dlq",
        entry_id="2-0",
        fields={"event": _event("entity.changed", "voyage")},
        projection_service=ProjectionService(ProjectionRegistry()),
        session_factory=Session,
    )

    assert result == "skipped"
    assert redis.acked == [("events", "graph-sync", "2-0")]
    assert len(redis.dlq) == 1
