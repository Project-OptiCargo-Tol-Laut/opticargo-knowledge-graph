"""Healthcheck exits differently for ready and unhealthy heartbeat states."""

import pytest

from opticargo_knowledge_graph import healthcheck
from opticargo_knowledge_graph.health import HealthReport


def test_healthcheck_uses_heartbeat_status(monkeypatch, tmp_path) -> None:
    path = tmp_path / "heartbeat.json"
    monkeypatch.setenv("GRAPH_HEARTBEAT_PATH", str(path))
    monkeypatch.setattr(
        healthcheck,
        "heartbeat_report",
        lambda *args, **kwargs: HealthReport("ready"),
    )
    healthcheck.main()

    monkeypatch.setattr(
        healthcheck,
        "heartbeat_report",
        lambda *args, **kwargs: HealthReport("stale"),
    )
    with pytest.raises(SystemExit) as error:
        healthcheck.main()
    assert error.value.code == 1
