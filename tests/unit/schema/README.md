# Unit Tests — schema

## Tujuan

Memverifikasi behavior module `schema` secara terisolasi.

## Kondisi eksekusi

Tidak menggunakan dependency eksternal; SDK diganti fake atau stub protocol yang memeriksa parameter dan urutan call.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_imports.py` | Migration export tanpa side effect. |
| `test_migration_loader.py` | Resource discovery, version/order, immutable naming, statement split. |
| `test_migrator.py` | Current/target, apply pending only, repeat, partial failure, metadata. |
| `test_schema_registry.py` | Expected constraints/index/fulltext resource dan no duplicate source. |

## Evidence minimum

- Fixture minimal
- Expected call/result/error
- Boundary dan invalid input
- Tidak ada network call

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
