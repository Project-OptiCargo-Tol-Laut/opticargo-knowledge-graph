# Maintained file manifest

Repository awal berisi banyak file 0 byte yang hanya menggambarkan rencana.
Seluruh file test yang tercantum dalam README sekarang dipulihkan dan berisi
skenario nyata. Placeholder workflow CI/integration telah digantikan workflow
aktif, sedangkan release workflow tetap nonaktif namun sudah memiliki gate lengkap.

## Runtime source

| Area | Implementasi |
|---|---|
| Schema | `schema/migrator.py`, `schema/migrations/*.cypher` |
| Projection | `projections/entity_builders.py`, `registry.py`, `service.py` |
| Event sync | `worker.py`, `clients/redis_stream.py`, `clients/postgres.py` |
| Reconciliation | `reconciliation.py`, `reconcile.py` |
| Query library | `queries/*.py` |
| Runtime clients | `clients/neo4j.py`, `clients/postgres.py`, `clients/redis_stream.py` |
| Operations | `cli/*`, `scripts/*`, Dockerfile |

## Intentionally empty files

- `src/opticargo_knowledge_graph/py.typed`: marker standar PEP 561.
- `tests/fixtures/*/.gitkeep` dan `vendor/.gitkeep`: marker direktori.
- `LICENSE`: belum boleh diisi tanpa keputusan pemilik organisasi; lihat
  `LICENSE_POLICY.md`.

Tidak ada core source, workflow aktif, atau test Python yang boleh kosong.
