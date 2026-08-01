# `opticargo_knowledge_graph.queries`

## Tujuan

Menyediakan typed, bounded, read-only graph queries untuk Agents dan graph context RAG.

## Posisi dalam alur runtime

Consumer memanggil public function dengan request tervalidasi. Executor menjalankan parameterized Cypher dan mengembalikan result model stabil. Query package tidak menulis graph atau transaksi.

## Tanggung jawab file

| File | Tanggung jawab | Perilaku yang diharapkan | Verifikasi utama |
|---|---|---|---|
| `__init__.py` | Public typed query exports. | Mengekspor function dan result model yang menjadi consumer contract. | `tests/unit/queries/test_imports.py` |
| `models.py` | Typed request/result model. | Backhaul candidate, cargo-ship match, transit path, supplier distance, overview, filter validation, units dan nullable semantics. | `tests/unit/queries/test_models.py` |
| `executor.py` | Shared query execution wrapper. | Readonly session/driver compatibility, parameter binding, timeout/error mapping, query metrics, result normalization. | `tests/unit/queries/test_executor.py` |
| `backhaul_discovery.py` | Backhaul candidate discovery. | Voyage atau origin input; radius; schedule tolerance; listing status; remaining weight/volume; deterministic order; limit. | `tests/unit/queries/test_backhaul_discovery.py` |
| `cargo_matching.py` | Cargo-to-voyage/ship matching query. | Origin/destination, commodity/category, capacity weight/volume, allowed cargo/certification, time window, bounded result. | `tests/unit/queries/test_cargo_matching.py` |
| `pathfinding.py` | Bounded port transit path query. | Start/end port; max hops allowlist; canonical ROUTE_TO relation; path cost and route detail; reject unbounded traversal. | `tests/unit/queries/test_pathfinding.py` |
| `spatial_queries.py` | Port/supplier radius discovery. | Coordinate validation; distance calculation; radius/limit bound; deterministic distance ordering. | `tests/unit/queries/test_spatial_queries.py` |
| `analytics.py` | Read-only operational/network analytics. | Graph overview, corridor load, lifecycle trace, underserved supplier insight setelah metric definition disetujui. | `tests/unit/queries/test_analytics.py` |

## Dependency dan contract

- Canonical labels/relationships dari projection registry/schema.
- Neo4j read session/driver protocol.
- Shared identifier/enum bila menjadi contract lintas repository.
- Prometheus query metrics dan structured logging.

## Aturan desain

- Semua value diparameterkan.
- Hop/radius/tolerance/limit memiliki bound.
- Filter hard constraint tidak boleh hanya menjadi post-processing.
- Result order deterministic dan tie-breaker terdokumentasi.
- Query tidak boleh mengandalkan property yang tidak diproyeksikan.
- Breaking response change memerlukan versioning/consumer contract test.

## Observability

- Query name, duration, result count, timeout/error class, filter mode, dan fallback signal bila consumer menerapkannya.
- Jangan memasukkan query text penuh dengan sensitive parameter ke log.

## Batas tanggung jawab

- Tidak menjalankan write Cypher.
- Tidak membuat recommendation persistence.
- Tidak melakukan booking/payment mutation.
- Tidak membuat arbitrary Cypher dari natural-language input.

## Kriteria verifikasi

- Unit test memverifikasi perilaku normal, input tidak valid, boundary condition, dan typed failure.
- Contract test memverifikasi schema lintas repository untuk event, query result, health, dan metrics.
- Integration test memakai PostgreSQL, Redis Streams, dan Neo4j aktual hanya pada layer adapter atau composition root.
- Implementasi tidak dianggap siap bila test hanya berisi placeholder, permanent skip, atau assertion yang tidak memeriksa perilaku.

> File implementasi pada struktur awal ini belum berisi kode. Dokumen ini menetapkan fungsi, contract, dan perilaku yang perlu dipenuhi saat file tersebut diimplementasikan.
