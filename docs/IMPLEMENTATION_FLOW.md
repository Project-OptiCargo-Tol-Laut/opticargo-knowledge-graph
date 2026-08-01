# Implementation Flow

## Fase 0 — Contract freeze

Shared event/entity version, canonical PostgreSQL read contract, graph schema/property allowlist, query request/result, Infra command/env/health/metrics, dan ADR disetujui.

## Fase 1 — Package foundation

Build metadata, config, error, protocol, serialization, public import, Shared installation, lint/type/test command.

## Fase 2 — Schema migration

Versioned resource loader, migration metadata, constraints/index, verify/apply CLI, package resource test.

## Fase 3 — Projection domain

Projection model/hash, registry 14 entity, property allowlist, relationship ownership, builder test, projection service.

## Fase 4 — Dependency adapters

Read-only PostgreSQL, Redis Streams/idempotency/lock/DLQ, Neo4j migration/projection/query adapter.

## Fase 5 — Event worker

Startup, group/schema, event validation, pending reclaim, bounded concurrency/retry, ACK/DLQ, heartbeat, metrics, shutdown.

## Fase 6 — Reconciliation

Check/repair, dependency order, stable hash comparison, distributed lock, stale policy, report, rebuild test.

## Fase 7 — Typed query library

Discovery, matching, pathfinding, spatial, analytics, typed result, consumer contract, query latency metrics.

## Fase 8 — Integration hardening

Live dependency, E2E lifecycle, fault injection, performance, security, image, Infra deployment, backup/rebuild/rollback.

## Dependency order yang tidak boleh dibalik

Shared contract dan PostgreSQL migration/seed harus tersedia sebelum graph sync integration. Graph schema/core query harus tersedia sebelum Agents matching workflow final. Metrics/health harus tersedia sebelum runtime masuk staging.
