"""Metrics use bounded labels and preserve deterministic local evidence."""

from opticargo_knowledge_graph.metrics import InMemoryMetrics, record_event, record_projection


def test_in_memory_metrics_and_prometheus_updates_are_safe() -> None:
    metrics = InMemoryMetrics()
    metrics.inc("projection.port.projected")
    metrics.inc("projection.port.projected", 2)
    assert metrics.snapshot() == {"projection.port.projected": 3}

    record_projection("PORT", "PROJECTED")
    record_event("entity.changed", "projected")


def test_metric_functions_do_not_accept_high_cardinality_labels() -> None:
    assert record_projection.__code__.co_argcount == 2
    assert record_event.__code__.co_argcount == 2
