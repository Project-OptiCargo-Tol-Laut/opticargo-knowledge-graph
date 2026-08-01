# Definition of Done

## Per feature

- Requirement/acceptance terhubung ke code, migration/query, test, dan docs.
- Unit, architecture, contract, dan relevant integration/evaluation test lulus.
- Typed interface, error, idempotency, timeout, retry, observability, and security boundary selesai.
- Schema change mempunyai versioned migration dan compatibility/rebuild/rollback evidence.
- Tidak ada secret, hardcoded production response, PII leak, atau unbounded query.

## Runtime/integration

- Worker health/metrics/log, pending reclaim, retry/DLQ, graceful shutdown, and restart verified.
- Reconciliation check/repair/lock/stale/full rebuild verified.
- Consumer Agents/RAG contract test lulus.
- Image non-root, immutable tag/digest, resource profile, command, and Infra smoke verified.

## Release

- Clean checkout reproducible.
- Staging seed/projection/query/recovery journey berhasil.
- Graph sync lag/query latency/reconciliation threshold measured.
- Backup/snapshot, rebuild, rollback, alert, and runbook rehearsed.
- Known limitation ditulis dan tidak disamarkan.
