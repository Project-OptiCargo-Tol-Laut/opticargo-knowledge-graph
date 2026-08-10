"""A running graph worker drains a controlled harmless burst without pending debt."""

import os
from datetime import UTC, datetime
from time import monotonic, sleep
from uuid import uuid4

import pytest
from opticargo_shared.events import DomainEvent, EventType

from opticargo_knowledge_graph.clients.redis_stream import create_redis_client
from opticargo_knowledge_graph.config import GraphSettings

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_PERFORMANCE") != "1" or os.getenv("OPTICARGO_FULL_INTEGRATION") != "1",
    reason="requires explicit Redis performance runtime and running graph worker",
)


def test_worker_drains_burst_without_pending_debt() -> None:
    client = create_redis_client(GraphSettings.from_environment())
    stream = os.getenv("EVENT_STREAM", "opticargo:events")
    group = os.getenv("GRAPH_CONSUMER_GROUP", "graph-sync")
    burst = int(os.getenv("GRAPH_PERF_BACKLOG_EVENTS", "40"))
    budget_seconds = float(os.getenv("GRAPH_PERF_BACKLOG_SECONDS", "15"))
    marker = f"performance-{uuid4()}"
    entry_ids: list[str] = []
    try:
        baseline = client.xinfo_groups(stream)
        assert any(item["name"] == group for item in baseline), baseline
        for index in range(burst):
            event_id = uuid4()
            envelope = DomainEvent(
                event_id=event_id,
                event_type=EventType.report_requested,
                occurred_at=datetime.now(UTC),
                producer="knowledge-graph-performance-test",
                entity_type="report",
                entity_id=uuid4(),
                correlation_id=uuid4(),
                idempotency_key=f"{marker}:{index}:{event_id}",
                payload={"sequence": index},
            )
            entry_ids.append(client.xadd(stream, {"event": envelope.model_dump_json()}))

        started = monotonic()
        final_group = None
        while monotonic() - started <= budget_seconds:
            final_group = next(
                item for item in client.xinfo_groups(stream) if item["name"] == group
            )
            if int(final_group.get("lag") or 0) == 0 and int(final_group["pending"]) == 0:
                break
            sleep(0.1)

        elapsed = monotonic() - started
        evidence = {
            "burst": burst,
            "elapsed_seconds": elapsed,
            "drain_per_second": burst / max(elapsed, 0.001),
            "group": final_group,
        }
        assert final_group is not None
        assert int(final_group.get("lag") or 0) == 0, evidence
        assert int(final_group["pending"]) == 0, evidence
        assert elapsed <= budget_seconds, evidence
    finally:
        if entry_ids:
            client.xdel(stream, *entry_ids)
        client.close()
