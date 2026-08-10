# Test Structure

Testing dibagi berdasarkan tujuan agar evidence mudah ditelusuri ke requirement dan failure mode.

| Folder | Fokus |
|---|---|
| `architecture/` | Boundary source of truth, no public service, dependency direction, no sensitive graph data, dan package ownership. |
| `contract/` | Shared/event, projection schema, query result, Agents/RAG consumer, Infra command, health/metrics, dan packaging contract. |
| `unit/` | Pure behavior module, builder, validation, adapter dengan fake, worker state, reconciliation diff, dan query construction. |
| `smoke/` | Preflight cepat dari clean checkout hingga package/import/config/dependency/startup/check-only. |
| `integration/` | PostgreSQL, Redis Streams, Neo4j, schema migration, worker projection, reconciliation, query, dan metrics aktual. |
| `e2e/` | Critical lifecycle dan recovery lintas event-to-graph-to-query. |
| `resilience/` | Duplicate, pending reclaim, retry, DLQ, restart, missed event, lock, rebuild, stale cleanup. |
| `evaluation/` | Validitas hasil discovery/matching/pathfinding/analytics pada curated graph dataset. |
| `performance/` | Query latency, sync lag, projection throughput, backlog, dan reconciliation duration. |
| `security/` | Secret/log redaction, sensitive property exclusion, injection safety, read-only PostgreSQL, internal-only runtime. |
| `fixtures/` | Dataset/event/expected graph/query fixture versioned dan non-sensitive. |

Seluruh file test Python pada struktur di atas telah memiliki implementasi. Test
yang membutuhkan dependency nyata memakai environment gate eksplisit agar tidak
memberi hasil lulus semu pada runtime yang tidak tersedia:

- `OPTICARGO_INTEGRATION=1` untuk Neo4j integration dasar;
- `OPTICARGO_FULL_INTEGRATION=1` untuk PostgreSQL dan Redis disposable;
- `OPTICARGO_SEEDED_INTEGRATION=1` untuk evaluation terhadap dataset OptiCargo;
- `OPTICARGO_E2E=1` untuk lifecycle/recovery;
- `OPTICARGO_PERFORMANCE=1` untuk benchmark dengan threshold terkonfigurasi.

Skip tanpa environment tersebut berarti precondition runtime tidak dipenuhi,
bukan bukti bahwa capability telah lulus.
