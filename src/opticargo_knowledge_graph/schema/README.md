# `opticargo_knowledge_graph.schema`

## Tujuan

Mengelola schema Neo4j melalui migration versioned yang repeatable, dapat diverifikasi, dan terpaket di wheel.

## Posisi dalam alur runtime

Worker/reconciliation menjalankan startup migration hingga target version. CLI migration dapat dijalankan sebagai pre-deploy job. Query hanya boleh aktif setelah required schema tersedia.

## Tanggung jawab file

| File | Tanggung jawab | Perilaku yang diharapkan | Verifikasi utama |
|---|---|---|---|
| `__init__.py` | Public migration exports. | Mengekspor migration model/runner tanpa menjalankan migration saat import. | `tests/unit/schema/test_imports.py` |
| `migrator.py` | Versioned Neo4j migration loader dan runner. | Load ordered resources; statement split; current version; target validation; idempotent apply; migration record; partial failure reporting. | `tests/unit/schema/test_migrator.py` |
| `constraints.cypher` | Legacy/compatibility schema placeholder. | Tidak boleh menjadi source of truth kedua. Keputusan mempertahankan atau menghapus harus dicatat pada ADR. | `tests/architecture/test_single_schema_source.py` |
| `indexes.cypher` | Legacy/compatibility index placeholder. | Tidak boleh menduplikasi versioned migration tanpa alasan dan test. | `tests/architecture/test_single_schema_source.py` |

## Dependency dan contract

- Neo4j adapter dengan migration/admin capability.
- Package resource loader.
- Schema target version dari config.
- Deployment/migration ordering dari Infra.

## Aturan desain

- Migration immutable setelah dirilis.
- Urutan version unik dan deterministic.
- Constraint/index name stabil.
- Cypher migration tidak memuat environment-specific value atau secret.
- Satu sumber resmi migration; resource legacy tidak boleh drift.
- Rollback utama derived store dapat berupa rebuild terkontrol bila down migration tidak aman.

## Observability

- Current/target version, migration ID, duration, applied/skipped/failed, Neo4j error code.
- Tidak mencatat credential atau raw graph data.

## Batas tanggung jawab

- Tidak membuat application transaction schema PostgreSQL.
- Tidak mengubah data bisnis di luar kebutuhan migration/rebuild yang disetujui.
- Tidak mengaktifkan destructive migration tanpa backup/rebuild plan.

## Kriteria verifikasi

- Unit test memverifikasi perilaku normal, input tidak valid, boundary condition, dan typed failure.
- Contract test memverifikasi schema lintas repository untuk event, query result, health, dan metrics.
- Integration test memakai PostgreSQL, Redis Streams, dan Neo4j aktual hanya pada layer adapter atau composition root.
- Implementasi tidak dianggap siap bila test hanya berisi placeholder, permanent skip, atau assertion yang tidak memeriksa perilaku.

> File implementasi pada struktur awal ini belum berisi kode. Dokumen ini menetapkan fungsi, contract, dan perilaku yang perlu dipenuhi saat file tersebut diimplementasikan.
