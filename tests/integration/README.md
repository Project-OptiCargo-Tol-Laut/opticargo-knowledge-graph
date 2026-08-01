# Integration Tests

## Tujuan

Membuktikan adapter, migration, worker service, reconciliation, dan query package terhadap service aktual.

## Kondisi eksekusi

Gunakan database/stream/graph namespace disposable, readiness check, timeout, dan cleanup. Test tidak boleh berjalan terhadap environment production.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_postgres_connection.py` | Read-only connection, canonical query, timeout, transaction isolation, dan write denial. |
| `test_redis_connection.py` | Auth/database/ping dan cleanup namespace test. |
| `test_neo4j_connection.py` | Database selection, read/write session untuk runtime owner, timeout, dan cleanup graph test. |
| `test_schema_migrations.py` | Apply migration 1..target dua kali, inspect constraints/index/fulltext, dan package resource. |
| `test_event_consumer_group.py` | Create/read/pending/autoclaim/ack consumer group dengan event fixture. |
| `test_projection_roundtrip.py` | Seed PostgreSQL row, process event, verify node/properties/relationships/hash, update FK, then delete. |
| `test_query_execution.py` | Seed graph lalu menjalankan seluruh typed query dengan expected result. |
| `test_reconciliation_runtime.py` | Missing/mismatched/stale graph terdeteksi dan diperbaiki; check-only tidak mutate. |
| `test_metrics_exposure.py` | Metrics endpoint/scrape internal memuat metric graph tanpa high-cardinality sensitive label. |

## Evidence minimum

- Image/version dependency
- Seed/stream/graph namespace
- State sebelum dan sesudah
- Cleanup result dan log/metric artifact

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
