# Smoke Tests

## Tujuan

Memberikan preflight cepat dari struktur hingga dependency/runtime entrypoint sebelum integration suite.

## Kondisi eksekusi

Dijalankan berurutan. Case dependency hanya berjalan ketika environment eksplisit tersedia; skip harus menjelaskan dependency yang belum disiapkan, bukan menyamarkan failure.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_repository_structure.py` | Memastikan file/folder/README/manifest tersedia, placeholder tetap kosong, workflow tidak aktif, dan tidak ada wheel/secret. |
| `test_shared_wheel.py` | Memastikan wheel Shared tersedia, version/distribution benar, import contract berhasil, dan checksum dapat dicatat. |
| `test_environment_contract.py` | Memastikan required env tersedia, URI scheme benar, host/internal port tidak tertukar, dan collision tidak terjadi. |
| `test_dependency_connectivity.py` | TCP/driver ping PostgreSQL, Redis, dan Neo4j menggunakan timeout singkat. |
| `test_query_package_import.py` | Memastikan public query package dapat diimpor dari installed wheel tanpa side effect. |
| `test_schema_migration_command.py` | Menjalankan migration verify/apply pada database disposable dan memastikan target version tercapai. |
| `test_worker_startup.py` | Memastikan group/schema/dependency/metrics/heartbeat startup siap lalu shutdown bersih tanpa event. |
| `test_reconciliation_check.py` | Menjalankan check-only reconciliation pada seed kecil dan menghasilkan report machine-readable. |
| `test_healthcheck.py` | Memastikan health command membedakan ready/stale/dependency failure. |

## Evidence minimum

- Command dan exit code
- Dependency endpoint tanpa credential
- Schema/consumer group/health status
- Duration dan failure reason

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
