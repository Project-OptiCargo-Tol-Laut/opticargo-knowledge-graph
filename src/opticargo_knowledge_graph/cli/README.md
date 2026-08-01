# `opticargo_knowledge_graph.cli`

## Tujuan

Menyediakan command operasional untuk dependency diagnosis, schema migration, dan schema inspection.

## Posisi dalam alur runtime

CLI menjadi thin composition layer. Domain logic tetap berada pada schema, projection, query, atau reconciliation service.

## Tanggung jawab file

| File | Tanggung jawab | Perilaku yang diharapkan | Verifikasi utama |
|---|---|---|---|
| `__init__.py` | CLI package marker. | Tidak menjalankan command saat import. | `tests/unit/cli/test_imports.py` |
| `factory.py` | Composition helper untuk Settings dan adapter. | Membuat dependency; ping/readiness bila diminta; close seluruh resource pada success/failure. | `tests/unit/cli/test_factory.py` |
| `doctor.py` | Dependency diagnostic command. | Memeriksa config, Shared version, PostgreSQL read access, Redis group/stream capability, Neo4j database/schema version, health/metrics readiness. | `tests/unit/cli/test_doctor.py` |
| `migrate.py` | Schema migration command. | Apply atau verify migration; target override terkontrol; machine-readable summary; exit code. | `tests/unit/cli/test_migrate.py` |
| `schema.py` | Graph schema inspection command. | Menampilkan canonical labels, relationships, projection entities, migration target, query contract version tanpa secret. | `tests/unit/cli/test_schema.py` |

## Dependency dan contract

- Settings package.
- Client adapter.
- GraphMigrator dan projection/query registry.
- Structured output/logging.

## Aturan desain

- Command mempunyai deterministic exit code.
- Mode machine-readable dan human-readable dipisahkan.
- Diagnostic tidak melakukan mutation kecuali command migration yang eksplisit.
- Secret tidak dicetak.
- Resource selalu ditutup.

## Observability

- Command name, duration, dependency status, migration current/target, and exit status.
- Output JSON tidak memuat credential.

## Batas tanggung jawab

- CLI bukan public service.
- CLI tidak menjadi lokasi business logic.
- Doctor tidak memperbaiki state secara diam-diam.

## Kriteria verifikasi

- Unit test memverifikasi perilaku normal, input tidak valid, boundary condition, dan typed failure.
- Contract test memverifikasi schema lintas repository untuk event, query result, health, dan metrics.
- Integration test memakai PostgreSQL, Redis Streams, dan Neo4j aktual hanya pada layer adapter atau composition root.
- Implementasi tidak dianggap siap bila test hanya berisi placeholder, permanent skip, atau assertion yang tidak memeriksa perilaku.

> File implementasi pada struktur awal ini belum berisi kode. Dokumen ini menetapkan fungsi, contract, dan perilaku yang perlu dipenuhi saat file tersebut diimplementasikan.
