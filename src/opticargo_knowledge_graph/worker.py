from __future__ import annotations

import json
import os
import signal
import socket
import time
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from opticargo_shared.events import EVENT_VERSION, DomainEvent, EventType

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.clients.postgres import PostgresProjectionSource
from opticargo_knowledge_graph.clients.redis_stream import create_redis_client
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.contracts import EntityChangedEvent
from opticargo_knowledge_graph.health import WorkerHeartbeat, write_heartbeat
from opticargo_knowledge_graph.logging import configure_logging, get_logger, log_event
from opticargo_knowledge_graph.metrics import (
    DEPENDENCY_UP,
    PENDING_BACKLOG,
    WORKER_HEARTBEAT_TIMESTAMP,
    record_event,
    start_metrics,
)
from opticargo_knowledge_graph.projections import (
    ProjectionService,
    default_projection_registry,
)
from opticargo_knowledge_graph.schema import SchemaMigrator
from opticargo_knowledge_graph.version import __version__

_shutdown = False
LOGGER = get_logger()

PROJECTABLE_EVENT_TYPES: dict[EventType, tuple[str | None, str]] = {
    EventType.entity_changed: (None, "updated"),
    EventType.booking_created: ("booking", "created"),
    EventType.booking_status_changed: ("booking", "updated"),
    EventType.payment_created: ("payment", "created"),
    EventType.payment_status_changed: ("payment", "updated"),
    EventType.document_uploaded: ("document", "created"),
    EventType.document_ingestion_completed: ("document", "updated"),
    EventType.document_ingestion_failed: ("document", "updated"),
    EventType.recommendation_created: ("recommendation", "created"),
    EventType.review_created: ("review", "created"),
}


def _handle_shutdown(signum, frame):
    global _shutdown
    _ = (signum, frame)
    _shutdown = True


def ensure_consumer_group(redis_client, stream: str, group: str) -> None:
    try:
        redis_client.xgroup_create(stream, group, id="0", mkstream=True)
    except Exception as exc:
        if "BUSYGROUP" not in str(exc):
            raise


def process_entry(
    redis_client,
    *,
    stream: str,
    group: str,
    dlq_stream: str,
    entry_id: str,
    fields: dict[str, Any],
    projection_service: ProjectionService,
    session_factory: Callable[[], Any],
    max_attempts: int = 5,
    delivery_attempt: int | None = None,
) -> str:
    raw_event = fields.get("event") or fields.get("data")
    if not raw_event:
        _publish_dlq(redis_client, dlq_stream, "", "event envelope is missing", entry_id)
        redis_client.xack(stream, group, entry_id)
        record_event("invalid", "invalid")
        return "invalid"

    event_json = raw_event if isinstance(raw_event, str) else json.dumps(raw_event)
    try:
        event = DomainEvent.model_validate_json(event_json)
    except Exception as exc:  # noqa: BLE001 - projection dependencies have varied errors
        _publish_dlq(
            redis_client,
            dlq_stream,
            event_json,
            f"invalid event envelope: {exc.__class__.__name__}",
            entry_id,
        )
        redis_client.xack(stream, group, entry_id)
        record_event("invalid", "invalid")
        return "invalid"

    if event.event_version != EVENT_VERSION:
        _publish_dlq(
            redis_client,
            dlq_stream,
            event_json,
            f"unsupported event version: {event.event_version}",
            entry_id,
        )
        redis_client.xack(stream, group, entry_id)
        record_event(str(event.event_type), "invalid")
        return "invalid"

    mapping = PROJECTABLE_EVENT_TYPES.get(event.event_type)
    if mapping is None:
        redis_client.xack(stream, group, entry_id)
        record_event(str(event.event_type), "ignored")
        return "ignored"

    mapped_entity_type, default_operation = mapping
    operation = str(
        event.payload.get("change_type")
        or event.payload.get("operation")
        or default_operation
    )

    changed = EntityChangedEvent(
        event_id=str(event.event_id),
        entity_type=mapped_entity_type or event.entity_type,
        entity_id=str(event.entity_id),
        operation=operation,
        payload=dict(event.payload),
        occurred_at=event.occurred_at,
    )
    try:
        with session_factory() as session:
            result = projection_service.project(session, changed)
        if result.status == "skipped":
            _publish_dlq(
                redis_client,
                dlq_stream,
                event_json,
                result.detail or "projection was skipped",
                entry_id,
            )
            status = "skipped"
        else:
            status = result.status
    except Exception as exc:  # noqa: BLE001
        attempt = delivery_attempt or _delivery_attempts(
            redis_client, stream=stream, group=group, entry_id=entry_id
        )
        if attempt < max(1, max_attempts):
            log_event(
                LOGGER,
                "projection_retry",
                entry_id=entry_id,
                attempt=attempt,
                error_type=exc.__class__.__name__,
            )
            record_event(str(event.event_type), "retry")
            return "retry"
        _publish_dlq(
            redis_client,
            dlq_stream,
            event_json,
            f"projection failed after {attempt} attempts: {exc.__class__.__name__}",
            entry_id,
        )
        status = "failed"

    redis_client.xack(stream, group, entry_id)
    record_event(str(event.event_type), status)
    return status


