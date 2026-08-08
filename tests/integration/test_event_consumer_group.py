"""Redis consumer group supports pending ownership, reclaim, ACK, and cleanup."""

import os
from uuid import uuid4

import pytest

from opticargo_knowledge_graph.clients.redis_stream import create_redis_client
from opticargo_knowledge_graph.config import GraphSettings

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_FULL_INTEGRATION") != "1",
    reason="requires explicit disposable Redis runtime",
)


def test_consumer_group_pending_reclaim_and_ack_roundtrip() -> None:
    client = create_redis_client(GraphSettings.from_environment())
    stream = f"opticargo:test:graph:{uuid4()}"
    group = "graph-test"
    try:
        client.xgroup_create(stream, group, id="0", mkstream=True)
        entry_id = client.xadd(stream, {"event": "{}"})
        batches = client.xreadgroup(group, "consumer-a", {stream: ">"}, count=1)
        assert batches[0][1][0][0] == entry_id
        assert client.xpending(stream, group)["pending"] == 1
        reclaimed = client.xautoclaim(stream, group, "consumer-b", 0, "0-0", count=1)
        assert reclaimed[1][0][0] == entry_id
        assert client.xack(stream, group, entry_id) == 1
        assert client.xpending(stream, group)["pending"] == 0
    finally:
        client.delete(stream)
        client.close()
