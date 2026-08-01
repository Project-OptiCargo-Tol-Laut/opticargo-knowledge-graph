# Architecture Decision Records

ADR diperlukan untuk keputusan yang memengaruhi contract, schema, data boundary, runtime, recovery, atau consumer.

ADR awal yang disarankan:

- PostgreSQL source of truth dan Neo4j derived projection.
- Redis Streams + canonical lookup + ACK/retry/DLQ.
- Canonical graph schema/property allowlist/relationship ownership.
- Versioned migration dan rebuild-oriented rollback.
- Typed query package, no public API, read-only query boundary.
- Reconciliation lock/stale cleanup/full rebuild.
- Metrics/health/log contract.
- Full-text index decision.

Gunakan `0000-template.md`. Status: proposed, accepted, superseded, rejected.
