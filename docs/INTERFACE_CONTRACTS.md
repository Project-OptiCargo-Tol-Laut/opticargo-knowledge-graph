# Interface Contracts

## Shared

- `DomainEvent` envelope dan event version.
- Entity identifiers, enum/status, and graph schema-compatible payload references.
- Semver dan compatibility test.

## Gateway / PostgreSQL

- Gateway adalah owner transaction dan outbox.
- Knowledge Graph membutuhkan read-only canonical query/view per entity.
- Table/column/view migration harus tersedia sebelum graph integration test.
- Event publish tidak menjadikan payload sebagai source row final.

## Redis / Infra

- Stream, DLQ, group, retention/maxlen, pending alert, auth, persistence policy.
- Worker/reconciliation command, healthcheck, metrics scrape, resource profile, scheduler, restart, deployment/rollback.

## Neo4j

- Database name, Bolt URI, runtime/migration credential, backup/snapshot, schema version, memory/resource profile.
- Neo4j tidak diakses browser/frontend secara langsung.

## Agents

- Installed typed query package and result schema.
- Timeout/fallback/correlation behavior.
- Agents tidak menyusun domain Cypher sendiri dan tidak menulis transaksi.

## RAG

- Graph context query interface tanpa circular runtime callback.
- RAG tidak menggunakan Knowledge Graph untuk menyimpan chunk/vector.
