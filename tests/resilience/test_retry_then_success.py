import json
from datetime import UTC, datetime
from uuid import uuid4

from opticargo_knowledge_graph.worker import process_entry


class Redis:
    def __init__(self):
        self.acked = []
        self.dlq = []

    def xack(self, *args):
        self.acked.append(args)

    def xadd(self, stream, fields):
        self.dlq.append((stream, fields))


class FailingService:
    def project(self, session, event):
        raise ConnectionError("neo4j unavailable")


class Session:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def event() -> str:
    return json.dumps(
        {
            "event_id": str(uuid4()),
            "event_type": "entity.changed",
            "event_version": "1.0",
            "occurred_at": datetime.now(UTC).isoformat(),
            "producer": "test",
            "entity_type": "voyage",
            "entity_id": str(uuid4()),
            "correlation_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "payload": {"operation": "updated"},
        }
    )


def test_transient_failure_stays_pending_until_retry_budget_exhausted() -> None:
    redis = Redis()
    arguments = {
        "stream": "events",
        "group": "graph",
        "dlq_stream": "dlq",
        "entry_id": "1-0",
        "fields": {"event": event()},
        "projection_service": FailingService(),
        "session_factory": Session,
        "max_attempts": 3,
    }

    assert process_entry(redis, delivery_attempt=1, **arguments) == "retry"
    assert redis.acked == []
    assert redis.dlq == []

    assert process_entry(redis, delivery_attempt=3, **arguments) == "failed"
    assert len(redis.acked) == 1
    assert len(redis.dlq) == 1
