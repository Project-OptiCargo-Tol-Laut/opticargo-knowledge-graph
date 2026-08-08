# Test suite catalog

Test suite menggunakan skenario nyata per file yang ditetapkan README dan
dikelompokkan berdasarkan capability agar requirement serta evidence dapat
ditelusuri langsung.

| Capability | Evidence utama |
|---|---|
| Shared GraphContext | `tests/contract/test_rag_graph_context_contract.py` |
| Migration loader/version/checksum | `tests/unit/schema/` |
| Projection registry/builders/transaction/dedup | `tests/unit/projections/` |
| PostgreSQL read-only source | `tests/unit/clients/test_postgres.py` |
| Typed discovery/matching/path/spatial/analytics | `tests/unit/queries/` |
| Worker envelope, retry, pending reclaim, DLQ | `tests/unit/test_worker.py`, `tests/resilience/` |
| Reconciliation drift/repair | `tests/unit/test_reconciliation.py` |
| Query/projection security | `tests/security/` |
| Architecture read-only invariant | `tests/architecture/` |
| Live Neo4j migration/query | `tests/integration/` |
| Critical event-to-query lifecycle | `tests/e2e/` |
| Seeded result quality | `tests/evaluation/` |
| Latency/throughput/backlog/reconciliation | `tests/performance/` |

Integration test generik dilewati kecuali `OPTICARGO_INTEGRATION=1`; workflow
integration menyediakan Neo4j nyata. Validasi capability yang membutuhkan dataset
OptiCargo juga memerlukan `OPTICARGO_SEEDED_INTEGRATION=1` agar tidak dijalankan
terhadap database Neo4j kosong di CI.
E2E dan performance memakai environment gate tersendiri sebagaimana dijelaskan
di `tests/README.md`. File test 0 byte tidak diperbolehkan.
