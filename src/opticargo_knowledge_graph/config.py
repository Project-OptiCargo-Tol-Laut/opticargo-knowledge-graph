"""Environment configuration for the graph worker and query client."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class GraphSettings:
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""
    redis_url: str = "redis://redis:6379/0"
    worker_heartbeat_seconds: int = 30

    @classmethod
    def from_environment(cls) -> "GraphSettings":
        return cls(
            neo4j_uri=os.getenv("NEO4J_URI", cls.neo4j_uri),
            neo4j_user=os.getenv("NEO4J_USER", cls.neo4j_user),
            neo4j_password=os.getenv("NEO4J_PASSWORD", cls.neo4j_password),
            redis_url=os.getenv("REDIS_URL", cls.redis_url),
            worker_heartbeat_seconds=int(os.getenv("WORKER_HEARTBEAT_SECONDS", str(cls.worker_heartbeat_seconds))),
        )


__all__ = ["GraphSettings"]
