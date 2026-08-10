from __future__ import annotations

import logging
import os
import signal
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .clients import Neo4jClient, PostgresClient, RedisStreamClient
from .config import Settings, get_settings
from .contracts import EventEnvelopeView, stream_fields_to_dict, validate_domain_event
from .errors import ContractError, KnowledgeGraphError, UnsupportedEventError
from .health import WorkerHealth, WorkerHeartbeat, write_health, write_heartbeat
from .logging import configure_logging, log_event
from .metrics import (
    GRAPH_BUILD_INFO,
    GRAPH_DEPENDENCY_UP,
    GRAPH_DLQ_TOTAL,
    GRAPH_EVENT_DURATION,
    GRAPH_EVENTS_TOTAL,
    GRAPH_HEARTBEAT,
    GRAPH_PENDING,
    GRAPH_RETRIES_TOTAL,
    GRAPH_SYNC_LAG,
    start_metrics_server,
)
from .projections import ProjectionService
from .schema import GraphMigrator

from opticargo_shared.events import EventType

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


class GraphWorker:
    def __init__(
        self,
        settings: Settings,
        postgres: Any,
        neo4j: Any,
        redis: Any,
        *,
        event_validator: Callable[[dict[str, Any]], EventEnvelopeView] = validate_domain_event,
    ) -> None:
        self.settings = settings
        self.postgres = postgres
        self.neo4j = neo4j
        self.redis = redis
        self.event_validator = event_validator
        self.projection = ProjectionService(postgres, neo4j)
        self.logger = logging.getLogger(__name__)
        self.stop_event = threading.Event()
        self._state_lock = threading.Lock()
        self._state = "starting"
        self._last_event_id: str | None = None
        self._last_error: str | None = None
        self._dependencies: dict[str, bool] = {}
        self._active_message_ids: set[str] = set()

    def request_stop(self, *_args: Any) -> None:
        self.stop_event.set()

    def startup(self) -> None:
        self.redis.ensure_group(self.settings.event_stream, self.settings.graph_consumer_group)
        GraphMigrator(
            self.neo4j,
            schema_name=self.settings.graph_schema_name,
            target_version=self.settings.graph_schema_target_version,
        ).migrate()
        self._probe_dependencies(require_all=True)

    def run_forever(self) -> None:
        self.startup()
        monitor = threading.Thread(target=self._monitor_loop, name="graph-monitor", daemon=True)
        monitor.start()
        with ThreadPoolExecutor(
            max_workers=self.settings.worker_concurrency,
            thread_name_prefix="graph-event",
        ) as executor:
            futures: set[Future[None]] = set()
            while not self.stop_event.is_set():
                futures = {future for future in futures if not future.done()}
                capacity = max(0, self.settings.worker_concurrency - len(futures))
                if capacity == 0:
                    time.sleep(0.05)
                    continue
                messages = self.redis.autoclaim(
                    stream=self.settings.event_stream,
                    group=self.settings.graph_consumer_group,
                    consumer=self.settings.graph_consumer_name,
                    min_idle_ms=self.settings.worker_pending_idle_ms,
                    count=min(capacity, self.settings.worker_batch_size),
                )
                if not messages:
                    messages = self.redis.read_group(
                        stream=self.settings.event_stream,
                        group=self.settings.graph_consumer_group,
                        consumer=self.settings.graph_consumer_name,
                        count=min(capacity, self.settings.worker_batch_size),
                        block_ms=self.settings.worker_block_ms,
                    )
                if not messages:
                    self._set_state("idle")
                    continue
                for message_id, fields in messages:
                    if not self._reserve_message(message_id):
                        continue
                    future = executor.submit(self._handle_message, message_id, fields)
                    future.add_done_callback(
                        lambda _future, reserved_id=message_id: self._release_message(reserved_id)
                    )
                    futures.add(future)
            for future in futures:
                future.result()
        self._set_state("stopped")
        monitor.join(timeout=self.settings.worker_heartbeat_seconds + 1)
        self._write_health()

    def _reserve_message(self, message_id: str) -> bool:
        with self._state_lock:
            if message_id in self._active_message_ids:
                return False
            self._active_message_ids.add(message_id)
            return True

    def _release_message(self, message_id: str) -> None:
        with self._state_lock:
            self._active_message_ids.discard(message_id)

    def _handle_message(self, message_id: str, fields: dict[Any, Any]) -> None:
        started = time.perf_counter()
        event: EventEnvelopeView | None = None
        try:
            raw = stream_fields_to_dict(fields)
            event = self.event_validator(raw)
            if event.event_version != self.settings.graph_supported_event_version:
                raise ContractError(
                    f"unsupported event version {event.event_version}; "
                    f"expected {self.settings.graph_supported_event_version}"
                )
            if self.redis.is_processed(self.settings.graph_projection_namespace, event.event_id):
                self._ack_success(message_id, event, "duplicate")
                return
            self._set_state("processing", event_id=event.event_id)
            self._process_with_retry(event)
            self.redis.mark_processed(self.settings.graph_projection_namespace, event.event_id)
            self.redis.clear_retry(self.settings.graph_projection_namespace, event.event_id)
            self._ack_success(message_id, event, "projected")
        except UnsupportedEventError:
            self.redis.ack(
                self.settings.event_stream,
                self.settings.graph_consumer_group,
                message_id,
            )
            if event is not None:
                self.redis.clear_retry(
                    self.settings.graph_projection_namespace,
                    event.event_id,
                )
            GRAPH_EVENTS_TOTAL.labels(
                event_type=event.event_type if event else "unknown",
                result="ignored",
            ).inc()
            self._set_state("idle", event_id=event.event_id if event else None)
            log_event(
                self.logger,
                logging.INFO,
                "graph event ignored",
                event_id=event.event_id if event else None,
                event_type=event.event_type if event else "unknown",
                correlation_id=event.correlation_id if event else None,
                reason="not_projectable",
            )
        except ContractError as exc:
            self._to_dlq(message_id, event, "contract_error", str(exc), fields)
        except Exception as exc:
            self._to_dlq(message_id, event, "processing_error", str(exc), fields)
        finally:
            GRAPH_EVENT_DURATION.labels(
                event_type=event.event_type if event else "unknown"
            ).observe(time.perf_counter() - started)

    def _process_with_retry(self, event: EventEnvelopeView) -> None:
        attempts = self.redis.retry_count(self.settings.graph_projection_namespace, event.event_id)
        while True:
            try:
                self.projection.process_event(event)
                return
            except Exception as exc:
                # Valid-but-irrelevant events and other non-retryable domain errors
                # must never consume the retry budget. They are handled by the
                # outer worker boundary (ignored/ACK or DLQ as appropriate).
                if isinstance(exc, KnowledgeGraphError) and not exc.retryable:
                    raise
                attempts = self.redis.increment_retry(
                    self.settings.graph_projection_namespace,
                    event.event_id,
                )
                GRAPH_RETRIES_TOTAL.labels(reason=type(exc).__name__).inc()
                if attempts > self.settings.worker_max_retries:
                    raise
                self._set_state("retrying", event_id=event.event_id, error=str(exc))
                log_event(
                    self.logger,
                    logging.WARNING,
                    "graph event retry scheduled",
                    event_id=event.event_id,
                    event_type=event.event_type,
                    correlation_id=event.correlation_id,
                    attempt=attempts,
                    error=str(exc),
                )
                self.redis.sleep_backoff(
                    self.settings.worker_retry_backoff_seconds,
                    attempts,
                )

    def _ack_success(self, message_id: str, event: EventEnvelopeView, result: str) -> None:
        self.redis.ack(
            self.settings.event_stream,
            self.settings.graph_consumer_group,
            message_id,
        )
        lag = max(0.0, (datetime.now(UTC) - event.occurred_at.astimezone(UTC)).total_seconds())
        GRAPH_SYNC_LAG.set(lag)
        GRAPH_EVENTS_TOTAL.labels(event_type=event.event_type, result=result).inc()
        self._set_state("idle", event_id=event.event_id)
        log_event(
            self.logger,
            logging.INFO,
            "graph event processed",
            event_id=event.event_id,
            event_type=event.event_type,
            entity_id=event.entity_id,
            correlation_id=event.correlation_id,
            result=result,
            sync_lag_seconds=lag,
        )

    def _to_dlq(
        self,
        message_id: str,
        event: EventEnvelopeView | None,
        reason: str,
        error: str,
        fields: dict[Any, Any],
    ) -> None:
        event_id = event.event_id if event else str(message_id)
        self.redis.send_dlq(
            self.settings.event_dlq_stream,
            {
                "source_stream": self.settings.event_stream,
                "source_message_id": message_id,
                "consumer_group": self.settings.graph_consumer_group,
                "failed_by": self.settings.graph_consumer_name,
                "event_id": event_id,
                "event_type": event.event_type if event else "unknown",
                "failure_code": reason,
                "failure_message": error[:1000],
                "original_field_count": len(fields),
            },
        )
        self.redis.ack(
            self.settings.event_stream,
            self.settings.graph_consumer_group,
            message_id,
        )
        GRAPH_DLQ_TOTAL.labels(reason=reason).inc()
        GRAPH_EVENTS_TOTAL.labels(
            event_type=event.event_type if event else "unknown",
            result="dlq",
        ).inc()
        self._set_state("idle", event_id=event_id, error=error)
        log_event(
            self.logger,
            logging.ERROR,
            "graph event routed to DLQ",
            event_id=event_id,
            event_type=event.event_type if event else "unknown",
            correlation_id=event.correlation_id if event else None,
            reason=reason,
            error=error,
        )

    def _probe_dependencies(self, *, require_all: bool = False) -> dict[str, bool]:
        checks = {
            "postgres": self.postgres.ping,
            "neo4j": self.neo4j.ping,
            "redis": self.redis.ping,
        }
        dependencies: dict[str, bool] = {}
        for name, check in checks.items():
            try:
                dependencies[name] = bool(check())
            except Exception:
                dependencies[name] = False
            GRAPH_DEPENDENCY_UP.labels(dependency=name).set(int(dependencies[name]))
        with self._state_lock:
            self._dependencies = dependencies
        if require_all and not all(dependencies.values()):
            unavailable = sorted(name for name, available in dependencies.items() if not available)
            raise RuntimeError(f"graph worker dependencies unavailable: {', '.join(unavailable)}")
        return dependencies

    def _monitor_loop(self) -> None:
        while not self.stop_event.wait(self.settings.worker_heartbeat_seconds):
            try:
                pending = self.redis.pending_count(
                    self.settings.event_stream,
                    self.settings.graph_consumer_group,
                )
            except Exception:
                pending = -1
            GRAPH_PENDING.set(max(0, pending))
            GRAPH_HEARTBEAT.set(time.time())
            self._probe_dependencies()
            self._write_health(pending_entries=max(0, pending))

    def _set_state(
        self,
        state: str,
        *,
        event_id: str | None = None,
        error: str | None = None,
    ) -> None:
        with self._state_lock:
            self._state = state
            if event_id is not None:
                self._last_event_id = event_id
            self._last_error = error
        self._write_health()

    def _write_health(self, pending_entries: int = 0) -> None:
        with self._state_lock:
            health = WorkerHealth.now(
                state=self._state,
                dependencies=dict(self._dependencies),
                pending_entries=pending_entries,
                last_event_id=self._last_event_id,
                last_error=self._last_error,
                release=self.settings.opticargo_release,
                git_sha=self.settings.opticargo_git_sha,
            )
        write_health(self.settings.worker_health_file, health)

        # Preserve the develop heartbeat contract when infra explicitly asks for
        # it, while keeping the final structured health file as the canonical
        # runtime health source. This lets old healthcheck callers coexist with
        # the final worker without changing the projection/runtime path.
        legacy_path = os.getenv("GRAPH_HEARTBEAT_PATH")
        if legacy_path:
            dependencies = {
                name: "ready" if available else "degraded"
                for name, available in health.dependencies.items()
            }
            legacy_state = (
                "ready"
                if health.dependencies and all(health.dependencies.values())
                else "degraded"
            )
            write_heartbeat(
                Path(legacy_path),
                WorkerHeartbeat(
                    state=legacy_state,
                    timestamp=datetime.now(UTC),
                    release=health.release,
                    dependencies=dependencies,
                    pending_count=health.pending_entries,
                    last_event_ref=health.last_event_id,
                    last_error=health.last_error,
                ),
            )


