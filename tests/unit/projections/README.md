# Unit Tests — projections

## Tujuan

Memverifikasi behavior module `projections` secara terisolasi.

## Kondisi eksekusi

Tidak menggunakan dependency eksternal; SDK diganti fake atau stub protocol yang memeriksa parameter dan urutan call.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_imports.py` | Projection export surface. |
| `test_models.py` | Immutable model, owner metadata, source hash determinism. |
| `test_registry.py` | Entity aliases, 14 specs, labels, SQL metadata, dependency order, unsupported entity. |
| `test_entity_builders.py` | Property allowlist dan relationship plan untuk setiap canonical entity. |
| `test_service.py` | Resolve event target, lookup, apply/delete/ignore/not-found, typed outcome. |

## Evidence minimum

- Fixture minimal
- Expected call/result/error
- Boundary dan invalid input
- Tidak ada network call

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
