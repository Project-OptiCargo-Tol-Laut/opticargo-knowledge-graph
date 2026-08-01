# Unit Tests — cli

## Tujuan

Memverifikasi behavior module `cli` secara terisolasi.

## Kondisi eksekusi

Tidak menggunakan dependency eksternal; SDK diganti fake atau stub protocol yang memeriksa parameter dan urutan call.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_imports.py` | CLI import tanpa execution. |
| `test_factory.py` | Dependency creation/cleanup pada success/failure. |
| `test_doctor.py` | Ready/degraded/error, JSON/human output, no secret. |
| `test_migrate.py` | Apply/verify, target, exit code, cleanup. |
| `test_schema.py` | Canonical schema output dan no secret. |

## Evidence minimum

- Fixture minimal
- Expected call/result/error
- Boundary dan invalid input
- Tidak ada network call

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
