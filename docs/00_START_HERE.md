# Start Here

## Tujuan repository

Bangun typed graph query package, event-driven projection worker, versioned Neo4j schema, dan scheduled reconciliation dengan PostgreSQL sebagai source of truth.

## Urutan pembacaan

1. `REVIEW_BASIS.md`
2. `EXISTING_IMPLEMENTATION_REVIEW.md`
3. `GRAPH_SCHEMA_SPECIFICATION.md`
4. `PROJECTION_MODEL.md`
5. `INTERFACE_CONTRACTS.md`
6. `IMPLEMENTATION_FLOW.md`
7. `QUERY_LIBRARY.md`
8. `EVENT_PROCESSING.md`
9. `RECONCILIATION.md`
10. `TESTING_STRATEGY.md`
11. `SMOKE_TEST_SPECIFICATION.md`
12. `OPEN_DECISIONS.md`

## Gate pertama

Sebelum source diisi, selesaikan:

- versi/tag/checksum `opticargo-shared`;
- canonical PostgreSQL table/column/view contract;
- 14 label, relationship, dan property allowlist;
- event catalog/version dan ACK/retry/DLQ contract;
- typed query request/result yang dikonsumsi Agents/RAG;
- schema migration source-of-truth dan target version;
- Infra command, metrics scrape port, healthcheck, secret, dan read-only PostgreSQL credential;
- curated seed untuk projection/query/reconciliation test.

## Larangan awal

- Jangan menyalin implementasi lama ke file kosong tanpa meninjau contract dan migration.
- Jangan membuka public HTTP endpoint.
- Jangan memproyeksikan event payload secara langsung tanpa canonical lookup.
- Jangan membuat label/relation/property berdasarkan string input yang tidak terdaftar.
- Jangan mengaktifkan CI workflow sebelum command dan test nyata tersedia.
