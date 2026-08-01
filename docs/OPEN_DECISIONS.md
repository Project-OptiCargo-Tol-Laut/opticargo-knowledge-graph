# Open Decisions

Materi yang diberikan belum cukup untuk menetapkan hal berikut secara final:

1. URL/tag/checksum resmi `opticargo-shared`.
2. Canonical PostgreSQL table/view/column contract dan credential read-only.
3. Final property allowlist per entity dan PII approval.
4. Source resmi migration bila legacy `constraints.cypher`/`indexes.cypher` dipertahankan.
5. Full-text index use case, field, analyzer, dan locale.
6. Metrics port dan scrape configuration graph worker pada Infra.
7. Processed-event/retry key retention dan Redis persistence policy.
8. Default stale cleanup pada staging/production dan approval flow.
9. Exact typed query result/version yang dikonsumsi Agents dan RAG.
10. Formula network analytics, corridor load, dan underserved supplier.
11. Schema migration vs application rollout compatibility/rollback order.
12. Neo4j backup/snapshot dan full rebuild operational ownership.

Setiap keputusan harus menghasilkan ADR, config/contract update, test, dan traceability.
