from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any


class RedisStreamClient:
    """Redis Streams, idempotency, retry, and distributed-lock adapter."""

    def __init__(self, redis_url: str, *, client: Any | None = None) -> None:
        self._redis_url = redis_url
        self._client = client

    @property
    def client(self) -> Any:
        if self._client is None:
            from redis import Redis

            self._client = Redis.from_url(self._redis_url, decode_responses=False)
        return self._client

    def ping(self) -> bool:
        return bool(self.client.ping())

    def ensure_group(self, stream: str, group: str) -> None:
        try:
            self.client.xgroup_create(stream, group, id="0-0", mkstream=True)
        except Exception as exc:
            if "BUSYGROUP" not in str(exc):
                raise

    def read_group(
        self,
        *,
        stream: str,
        group: str,
        consumer: str,
        count: int,
        block_ms: int,
    ) -> list[tuple[str, dict[Any, Any]]]:
        result = self.client.xreadgroup(
            group,
            consumer,
            {stream: ">"},
            count=count,
            block=block_ms,
        )
        messages: list[tuple[str, dict[Any, Any]]] = []
        for _stream_name, entries in result:
            for message_id, fields in entries:
                messages.append((self._text(message_id), dict(fields)))
        return messages

    def autoclaim(
        self,
        *,
        stream: str,
        group: str,
        consumer: str,
        min_idle_ms: int,
        count: int,
        start_id: str = "0-0",
    ) -> list[tuple[str, dict[Any, Any]]]:
        result = self.client.xautoclaim(
            stream,
            group,
            consumer,
            min_idle_ms,
            start_id=start_id,
            count=count,
        )
        entries = result[1] if len(result) > 1 else []
        return [(self._text(message_id), dict(fields)) for message_id, fields in entries]

    def ack(self, stream: str, group: str, message_id: str) -> None:
        self.client.xack(stream, group, message_id)

    def pending_count(self, stream: str, group: str) -> int:
        summary = self.client.xpending(stream, group)
        if isinstance(summary, Mapping):
            return int(summary.get("pending", 0))
        return int(summary[0])

    def retry_count(self, namespace: str, event_id: str) -> int:
        value = self.client.get(f"{namespace}:retry:{event_id}")
        return int(value or 0)

    def increment_retry(self, namespace: str, event_id: str, *, ttl_seconds: int = 86400) -> int:
        key = f"{namespace}:retry:{event_id}"
        value = int(self.client.incr(key))
        self.client.expire(key, ttl_seconds)
        return value

    def clear_retry(self, namespace: str, event_id: str) -> None:
        self.client.delete(f"{namespace}:retry:{event_id}")

    def is_processed(self, namespace: str, event_id: str) -> bool:
        return bool(self.client.exists(f"{namespace}:processed:{event_id}"))

    def mark_processed(self, namespace: str, event_id: str, *, ttl_seconds: int = 2592000) -> None:
        self.client.set(f"{namespace}:processed:{event_id}", "1", ex=ttl_seconds)

    def send_dlq(self, stream: str, fields: Mapping[str, Any]) -> str:
        safe = {str(key): self._text(value) for key, value in fields.items()}
        return self._text(self.client.xadd(stream, safe))

    def acquire_lock(self, key: str, token: str, ttl_seconds: int) -> bool:
        return bool(self.client.set(key, token, nx=True, ex=ttl_seconds))

    def refresh_lock(self, key: str, token: str, ttl_seconds: int) -> bool:
        script = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
          return redis.call('expire', KEYS[1], ARGV[2])
        end
        return 0
        """
        return bool(self.client.eval(script, 1, key, token, ttl_seconds))

    def release_lock(self, key: str, token: str) -> bool:
        script = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
          return redis.call('del', KEYS[1])
        end
        return 0
        """
        return bool(self.client.eval(script, 1, key, token))

    def sleep_backoff(self, base_seconds: float, attempt: int) -> None:
        time.sleep(min(base_seconds * (2 ** max(0, attempt - 1)), 300))

    def close(self) -> None:
        if self._client is not None:
            self._client.close()

    @staticmethod
    def _text(value: Any) -> str:
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return str(value)


def create_redis_client(settings=None):
    from redis import Redis
    from opticargo_knowledge_graph.config import GraphSettings
    active = settings or GraphSettings.from_environment()
    return Redis.from_url(active.redis_url, decode_responses=True)
