from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from opticargo_knowledge_graph.contracts import EventEnvelopeView
from opticargo_knowledge_graph.errors import ProjectionError, UnsupportedEventError
from opticargo_knowledge_graph.health import WorkerHealth, write_health
from opticargo_knowledge_graph.worker import GraphWorker


class RetryRedis:
    def __init__(self) -> None:
        self.increment_calls = 0
        self.backoff_calls = 0

    def retry_count(self, *_args):
        return 0

    def increment_retry(self, *_args):
        self.increment_calls += 1
        return self.increment_calls

    def sleep_backoff(self, *_args):
        self.backoff_calls += 1


def _event(event_type: str) -> EventEnvelopeView:
    return EventEnvelopeView(
        event_id=str(uuid4()),
        event_type=event_type,
        event_version="1.0",
        occurred_at=datetime.now(UTC),
        producer="test",
        entity_type="report",
        entity_id=str(uuid4()),
        actor_id=None,
        correlation_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        payload={},
    )


def _worker(redis: RetryRedis) -> GraphWorker:
    settings = SimpleNamespace(
        graph_projection_namespace="kg:test",
        worker_max_retries=2,
        worker_retry_backoff_seconds=0.0,
    )
    worker = GraphWorker(settings, object(), object(), redis)
    return worker


def test_unsupported_event_is_not_retried() -> None:
    redis = RetryRedis()
    worker = _worker(redis)
    worker.projection = SimpleNamespace(
        process_event=lambda _event: (_ for _ in ()).throw(
            UnsupportedEventError("event type is not projected: report.requested")
        )
    )

    with pytest.raises(UnsupportedEventError):
        worker._process_with_retry(_event("report.requested"))

    assert redis.increment_calls == 0
    assert redis.backoff_calls == 0


def test_retryable_projection_error_still_retries() -> None:
    redis = RetryRedis()
    worker = _worker(redis)
    calls = 0

    def process(_event):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise ProjectionError("temporary projection failure")

    worker.projection = SimpleNamespace(process_event=process)
    worker._set_state = lambda *_args, **_kwargs: None
    worker.projection.process_event = process
    worker._process_with_retry(_event("entity.changed"))

    assert calls == 2
    assert redis.increment_calls == 1
    assert redis.backoff_calls == 1


def test_health_atomic_write_survives_concurrent_publishers(tmp_path) -> None:
    path = tmp_path / "worker-health.json"

    def publish(index: int) -> None:
        for sequence in range(30):
            write_health(
                path,
                WorkerHealth.now(
                    state=f"worker-{index}",
                    pending_entries=sequence,
                    dependencies={"postgres": True, "neo4j": True, "redis": True},
                ),
            )

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(publish, range(8)))

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["state"].startswith("worker-")
    assert payload["dependencies"] == {"postgres": True, "neo4j": True, "redis": True}
    assert list(tmp_path.glob("*.tmp")) == []
