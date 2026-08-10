from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    opticargo_environment: str = "development"
    opticargo_release: str = "dev"
    opticargo_git_sha: str = "local"
    opticargo_shared_version: str = "1.0.0"

    database_url: SecretStr
    redis_url: SecretStr
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: SecretStr
    neo4j_database: str = "neo4j"

    event_stream: str = "opticargo:events"
    event_dlq_stream: str = "opticargo:events:dlq"
    graph_consumer_group: str = "graph-sync"
    graph_consumer_name: str = "graph-worker-1"
    graph_supported_event_version: str = "1.0"

    worker_concurrency: int = Field(default=2, ge=1, le=16)
    worker_batch_size: int = Field(default=20, ge=1, le=500)
    worker_block_ms: int = Field(default=5000, ge=100, le=60000)
    worker_max_retries: int = Field(default=5, ge=0, le=20)
    worker_retry_backoff_seconds: float = Field(default=2.0, ge=0.1, le=300)
    worker_pending_idle_ms: int = Field(default=60000, ge=1000)
    worker_metrics_port: int = Field(default=9100, ge=1024, le=65535)
    worker_health_file: Path = Path("/tmp/opticargo-graph-worker-health.json")
    worker_heartbeat_seconds: float = Field(default=10, ge=1, le=300)
    worker_heartbeat_stale_seconds: float = Field(default=45, ge=5, le=1800)

    graph_query_timeout_seconds: float = Field(default=10, gt=0, le=120)
    graph_reconciliation_batch_size: int = Field(default=500, ge=10, le=10000)
    graph_reconciliation_lock_ttl_seconds: int = Field(default=3600, ge=60, le=86400)
    scheduler_lock_key: str = "opticargo:locks:graph-reconciliation"
    graph_schema_name: str = "opticargo-knowledge-graph"
    graph_schema_target_version: int = Field(default=3, ge=1)
    graph_delete_stale: bool = True
    graph_projection_namespace: str = "opticargo:graph"

    log_format: str = "json"
    log_level: str = "INFO"
    correlation_header: str = "X-Correlation-ID"

    @field_validator("opticargo_shared_version")
    @classmethod
    def validate_shared_version(cls, value: str) -> str:
        if value != "1.0.0":
            raise ValueError("opticargo-shared must be locked to 1.0.0")
        return value

    @field_validator("neo4j_uri")
    @classmethod
    def validate_neo4j_uri(cls, value: str) -> str:
        if not value.startswith(("bolt://", "neo4j://", "neo4j+s://", "bolt+s://")):
            raise ValueError("NEO4J_URI must use a Neo4j/Bolt scheme")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]

# Develop-compatible lightweight settings used by query/worker helper APIs.
from dataclasses import dataclass as _dataclass
import os as _os

@_dataclass(frozen=True)
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
    def from_environment(cls):
        return cls(
            neo4j_uri=_os.getenv("NEO4J_URI", cls.neo4j_uri),
            neo4j_user=_os.getenv("NEO4J_USER", cls.neo4j_user),
            neo4j_password=_os.getenv("NEO4J_PASSWORD", cls.neo4j_password),
            redis_url=_os.getenv("REDIS_URL", cls.redis_url),
            neo4j_database=_os.getenv("NEO4J_DATABASE", cls.neo4j_database),
            worker_heartbeat_seconds=int(_os.getenv("WORKER_HEARTBEAT_SECONDS", str(cls.worker_heartbeat_seconds))),
            worker_block_ms=int(_os.getenv("GRAPH_WORKER_BLOCK_MS", str(cls.worker_block_ms))),
            worker_batch_size=int(_os.getenv("GRAPH_WORKER_BATCH_SIZE", str(cls.worker_batch_size))),
            worker_max_attempts=int(_os.getenv("GRAPH_WORKER_MAX_ATTEMPTS", str(cls.worker_max_attempts))),
            worker_pending_idle_ms=int(_os.getenv("GRAPH_WORKER_PENDING_IDLE_MS", str(cls.worker_pending_idle_ms))),
        )
