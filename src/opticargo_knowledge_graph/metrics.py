"""Bounded-cardinality Prometheus metrics plus deterministic test snapshots."""

from __future__ import annotations

from collections import Counter as MemoryCounter
from threading import Lock

from prometheus_client import Counter, Gauge, Histogram, start_http_server

PROJECTION_TOTAL = Counter(
    "opticargo_graph_projection_total",
    "Graph projection outcomes.",
    ("entity_type", "outcome"),
)
EVENT_TOTAL = Counter(
    "opticargo_graph_event_total",
    "Redis Stream event processing outcomes.",
    ("event_type", "outcome"),
)
QUERY_DURATION_SECONDS = Histogram(
    "opticargo_graph_query_duration_seconds",
    "Typed graph query execution duration.",
    ("query_name", "outcome"),
)
RECONCILIATION_DURATION_SECONDS = Histogram(
    "opticargo_graph_reconciliation_duration_seconds",
    "Reconciliation execution duration.",
    ("mode", "outcome"),
)
RECONCILIATION_DRIFT = Gauge(
    "opticargo_graph_reconciliation_drift",
    "Latest reconciliation drift count.",
    ("entity_type", "kind"),
)
WORKER_HEARTBEAT_TIMESTAMP = Gauge(
    "opticargo_graph_worker_heartbeat_timestamp_seconds",
    "Unix timestamp of the latest worker heartbeat.",
)
DEPENDENCY_UP = Gauge(
    "opticargo_graph_dependency_up",
    "Dependency readiness (1 ready, 0 unavailable).",
    ("dependency",),
)
PENDING_BACKLOG = Gauge(
    "opticargo_graph_pending_backlog",
    "Redis Stream pending messages for the graph consumer group.",
)


class InMemoryMetrics:
    """Thread-safe evidence store used without scraping global Prometheus state."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: MemoryCounter[str] = MemoryCounter()

    def inc(self, name: str, amount: int = 1) -> None:
        with self._lock:
            self._counters[name] += amount

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return dict(self._counters)


METRICS = InMemoryMetrics()
_SERVER_LOCK = Lock()
_SERVER_STARTED = False


def start_metrics(port: int) -> bool:
    """Start the internal scrape endpoint once per process."""
    global _SERVER_STARTED
    with _SERVER_LOCK:
        if _SERVER_STARTED:
            return False
        start_http_server(max(1, int(port)))
        _SERVER_STARTED = True
        return True


def record_projection(entity: str, status: str) -> None:
    normalized_entity = entity.casefold()
    normalized_status = status.casefold()
    METRICS.inc(f"projection.{normalized_entity}.{normalized_status}")
    PROJECTION_TOTAL.labels(entity_type=normalized_entity, outcome=normalized_status).inc()


def record_event(event_type: str, outcome: str) -> None:
    EVENT_TOTAL.labels(event_type=event_type, outcome=outcome).inc()


__all__ = [
    "DEPENDENCY_UP",
    "EVENT_TOTAL",
    "METRICS",
    "PENDING_BACKLOG",
    "PROJECTION_TOTAL",
    "QUERY_DURATION_SECONDS",
    "RECONCILIATION_DRIFT",
    "RECONCILIATION_DURATION_SECONDS",
    "WORKER_HEARTBEAT_TIMESTAMP",
    "InMemoryMetrics",
    "record_event",
    "record_projection",
    "start_metrics",
]
