"""Publish a safe entity.changed event for graph-worker runtime smoke tests."""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from uuid import UUID, uuid4

import redis
from opticargo_shared.events import DomainEvent, EventType


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "entity_type",
        choices=("port", "ship", "commodity", "route", "voyage", "supplier"),
    )
    parser.add_argument("entity_id", type=UUID)
    parser.add_argument("--copies", type=int, default=2)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    copies = max(1, min(args.copies, 10))
    event_id = uuid4()
    event = DomainEvent(
        event_id=event_id,
        event_type=EventType.entity_changed,
        occurred_at=datetime.now(UTC),
        producer="knowledge-graph-runtime-smoke",
        entity_type=args.entity_type,
        entity_id=args.entity_id,
        correlation_id=uuid4(),
        idempotency_key=f"graph-smoke:{event_id}",
        payload={"operation": "updated"},
    )
    client = redis.Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    try:
        stream = os.getenv("EVENT_STREAM", "opticargo:events")
        entries = [client.xadd(stream, {"event": event.model_dump_json()}) for _ in range(copies)]
        print(json.dumps({"event_id": str(event_id), "stream_entries": entries}))
    finally:
        client.close()


if __name__ == "__main__":
    main()
