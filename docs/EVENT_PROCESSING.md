# Event Processing

## Input contract

Envelope minimum: event ID/type/version/time, producer, entity type/ID, actor optional, correlation ID, idempotency key, payload.

Event minimum yang relevan dari rancangan:

- `entity.changed`
- `booking.created`, `booking.status_changed`
- `payment.created`, `payment.status_changed`
- `document.uploaded`, `document.ingestion_completed`, `document.ingestion_failed`
- `recommendation.created`
- `review.created`

## Redis Streams

- Consumer group: contract Infra menetapkan `graph-sync` sebagai default.
- New message dibaca dengan group ID `>`.
- Pending message direclaim setelah idle threshold.
- ACK hanya setelah success, duplicate, ignored yang sah, atau DLQ berhasil dibuat.

## Idempotency dan retry

- Processed key berdasarkan event ID; TTL/persistence policy harus disetujui.
- Mutation Neo4j tetap idempotent walau processed key hilang.
- Transient failure memakai bounded exponential backoff.
- Contract/permanent failure atau retry exhaustion masuk DLQ sanitized.
- Unknown event version tidak diproses secara spekulatif.

## DLQ minimum

Event reference, source stream/message ID, event type/version/entity reference bila dapat dibaca, failure class, sanitized message, occurred/failed time, retry count, correlation ID. Raw secret atau full canonical row dilarang.
