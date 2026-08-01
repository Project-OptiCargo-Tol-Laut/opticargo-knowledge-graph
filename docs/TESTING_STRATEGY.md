# Testing Strategy

## Layer

1. Architecture boundary.
2. Shared/producer/consumer/Infra contract.
3. Unit module and builder/query behavior.
4. Smoke package/config/dependency/startup/check.
5. Integration PostgreSQL/Redis/Neo4j/migration/projection/query/reconciliation.
6. E2E lifecycle/recovery.
7. Resilience/fault injection.
8. Query evaluation/domain validity.
9. Performance/sync lag/backlog.
10. Security/data boundary.

## Gate

- Source change: lint/type/unit/architecture/contract.
- Schema change: migration-resource, repeat, inspection, query compatibility, rebuild plan.
- Worker change: retry/ACK/DLQ/pending/restart and integration.
- Query change: unit, curated evaluation, consumer contract, latency.
- Reconciliation change: check/repair/lock/stale/rebuild and performance.
- Release: clean checkout, wheel/image, smoke, integration, E2E, security, backup/rebuild/rollback evidence.

## Test integrity

Permanent skip, assertion semu, mocked-everything integration, atau test yang hanya mengecek tidak crash tidak memenuhi gate. External test skip hanya boleh berdasarkan environment marker dan harus berjalan di pipeline integration resmi.
