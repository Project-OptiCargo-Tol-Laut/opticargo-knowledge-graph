# `opticargo_knowledge_graph.clients`

## Tujuan

Mengisolasi SDK/driver PostgreSQL, Redis, dan Neo4j dari projection, worker, reconciliation, dan query domain.

## Posisi dalam alur runtime

Composition root membuat adapter. Domain service bergantung pada protocol dan menerima adapter melalui dependency injection.

## Tanggung jawab file

| File | Tanggung jawab | Perilaku yang diharapkan | Verifikasi utama |
|---|---|---|---|
| `__init__.py` | Public adapter exports. | Mengekspor class adapter yang stabil tanpa membuat connection saat import. | `tests/unit/clients/test_imports.py` |
| `neo4j.py` | Neo4j driver adapter. | Lazy driver; ping; parameterized read query; migration statements; projection transaction; relationship replacement; delete; projection state; close. | `tests/unit/clients/test_neo4j.py` |
| `postgres.py` | Read-only PostgreSQL adapter. | Connection pool; ping; canonical fetch one/batch/iterator/count; statement timeout; close; tidak menyediakan write transaction. | `tests/unit/clients/test_postgres.py` |
| `redis_stream.py` | Redis Streams, idempotency, retry, DLQ, dan lock adapter. | Create group; read group; XAUTOCLAIM; ACK; pending count; processed/retry key; bounded backoff; sanitized DLQ; token-safe lock. | `tests/unit/clients/test_redis_stream.py` |

## Dependency dan contract

- PostgreSQL driver/SQL toolkit yang disetujui.
- Redis client dengan Redis Streams dan Lua/EVAL support untuk lock.
- Neo4j Python driver dengan database selection dan timeout.
- Settings/secret dari package config.

## Aturan desain

- Connection dibuat lazy atau eksplisit pada startup.
- Semua query value menggunakan parameter; dynamic label/relationship identifier harus berasal dari allowlist registry.
- PostgreSQL credential untuk runtime ini harus read-only.
- Lock hanya dapat diperpanjang/dilepas oleh token pemilik.
- DLQ tidak boleh menyimpan secret atau raw sensitive row.

## Observability

- Dependency up/down, operation latency, timeout, pool/driver error class, pending count, dan DLQ result.
- Jangan meletakkan URI berisi password pada log.

## Batas tanggung jawab

- Adapter tidak menentukan business projection schema.
- Adapter tidak melakukan retry policy global di luar contract yang disepakati.
- Adapter Neo4j tidak menjadi jalur mutation bebas untuk consumer Agents/RAG.

## Kriteria verifikasi

- Unit test memverifikasi perilaku normal, input tidak valid, boundary condition, dan typed failure.
- Contract test memverifikasi schema lintas repository untuk event, query result, health, dan metrics.
- Integration test memakai PostgreSQL, Redis Streams, dan Neo4j aktual hanya pada layer adapter atau composition root.
- Implementasi tidak dianggap siap bila test hanya berisi placeholder, permanent skip, atau assertion yang tidak memeriksa perilaku.

> File implementasi pada struktur awal ini belum berisi kode. Dokumen ini menetapkan fungsi, contract, dan perilaku yang perlu dipenuhi saat file tersebut diimplementasikan.
