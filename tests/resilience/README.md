# Resilience and Recovery Tests

## Tujuan

Memverifikasi idempotency, pending recovery, bounded retry, DLQ, restart, distributed lock, reconciliation, rebuild, dan source-of-truth protection.

## Kondisi eksekusi

Dijalankan dengan fault injection terkontrol. Setiap case mendefinisikan failure point, expected recovery, time bound, dan cleanup.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_duplicate_event.py` | Duplicate event ID tidak menggandakan node/relationship atau side effect dan tetap di-ACK sesuai policy. |
| `test_pending_reclaim.py` | In-flight event dari consumer mati direclaim setelah idle threshold dan diproses sekali. |
| `test_retry_then_success.py` | Transient PostgreSQL/Neo4j/Redis failure menjalankan bounded backoff lalu success tanpa DLQ. |
| `test_dlq_flow.py` | Permanent contract/unsupported version/exhausted retry masuk DLQ sanitized sebelum source ACK. |
| `test_worker_restart.py` | Restart pada berbagai failure point tidak kehilangan event dan heartbeat kembali fresh. |
| `test_missed_event_reconciliation.py` | Projection yang tidak menerima event ditemukan dan diperbaiki dari PostgreSQL. |
| `test_lock_contention.py` | Dua reconciliation job tidak overlap; token owner melindungi refresh/release. |
| `test_neo4j_rebuild.py` | Graph disposable dapat dibangun ulang dari PostgreSQL melalui full reconciliation. |
| `test_stale_projection_cleanup.py` | Stale node/owned relationship dihapus hanya pada repair mode dan policy aktif. |
| `test_postgres_unavailable.py` | Worker tidak memproyeksikan event snapshot saat PostgreSQL unavailable dan menggunakan retry/DLQ policy. |

## Evidence minimum

- Injected failure dan timestamp
- State sebelum, selama, sesudah recovery
- ACK/pending/retry/DLQ/lock state
- Tidak ada duplicate side effect

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
