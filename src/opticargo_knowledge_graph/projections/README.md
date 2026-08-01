# `opticargo_knowledge_graph.projections`

## Tujuan

Mendefinisikan projection deterministic dari canonical PostgreSQL row menjadi node dan relationship Neo4j.

## Posisi dalam alur runtime

Worker mengubah event menjadi target entity, service membaca row canonical, registry membangun plan, lalu adapter Neo4j menerapkannya dalam write transaction. Reconciliation menggunakan registry yang sama untuk mencegah drift.

## Tanggung jawab file

| File | Tanggung jawab | Perilaku yang diharapkan | Verifikasi utama |
|---|---|---|---|
| `__init__.py` | Public projection exports. | Mengekspor model, registry lookup, dan service yang disetujui. | `tests/unit/projections/test_imports.py` |
| `models.py` | Immutable projection plan models. | Node reference, relationship plan, property allowlist, ownership metadata, source hash, deterministic comparison. | `tests/unit/projections/test_models.py` |
| `registry.py` | Canonical mapping entity type ke label, source query, builder, dependency order, alias, dan supported events. | Menyediakan 14 entity spec; stable ID; graph-safe property allowlist; canonical relationship mapping; alias normalization. | `tests/unit/projections/test_registry.py` |
| `service.py` | Orchestrasi event/row menjadi graph mutation. | Resolve target; canonical row lookup; build plan; upsert/delete; ignored outcome; typed result; no-op untuk unchanged hash bila disepakati. | `tests/unit/projections/test_service.py` |

## Dependency dan contract

- Contract entity/enums dari Shared.
- Read-only canonical repository.
- Neo4j projection adapter.
- Serialization dan stable hash utility.
- Versioned graph schema.

## Aturan desain

- Stable ID selalu berasal dari ID canonical.
- Property memakai allowlist per entity; sensitive field tidak boleh ikut karena serialisasi generik.
- Relationship memiliki ownership metadata agar replacement aman saat foreign key berubah.
- Builder harus deterministic dan side-effect free.
- Registry menjadi satu source mapping projection untuk worker, reconciliation, docs, dan test.

## Observability

- Entity type, change type, plan hash, relationship count, outcome, duration, and mismatch reason.
- Property value dan row sensitif tidak dicatat penuh.

## Batas tanggung jawab

- Tidak menulis PostgreSQL.
- Tidak melakukan domain scoring atau booking logic.
- Tidak membangun vector/index RAG.
- Tidak menerima arbitrary label, relationship type, atau Cypher dari event.

## Kriteria verifikasi

- Unit test memverifikasi perilaku normal, input tidak valid, boundary condition, dan typed failure.
- Contract test memverifikasi schema lintas repository untuk event, query result, health, dan metrics.
- Integration test memakai PostgreSQL, Redis Streams, dan Neo4j aktual hanya pada layer adapter atau composition root.
- Implementasi tidak dianggap siap bila test hanya berisi placeholder, permanent skip, atau assertion yang tidak memeriksa perilaku.

> File implementasi pada struktur awal ini belum berisi kode. Dokumen ini menetapkan fungsi, contract, dan perilaku yang perlu dipenuhi saat file tersebut diimplementasikan.
