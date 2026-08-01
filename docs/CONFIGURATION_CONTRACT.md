# Configuration Contract

## Groups

- Build identity: environment, release, git SHA, Shared version.
- PostgreSQL: read-only URL, pool/timeout if needed.
- Redis: URL, event/DLQ stream, group/consumer, retry/idempotency/lock namespace.
- Neo4j: URI, user/password, database, query timeout.
- Worker: concurrency, batch, block, retry, pending idle, heartbeat, health file, metrics port.
- Reconciliation: batch, lock TTL/key, stale policy.
- Schema: name and target version.
- Observability: log format/level, correlation header.

## Validation

- Missing required setting fails before consumer starts.
- URI scheme dan internal hostname divalidasi.
- Port/range/concurrency/batch/timeout bound eksplisit.
- Shared/event/schema version unsupported gagal jelas.
- Secret type tidak tampil pada repr/log.
- Unknown setting policy diputuskan per environment.

## Precedence

Urutan config source dan override harus didokumentasikan. `.env` hanya untuk development; staging/production memakai secret/config mechanism Infra.