def create_runtime(settings: Settings) -> tuple[GraphWorker, PostgresClient, Neo4jClient, RedisStreamClient]:
    postgres = PostgresClient(settings.database_url.get_secret_value())
    neo4j = Neo4jClient(
        settings.neo4j_uri,
        settings.neo4j_user,
        settings.neo4j_password.get_secret_value(),
        database=settings.neo4j_database,
        query_timeout_seconds=settings.graph_query_timeout_seconds,
    )
    redis = RedisStreamClient(settings.redis_url.get_secret_value())
    return GraphWorker(settings, postgres, neo4j, redis), postgres, neo4j, redis


def run() -> None:
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_format)
    start_metrics_server(settings.worker_metrics_port)
    GRAPH_BUILD_INFO.labels(
        release=settings.opticargo_release,
        git_sha=settings.opticargo_git_sha,
        shared_version=settings.opticargo_shared_version,
    ).set(1)
    worker, postgres, neo4j, redis = create_runtime(settings)
    signal.signal(signal.SIGTERM, worker.request_stop)
    signal.signal(signal.SIGINT, worker.request_stop)
    try:
        worker.run_forever()
    finally:
        postgres.close()
        neo4j.close()
        redis.close()


if __name__ == "__main__":
    run()

# Sync develop worker entrypoint retained for tests/tools; final GraphWorker remains production runtime.
from opticargo_knowledge_graph.compat.worker import process_entry, reclaim_pending, run_once
