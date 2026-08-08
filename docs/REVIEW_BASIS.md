# Review Basis

Struktur ini disusun setelah meninjau dua sumber yang diberikan:

1. **OptiCargo AI PRD Final Full Product v3.0** — khususnya keputusan PostgreSQL source of truth, Neo4j derived store, Redis Streams, repository classification, dependency contract, event architecture, KG-001 sampai KG-006, observability, testing, implementation sequence, dan Definition of Done.
2. **`opticargo-knowledge-graph-v1.0.0-final-complete`** — source package, projection registry, worker, reconciliation, schema migrations, typed queries, dependency clients, config, health/logging/metrics, CLI, test, README, dan operational documentation.

## Cara materi dipakai

- Nama module/file source mengikuti implementasi referensi agar fungsi yang sudah dirancang tidak hilang.
- Source, test, dan migration diimplementasikan ulang terhadap contract shared,
  PRD, serta source of truth PostgreSQL; referensi hanya menjadi basis review.
- README menjelaskan behavior runtime, precondition, evidence, dan boundary.
- Keputusan yang belum didukung contract/data tetap dicatat sebagai open decision,
  bukan disamarkan sebagai capability yang sudah selesai.
