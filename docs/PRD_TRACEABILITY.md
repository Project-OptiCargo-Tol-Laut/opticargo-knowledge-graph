# PRD Traceability

| PRD requirement | Struktur/bukti yang perlu dihasilkan |
|---|---|
| KG-001 schema node/relationship versioned | `schema/`, migration tests, schema inspection, docs schema |
| KG-002 real-time projection | worker, event/projection service, Redis/Neo4j integration, sync lag/idempotency tests |
| KG-003 nightly full reconciliation | reconciliation service/entrypoint, lock, check/repair/rebuild/stale tests |
| KG-004 query library discovery/matching/pathfinding | `queries/`, typed result, consumer contract, unit/evaluation/performance tests |
| KG-005 Booking/Payment/Review analytics graph | projection schema/builders dan lifecycle E2E/query test |
| KG-006 network analytics/underserved suppliers | analytics query, agreed formula, curated dataset, sanity/evaluation report |
| PostgreSQL source of truth | read-only adapter, canonical lookup, architecture/resilience tests |
| Redis Streams reliability | group, event ID, retry, pending reclaim, DLQ, ACK ordering tests |
| Observability | health, logs, sync lag, reconciliation mismatch, query latency metrics and alert inputs |
| Derived-store recovery | missed event repair, full rebuild, backup/rebuild/rollback evidence |
| Repository classification | package + worker/job, no public ingress architecture/Infra contract tests |
