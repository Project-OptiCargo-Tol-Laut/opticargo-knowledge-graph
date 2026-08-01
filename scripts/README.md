# Operational Scripts

Script pada folder ini masih kosong. Implementasinya harus menjadi thin wrapper dan tidak menggandakan business logic package.

| File | Keperluan |
|---|---|
| `bootstrap.sh / bootstrap.ps1` | Membuat virtual environment, menginstal build tooling, Shared wheel, package dev dependency, lalu menjalankan preflight. |
| `build_shared_wheel.py` | Membangun atau memverifikasi wheel `opticargo-shared` dari source/tag resmi, metadata version, dan SHA-256. |
| `smoke_structure.py` | Memeriksa manifest, placeholder, README, no active workflow, no secret/wheel. |
| `smoke_shared.py` | Memeriksa Shared distribution/version/import contract. |
| `smoke_infra.py` | Memeriksa env dan konektivitas PostgreSQL/Redis/Neo4j menggunakan host/container mode. |
| `migrate_schema.py` | Menjalankan verify/apply migration dengan output machine-readable. |
| `run_worker.py` | Wrapper local untuk graph worker dengan signal dan environment validation. |
| `run_reconciliation.py` | Wrapper check/repair/stale mode reconciliation. |
| `inspect_graph.py` | Menampilkan schema/version/count/mismatch/query diagnostic tanpa sensitive property. |
| `validate.sh / validate.ps1` | Menjalankan quality gate nyata setelah toolchain tersedia. |

## Aturan

- Mendukung exit code non-zero pada failure.
- Tidak menampilkan secret.
- Mempunyai timeout dan pesan dependency yang jelas.
- Tidak menjalankan destructive migration/cleanup tanpa flag eksplisit.
- Menggunakan package CLI/service sebagai source logic.
- Linux shell dan PowerShell mempunyai behavior setara untuk bootstrap/validate.
