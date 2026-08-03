"""Redis stream client factory."""

from __future__ import annotations

from opticargo_knowledge_graph.config import GraphSettings


def create_redis_client(settings: GraphSettings | None = None):
    from redis import Redis

    active = settings or GraphSettings.from_environment()
    return Redis.from_url(active.redis_url, decode_responses=True)


__all__ = ["create_redis_client"]
