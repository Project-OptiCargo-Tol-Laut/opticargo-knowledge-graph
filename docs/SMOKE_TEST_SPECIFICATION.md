# Smoke Test Specification

## Level 0 — Repository structure

Manifest, README, tidak ada Python kosong, workflow CI/integration tersedia,
dan tidak ada wheel/secret/generated artifact yang tidak semestinya.

## Level 1 — Package foundation

Build metadata tersedia, wheel dapat dibuat, public import tanpa side effect, `py.typed` dan migration resource masuk wheel.

## Level 2 — Shared contract

Wheel Shared distribution/version/checksum benar dan event/entity import dapat dilakukan.

## Level 3 — Environment

Required key, URI/port mode, secret presence, Shared/event/schema version, command contract.

## Level 4 — Dependency connectivity

PostgreSQL read-only ping/query, Redis group/stream capability, Neo4j database read/write untuk runtime owner.

## Level 5 — Schema and startup

Migration mencapai target dan repeat; worker membuat group, metrics, heartbeat lalu shutdown bersih.

## Level 6 — Projection

Satu canonical entity event menghasilkan node/relationship/hash benar; update/delete/idempotency terverifikasi.

## Level 7 — Reconciliation

Check-only menghasilkan report; injected missing projection diperbaiki tanpa duplicate.

## Level 8 — Query

Public typed query menjalankan curated seed dan mengembalikan result schema yang benar.

## Level 9 — Staging preflight

Image immutable, health/metrics scrape, pending/retry/DLQ, sync lag, scheduled reconciliation, backup/rebuild/rollback runbook tersedia.
