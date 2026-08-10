"""Permanent contract failure is sanitized into DLQ before source ACK."""

import json

from opticargo_knowledge_graph.projections import ProjectionRegistry, ProjectionService
from opticargo_knowledge_graph.worker import process_entry
from tests.unit.test_worker import FakeRedis


def test_invalid_envelope_dlq_does_not_copy_sensitive_payload() -> None:
    redis = FakeRedis()
    raw = json.dumps({"event_id": "bad", "payload": {"password": "secret"}})
    result = process_entry(
        redis,
        stream="events",
        group="graph",
        dlq_stream="dlq",
        entry_id="1-0",
        fields={"event": raw},
        projection_service=ProjectionService(ProjectionRegistry()),
        session_factory=lambda: None,
    )

    assert result == "invalid"
    assert redis.acked == [("events", "graph", "1-0")]
    assert len(redis.dlq) == 1
    dlq_fields = redis.dlq[0][1]
    assert "secret" not in json.dumps(dlq_fields)
    assert dlq_fields["source_entry_id"] == "1-0"
