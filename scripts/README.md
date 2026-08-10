# Operational Scripts

Script pada folder ini adalah entrypoint operasional yang dapat dijalankan. Script tetap
menjadi thin wrapper dan tidak menggandakan business logic package.

| File | Keperluan |
|---|---|
| `bootstrap.sh / bootstrap.ps1` | Membuat virtual environment, menginstal build tooling, Shared wheel, package dev dependency, lalu menjalankan preflight. |
| `build_shared_wheel.py` | Membangun atau memverifikasi wheel `opticargo-shared` dari source/tag resmi, metadata version, dan SHA-256. |
| `smoke_structure.py` | Memeriksa file wajib, Python kosong, urutan migration, dan workflow aktif. |
| `smoke_shared.py` | Memeriksa Shared distribution/version/import contract. |
| `smoke_infra.py` | Memeriksa env dan konektivitas PostgreSQL/Redis/Neo4j menggunakan host/container mode. |
| `smoke_realtime_projection.py` | Mengirim event aman dan duplikat untuk membuktikan idempotensi worker. |
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
