"""Redis adapter selects the configured database and decoded stream fields."""

from redis import Redis

from opticargo_knowledge_graph.clients.redis_stream import create_redis_client
from opticargo_knowledge_graph.config import GraphSettings


def test_redis_factory_uses_url_and_decode_mode(monkeypatch) -> None:
    calls = []
    sentinel = object()
    monkeypatch.setattr(
        Redis,
        "from_url",
        lambda url, **kwargs: calls.append((url, kwargs)) or sentinel,
    )

    result = create_redis_client(GraphSettings(redis_url="redis://redis:6379/4"))

    assert result is sentinel
    assert calls == [("redis://redis:6379/4", {"decode_responses": True})]
