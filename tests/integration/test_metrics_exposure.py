"""Internal Prometheus endpoint exposes graph metrics without sensitive labels."""

import socket
from urllib.request import urlopen

from opticargo_knowledge_graph.metrics import record_event, record_projection, start_metrics


def test_internal_metrics_endpoint_is_scrapeable() -> None:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    assert start_metrics(port)
    record_event("entity.changed", "projected")
    record_projection("port", "projected")

    with urlopen(f"http://127.0.0.1:{port}/metrics", timeout=3) as response:
        payload = response.read().decode("utf-8")
    assert "opticargo_graph_event_total" in payload
    assert "opticargo_graph_projection_total" in payload
    assert "event_id=" not in payload and "entity_id=" not in payload
