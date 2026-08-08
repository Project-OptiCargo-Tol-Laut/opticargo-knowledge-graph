"""Worker startup contract declares schema, stream, metrics, heartbeat, and shutdown hooks."""

import inspect

from opticargo_knowledge_graph import worker


def test_worker_startup_contains_required_runtime_gates() -> None:
    source = inspect.getsource(worker.main)
    assert "ensure_consumer_group" in source
    assert "SchemaMigrator" in source
    assert "start_metrics" in source
    assert "write_heartbeat" in source
    assert "driver.close" in source and "redis_client.close" in source
