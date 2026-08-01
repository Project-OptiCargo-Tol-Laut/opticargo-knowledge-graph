# Versioned Neo4j Migrations

## Tujuan

Menyimpan urutan mutation schema Neo4j yang menjadi resource package dan dapat diterapkan berulang dengan hasil yang sama.

## File

| File | Scope yang perlu diisi | Verifikasi |
|---|---|---|
| `001_constraints.cypher` | Unique/stable ID constraints untuk seluruh canonical label serta migration metadata bila diperlukan. | Constraint dapat diterapkan dua kali tanpa drift dan duplicate ID ditolak. |
| `002_indexes.cypher` | Index property yang benar-benar digunakan oleh projection dan query: status, date, foreign-key mirror, coordinates, atau filter utama sesuai profiling. | Index name/property sesuai schema; query plan diverifikasi. |
| `003_fulltext.cypher` | Full-text index lintas label/property hanya bila use case dan analyzer telah diputuskan. | Search behavior, locale, update semantics, dan rebuild didokumentasikan. |

## Aturan

- File yang telah dirilis tidak diubah; koreksi dibuat sebagai migration baru.
- Satu file boleh berisi beberapa statement jika splitter dan failure semantics diuji.
- Destructive change membutuhkan compatibility window atau rebuild/cutover plan.
- Migration harus masuk wheel dan image; test packaging wajib memeriksa resource tersebut.
- `constraints.cypher` dan `indexes.cypher` di parent folder tidak boleh menjadi versi paralel yang berbeda.
