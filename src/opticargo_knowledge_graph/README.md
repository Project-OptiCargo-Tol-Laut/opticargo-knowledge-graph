# `opticargo_knowledge_graph`

## Tujuan

Menyediakan typed Neo4j query package, graph projection runtime, versioned schema migration, reconciliation, dan operational entrypoint.

## Posisi dalam alur runtime

Event worker dan reconciliation memakai adapter PostgreSQL/Redis/Neo4j. Consumer Agents/RAG hanya menggunakan public typed query surface dan tidak mengakses implementation detail worker.

## Tanggung jawab file

| File | Tanggung jawab | Perilaku yang diharapkan | Verifikasi utama |
|---|---|---|---|
| `__init__.py` | Public package surface. | Mengekspor API stabil yang telah disetujui; tidak menjalankan side effect saat import. | `tests/unit/test_public_imports.py` |
| `client.py` | Convenience import untuk typed query client/session. | Menyediakan public entrypoint tanpa menggandakan implementasi adapter. | `tests/unit/test_client.py` |
| `config.py` | Runtime settings dan environment validation. | Typed setting, secret handling, range validation, supported Shared/event/schema version. | `tests/unit/test_config.py` |
| `contracts.py` | Adapter contract domain event dari Redis fields ke model Shared. | Decode field, validasi `DomainEvent`, normalisasi timestamp/payload, typed contract failure. | `tests/unit/test_contracts.py` |
| `errors.py` | Hierarki exception repository. | Membedakan contract, dependency, lock, query validation, migration, projection, dan reconciliation failure. | `tests/unit/test_errors.py` |
| `health.py` | Model heartbeat dan state worker/job. | Atomic write/read, freshness calculation, dependency state, pending count, last event/error. | `tests/unit/test_health.py` |
| `healthcheck.py` | Entrypoint container healthcheck. | Exit code berdasarkan heartbeat freshness dan required dependency state; tidak membuka HTTP server. | `tests/unit/test_healthcheck_entrypoint.py` |
| `logging.py` | Structured logging dan redaction. | JSON/text formatter, correlation context, allowlist/redaction, exception serialization. | `tests/unit/test_logging.py` |
| `metrics.py` | Prometheus metric definitions. | Graph sync lag, event count/duration, retry, DLQ, pending, query latency, reconciliation mismatch, dependency, build info. | `tests/unit/test_metrics.py` |
| `protocols.py` | Dependency inversion interfaces. | Graph client, canonical repository, stream/idempotency/lock client, clock/sleeper bila diperlukan. | `tests/unit/test_protocols.py` |
| `serialization.py` | Normalisasi graph-safe value dan stable hash. | Datetime/UUID/Decimal/Enum/list/map normalization; deterministic hash; drop value yang tidak diizinkan. | `tests/unit/test_serialization.py` |
| `worker.py` | Continuous Redis Streams graph synchronization runtime. | Startup, consumer group, pending reclaim, concurrency, event validation, retry, DLQ, ACK, projection, heartbeat, shutdown. | `tests/unit/test_worker.py` |
| `reconcile.py` | CLI entrypoint one-shot reconciliation. | Argument parsing untuk check/repair/stale policy, composition root, exit code, summary. | `tests/unit/test_reconcile_entrypoint.py` |
| `reconciliation.py` | Reconciliation domain service. | Lock, dependency-order scan, hash comparison, missing/mismatch repair, optional stale cleanup, report/metrics. | `tests/unit/test_reconciliation.py` |
| `version.py` | Package version source. | Menjaga version konsisten dengan build metadata dan release tag. | `tests/unit/test_version.py` |
| `py.typed` | Marker typed package. | Disertakan pada wheel agar consumer memperoleh type information. | `tests/contract/test_packaging_contract.py` |

## Dependency dan contract

- `opticargo-shared` untuk entity/event schema dan enum lintas repository.
- PostgreSQL read-only canonical access.
- Redis Streams untuk domain event, idempotency, retry, DLQ, dan distributed lock.
- Neo4j untuk projection dan read query.
- Prometheus/logging runtime yang disepakati Infra.

## Aturan desain

- Import package tidak membuat network connection.
- Neo4j tidak pernah dianggap source of truth.
- Semua mutation graph melalui projection/schema/reconciliation service.
- Event snapshot tidak menggantikan canonical PostgreSQL lookup.
- Public API package harus versioned dan backward compatibility diuji.

## Observability

- Correlation ID diteruskan dari event ke log.
- Worker state, sync lag, pending, retry, DLQ, projection result, reconciliation mismatch, dan query latency tersedia.
- Secret dan sensitive property tidak menjadi log/metric label.

## Batas tanggung jawab

- Tidak membuka public API.
- Tidak menulis transaksi PostgreSQL.
- Tidak melakukan booking/payment mutation.
- Tidak menyimpan document content, raw payment data, atau high-volume vector chunk pada graph.

## Kriteria verifikasi

- Unit test memverifikasi perilaku normal, input tidak valid, boundary condition, dan typed failure.
- Contract test memverifikasi schema lintas repository untuk event, query result, health, dan metrics.
- Integration test memakai PostgreSQL, Redis Streams, dan Neo4j aktual hanya pada layer adapter atau composition root.
- Implementasi tidak dianggap siap bila test hanya berisi placeholder, permanent skip, atau assertion yang tidak memeriksa perilaku.

> File implementasi pada struktur awal ini belum berisi kode. Dokumen ini menetapkan fungsi, contract, dan perilaku yang perlu dipenuhi saat file tersebut diimplementasikan.
