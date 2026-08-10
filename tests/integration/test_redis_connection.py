"""Redis runtime authenticates, selects the configured DB, and cleans test keys."""

import os
from uuid import uuid4

import pytest

from opticargo_knowledge_graph.clients.redis_stream import create_redis_client
from opticargo_knowledge_graph.config import GraphSettings

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_FULL_INTEGRATION") != "1",
    reason="requires explicit disposable Redis runtime",
)


def test_redis_ping_set_get_and_cleanup() -> None:
    client = create_redis_client(GraphSettings.from_environment())
    key = f"opticargo:test:graph:{uuid4()}"
    try:
        assert client.ping()
        assert client.set(key, "ready", ex=30)
        assert client.get(key) == "ready"
    finally:
        client.delete(key)
        client.close()
