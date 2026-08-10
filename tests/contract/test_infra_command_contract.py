"""Infra starts the worker/job with heartbeat and internal metrics contracts."""

from tests.helpers import WORKSPACE_ROOT


def test_infra_graph_commands_and_healthcheck_match_package_entrypoints() -> None:
    compose = (WORKSPACE_ROOT / "opticargo-infra" / "docker-compose.yml").read_text(
        encoding="utf-8"
    )
    env = (WORKSPACE_ROOT / "opticargo-infra" / ".env.example").read_text(encoding="utf-8")
    assert "opticargo_knowledge_graph.healthcheck" in compose
    assert "GRAPH_HEARTBEAT_PATH" in compose
    assert "WORKER_METRICS_PORT" in compose
    assert "GRAPH_WORKER_COMMAND=python -m opticargo_knowledge_graph.worker" in env
    assert "GRAPH_RECONCILIATION_COMMAND=python -m opticargo_knowledge_graph.reconcile" in env
