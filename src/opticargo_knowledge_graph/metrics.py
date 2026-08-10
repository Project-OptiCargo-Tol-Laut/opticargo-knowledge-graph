from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram, start_http_server

GRAPH_EVENTS_TOTAL = Counter(
    "opticargo_graph_events_total",
    "Graph worker events by type and result",
    ["event_type", "result"],
)
GRAPH_EVENT_DURATION = Histogram(
    "opticargo_graph_event_duration_seconds",
    "Graph event processing duration",
    ["event_type"],
)
GRAPH_SYNC_LAG = Gauge(
    "opticargo_graph_sync_lag_seconds",
    "Seconds between event occurrence and successful projection",
)
GRAPH_RETRIES_TOTAL = Counter(
    "opticargo_graph_retries_total",
    "Graph worker retry attempts",
    ["reason"],
)
GRAPH_DLQ_TOTAL = Counter(
    "opticargo_graph_dlq_total",
    "Graph events routed to DLQ",
    ["reason"],
)
GRAPH_PENDING = Gauge(
    "opticargo_graph_pending_entries",
    "Pending Redis Stream entries for graph consumer group",
)
GRAPH_QUERY_TOTAL = Counter(
    "opticargo_graph_query_total",
    "Typed graph queries by name and result",
    ["query_name", "result"],
)
GRAPH_QUERY_DURATION = Histogram(
    "opticargo_graph_query_duration_seconds",
    "Typed graph query duration",
    ["query_name"],
)
GRAPH_RECONCILIATION_TOTAL = Counter(
    "opticargo_graph_reconciliation_total",
    "Graph reconciliation executions",
    ["mode", "result"],
)
GRAPH_RECONCILIATION_DURATION = Histogram(
    "opticargo_graph_reconciliation_duration_seconds",
    "Graph reconciliation duration",
    ["mode"],
)
GRAPH_RECONCILIATION_MISMATCH = Gauge(
    "opticargo_graph_reconciliation_mismatch",
    "Current graph projection mismatches",
    ["entity_type", "kind"],
)
GRAPH_DEPENDENCY_UP = Gauge(
    "opticargo_graph_dependency_up",
    "Dependency health for graph runtime",
    ["dependency"],
)
GRAPH_HEARTBEAT = Gauge(
    "opticargo_graph_worker_last_heartbeat_unixtime",
    "Unix timestamp of the latest graph worker heartbeat",
)
GRAPH_BUILD_INFO = Gauge(
    "opticargo_graph_build_info",
    "Build information",
    ["release", "git_sha", "shared_version"],
)


def start_metrics_server(port: int) -> None:
    start_http_server(port)


# Stable develop metric names retained as compatibility aliases where the final
# runtime metric has the same semantics. No high-cardinality identifiers are labels.
PROJECTION_TOTAL = Counter(
    "opticargo_graph_projection_total",
    "Graph projection outcomes",
    ["entity_type", "outcome"],
)
DEPENDENCY_UP = GRAPH_DEPENDENCY_UP
EVENT_TOTAL = GRAPH_EVENTS_TOTAL
PENDING_BACKLOG = GRAPH_PENDING
QUERY_DURATION_SECONDS = GRAPH_QUERY_DURATION
WORKER_HEARTBEAT_TIMESTAMP = GRAPH_HEARTBEAT

__all__ = [name for name in globals() if name.startswith("GRAPH_")] + [
    "PROJECTION_TOTAL", "DEPENDENCY_UP", "EVENT_TOTAL", "PENDING_BACKLOG",
    "QUERY_DURATION_SECONDS", "WORKER_HEARTBEAT_TIMESTAMP", "start_metrics_server",
]

from collections import Counter as _CompatCounter
from threading import Lock as _CompatLock
class InMemoryMetrics:
    def __init__(self) -> None:
        self._lock = _CompatLock(); self._counters: _CompatCounter[str] = _CompatCounter()
    def inc(self, name: str, amount: int = 1) -> None:
        with self._lock: self._counters[name] += amount
    def snapshot(self) -> dict[str, int]:
        with self._lock: return dict(self._counters)
METRICS = InMemoryMetrics()
def record_projection(entity: str, status: str) -> None:
    entity_label = entity.strip().casefold().replace(" ", "_")[:64] or "unknown"
    status_label = status.strip().casefold().replace(" ", "_")[:64] or "unknown"
    METRICS.inc(f"projection.{entity_label}.{status_label}")
    try: PROJECTION_TOTAL.labels(entity_type=entity_label, result=status_label).inc()
    except Exception: pass
def record_event(event_type: str, outcome: str) -> None:
    event_label = event_type.strip().casefold()[:96] or "unknown"
    outcome_label = outcome.strip().casefold()[:64] or "unknown"
    METRICS.inc(f"event.{event_label}.{outcome_label}")
    try: GRAPH_EVENTS_TOTAL.labels(event_type=event_label, result=outcome_label).inc()
    except Exception: pass
def start_metrics(port: int) -> bool:
    start_metrics_server(port); return True
