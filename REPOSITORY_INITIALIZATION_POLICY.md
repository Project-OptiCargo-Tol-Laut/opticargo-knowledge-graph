# Repository Initialization Policy

Struktur awal ini memisahkan spesifikasi dari implementasi.

## File yang tetap kosong sampai scope implementasinya dimulai

- Seluruh `*.py` pada `src/` dan `tests/`.
- Script `*.py`, `*.sh`, dan `*.ps1` pada `scripts/`.
- Seluruh `*.cypher` pada `src/opticargo_knowledge_graph/schema/`.
- `pyproject.toml`, requirements, Dockerfile, Makefile, dan Compose overlay.
- Workflow dengan ekstensi `.disabled`.

## Penempatan spesifikasi

- Tanggung jawab file: README pada folder source/test.
- Contract lintas repository: `docs/INTERFACE_CONTRACTS.md`.
- Graph schema dan projection allowlist: `docs/GRAPH_SCHEMA_SPECIFICATION.md` dan `docs/PROJECTION_MODEL.md`.
- Konfigurasi: `docs/CONFIGURATION_CONTRACT.md`.
- Skenario test: README folder test dan `docs/TEST_CASE_CATALOG.md`.
- Keputusan arsitektur: `docs/adr/`.

File kosong tidak boleh diperlakukan sebagai fitur selesai. Status implementasi hanya berdasarkan code, migration, test, dan evidence yang tersedia.