def _delivery_attempts(redis_client, *, stream: str, group: str, entry_id: str) -> int:
    pending = redis_client.xpending_range(stream, group, entry_id, entry_id, 1)
    if not pending:
        return 1
    row = pending[0]
    if isinstance(row, dict):
        return int(row.get("times_delivered") or row.get("delivery_count") or 1)
    return int(getattr(row, "times_delivered", 1))


def reclaim_pending(
    redis_client,
    *,
    stream: str,
    group: str,
    consumer: str,
    min_idle_ms: int,
    count: int,
) -> list[tuple[str, dict[str, Any]]]:
    response = redis_client.xautoclaim(
        stream,
        group,
        consumer,
        min_idle_ms,
        "0-0",
        count=count,
    )
    if not response or len(response) < 2:
        return []
    return list(response[1])


def run_once(
    redis_client,
    *,
    stream: str,
    group: str,
    consumer: str,
    dlq_stream: str,
    projection_service: ProjectionService,
    session_factory: Callable[[], Any],
    block_ms: int = 1000,
    count: int = 20,
    pending_idle_ms: int = 60_000,
    max_attempts: int = 5,
) -> dict[str, int]:
    reclaimed = reclaim_pending(
        redis_client,
        stream=stream,
        group=group,
        consumer=consumer,
        min_idle_ms=pending_idle_ms,
        count=count,
    )
    batches = redis_client.xreadgroup(
        group,
        consumer,
        {stream: ">"},
        count=count,
        block=block_ms,
    )
    entries_to_process = list(reclaimed)
    seen = {entry_id for entry_id, _ in reclaimed}
    for _, entries in batches:
        entries_to_process.extend(
            (entry_id, fields) for entry_id, fields in entries if entry_id not in seen
        )
    outcomes: dict[str, int] = {}
    for entry_id, fields in entries_to_process:
        status = process_entry(
            redis_client,
            stream=stream,
            group=group,
            dlq_stream=dlq_stream,
            entry_id=entry_id,
            fields=fields,
            projection_service=projection_service,
            session_factory=session_factory,
            max_attempts=max_attempts,
        )
        outcomes[status] = outcomes.get(status, 0) + 1
    return outcomes


def _publish_dlq(
    redis_client,
    dlq_stream: str,
    event_json: str,
    reason: str,
    entry_id: str,
) -> None:
    safe_event: dict[str, Any] = {}
    try:
        decoded = json.loads(event_json)
        if isinstance(decoded, dict):
            for key in (
                "event_id",
                "event_type",
                "event_version",
                "producer",
                "entity_type",
                "entity_id",
                "correlation_id",
                "occurred_at",
            ):
                if key in decoded:
                    safe_event[key] = decoded[key]
    except (json.JSONDecodeError, TypeError):
        pass
    redis_client.xadd(
        dlq_stream,
        {
            "event": json.dumps(safe_event, sort_keys=True),
            "reason": reason,
            "source_entry_id": entry_id,
            "failed_at": datetime.now(timezone.utc).isoformat(),
        },
    )


