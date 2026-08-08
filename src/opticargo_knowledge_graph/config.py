"""Environment configuration for the graph worker and query client."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class GraphSettings:
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""
    redis_url: str = "redis://redis:6379/0"
    neo4j_database: str = "neo4j"
    worker_heartbeat_seconds: int = 30
    worker_block_ms: int = 1000
    worker_batch_size: int = 20
    worker_max_attempts: int = 5
    worker_pending_idle_ms: int = 60_000

    @classmethod
    def from_environment(cls) -> GraphSettings:
        return cls(
            neo4j_uri=os.getenv("NEO4J_URI", cls.neo4j_uri),
            neo4j_user=os.getenv("NEO4J_USER", cls.neo4j_user),
            neo4j_password=os.getenv("NEO4J_PASSWORD", cls.neo4j_password),
            redis_url=os.getenv("REDIS_URL", cls.redis_url),
            neo4j_database=os.getenv("NEO4J_DATABASE", cls.neo4j_database),
            worker_heartbeat_seconds=int(
                os.getenv("WORKER_HEARTBEAT_SECONDS", str(cls.worker_heartbeat_seconds))
            ),
            worker_block_ms=int(os.getenv("GRAPH_WORKER_BLOCK_MS", str(cls.worker_block_ms))),
            worker_batch_size=int(os.getenv("GRAPH_WORKER_BATCH_SIZE", str(cls.worker_batch_size))),
            worker_max_attempts=int(
                os.getenv("GRAPH_WORKER_MAX_ATTEMPTS", str(cls.worker_max_attempts))
            ),
            worker_pending_idle_ms=int(
                os.getenv("GRAPH_WORKER_PENDING_IDLE_MS", str(cls.worker_pending_idle_ms))
            ),
        )


__all__ = ["GraphSettings"]
