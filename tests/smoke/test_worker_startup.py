"""Worker startup contract declares schema, stream, metrics, health, and shutdown hooks."""

import inspect

from opticargo_knowledge_graph import worker


def test_worker_startup_contains_required_runtime_gates() -> None:
    startup_source = inspect.getsource(worker.GraphWorker.startup)
    run_source = inspect.getsource(worker.run)

    assert "ensure_group" in startup_source
    assert "GraphMigrator" in startup_source
    assert "_probe_dependencies(require_all=True)" in startup_source

    assert "start_metrics_server" in run_source
    assert "signal.signal" in run_source
    assert "worker.run_forever" in run_source
    assert "postgres.close" in run_source
    assert "neo4j.close" in run_source
    assert "redis.close" in run_source