def main() -> None:
    configure_logging()
    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)

    settings = GraphSettings.from_environment()
    stream = os.getenv("EVENT_STREAM", "opticargo:events")
    group = os.getenv("GRAPH_CONSUMER_GROUP", "graph-sync")
    dlq_stream = os.getenv("EVENT_DLQ_STREAM", "opticargo:events:dlq")
    consumer = f"graph-{socket.gethostname()}-{os.getpid()}"
    heartbeat_seconds = max(1, settings.worker_heartbeat_seconds)
    heartbeat_path = Path(os.getenv("GRAPH_HEARTBEAT_PATH", "/tmp/opticargo-graph-heartbeat.json"))
    start_metrics(int(os.getenv("WORKER_METRICS_PORT", "9100")))
    redis_client = create_redis_client(settings)
    driver = create_neo4j_driver(settings)
    projection_service = ProjectionService(
        default_projection_registry(),
        PostgresProjectionSource(),
    )

    ensure_consumer_group(redis_client, stream, group)
    driver.verify_connectivity()
    DEPENDENCY_UP.labels(dependency="redis").set(1)
    DEPENDENCY_UP.labels(dependency="neo4j").set(1)
    DEPENDENCY_UP.labels(dependency="postgres").set(1)
    with driver.session(database=settings.neo4j_database) as migration_session:
        migration_report = SchemaMigrator(migration_session).apply()
    log_event(
        LOGGER,
        "worker_started",
        consumer=consumer,
        schema_version=migration_report.current_version,
        migrations_applied=migration_report.applied,
    )
    last_heartbeat = 0.0

    def session_factory():
        return driver.session(database=settings.neo4j_database)

    try:
        while not _shutdown:
            try:
                outcomes = run_once(
                    redis_client,
                    stream=stream,
                    group=group,
                    consumer=consumer,
                    dlq_stream=dlq_stream,
                    projection_service=projection_service,
                    session_factory=session_factory,
                    block_ms=max(1, settings.worker_block_ms),
                    count=max(1, settings.worker_batch_size),
                    pending_idle_ms=max(1, settings.worker_pending_idle_ms),
                    max_attempts=max(1, settings.worker_max_attempts),
                )
                if outcomes:
                    log_event(LOGGER, "worker_batch", outcomes=outcomes)
            except Exception as exc:  # noqa: BLE001 - long-running worker retry boundary
                log_event(LOGGER, "worker_loop_retry", error_type=exc.__class__.__name__)
                time.sleep(1)
            now = time.monotonic()
            if now - last_heartbeat >= heartbeat_seconds:
                pending = redis_client.xpending(stream, group)
                pending_count = int(
                    pending.get("pending", 0) if isinstance(pending, dict) else pending[0]
                )
                timestamp = datetime.now(timezone.utc)
                PENDING_BACKLOG.set(pending_count)
                WORKER_HEARTBEAT_TIMESTAMP.set(timestamp.timestamp())
                write_heartbeat(
                    heartbeat_path,
                    WorkerHeartbeat(
                        state="ready",
                        timestamp=timestamp,
                        release=__version__,
                        dependencies={
                            "neo4j": "ready",
                            "postgres": "ready",
                            "redis": "ready",
                        },
                        pending_count=pending_count,
                    ),
                )
                log_event(LOGGER, "worker_heartbeat", consumer=consumer)
                last_heartbeat = now
    finally:
        driver.close()
        redis_client.close()
        log_event(LOGGER, "worker_stopped", consumer=consumer)


if __name__ == "__main__":
    main()
