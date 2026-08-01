# Critical Test Case Catalog

## Projection

- Create/update/delete setiap canonical entity.
- Foreign-key change mengganti owned relationship tanpa edge stale.
- Target placeholder kemudian canonical projection.
- Duplicate event dan replay event lama.
- Sensitive field tidak menjadi property.

## Event processing

- Valid, malformed payload, unsupported version, irrelevant event.
- Transient failure success setelah retry.
- Retry exhausted to sanitized DLQ.
- Pending reclaim dan restart before/after Neo4j commit/ACK.

## Reconciliation

- Missing, property mismatch, relationship mismatch, stale.
- Check-only no mutation.
- Repair no duplicate.
- Lock contention/expiry/owner release.
- Full rebuild dari PostgreSQL.

## Query

- Match dan no-match.
- Capacity weight/volume, cargo compatibility, certification, location/time.
- Path 0/1/max/no path dan invalid hop.
- Missing coordinates.
- Analytics no double count.

## Operations

- Migration repeat/partial failure/target mismatch.
- Stale heartbeat/dependency down.
- Metrics scrape/alert inputs.
- Backup/rebuild/rollback rehearsal.
