"""Heartbeat and metrics expose required safe fields with bounded labels."""

from datetime import UTC, datetime

from opticargo_knowledge_graph.health import WorkerHeartbeat
from opticargo_knowledge_graph.metrics import (
    DEPENDENCY_UP,
    EVENT_TOTAL,
    PENDING_BACKLOG,
    PROJECTION_TOTAL,
    QUERY_DURATION_SECONDS,
    WORKER_HEARTBEAT_TIMESTAMP,
)


def test_health_payload_and_metric_names_match_observability_contract() -> None:
    heartbeat = WorkerHeartbeat(
        state="ready",
        timestamp=datetime.now(UTC),
        release="0.1.0",
        dependencies={"neo4j": "ready", "postgres": "ready", "redis": "ready"},
        pending_count=0,
    ).to_dict()
    assert set(heartbeat) == {
        "state",
        "timestamp",
        "release",
        "dependencies",
        "pending_count",
        "last_event_ref",
        "last_error",
    }
    metrics = (
        DEPENDENCY_UP,
        EVENT_TOTAL,
        PENDING_BACKLOG,
        PROJECTION_TOTAL,
        QUERY_DURATION_SECONDS,
        WORKER_HEARTBEAT_TIMESTAMP,
    )
    assert all(metric._name.startswith("opticargo_graph_") for metric in metrics)
    assert "event_id" not in EVENT_TOTAL._labelnames
    assert "entity_id" not in PROJECTION_TOTAL._labelnames
