# Unit Tests — clients

## Tujuan

Memverifikasi behavior module `clients` secara terisolasi.

## Kondisi eksekusi

Tidak menggunakan dependency eksternal; SDK diganti fake atau stub protocol yang memeriksa parameter dan urutan call.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_imports.py` | Adapter export dan lazy import. |
| `test_neo4j.py` | Parameterized query, identifier allowlist, projection transaction, relationship replace, delete, state, close. |
| `test_postgres.py` | Read-only connect, fetch one/batch/iterate/count, statement timeout, close, error mapping. |
| `test_redis_stream.py` | Group/read/autoclaim/ack/pending, idempotency, retry TTL, DLQ sanitize, lock token, close. |

## Evidence minimum

- Fixture minimal
- Expected call/result/error
- Boundary dan invalid input
- Tidak ada network call

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
