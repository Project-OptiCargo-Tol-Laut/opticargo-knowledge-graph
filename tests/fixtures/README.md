# Test Fixtures

Fixture harus kecil, deterministic, versioned, tidak sensitif, dan dapat digunakan oleh unit/integration/E2E/evaluation tanpa menyalin production data.

| Folder | Isi |
|---|---|
| `events/` | Domain event valid/invalid/duplicate/unsupported version untuk entity dan transaction lifecycle. |
| `postgres/` | Canonical row/seed per entity, update/delete, dan dependency ordering. |
| `neo4j/` | Expected node, relationship, source hash, mismatch, stale, dan graph snapshot kecil. |
| `queries/` | Query request, expected candidate/path/analytics, match/no-match/edge cases. |
| `expected/` | Expected health, metrics, CLI, reconciliation report, and DLQ envelopes. |

Semua UUID, timestamp, unit, dan provenance harus eksplisit. Fixture synthetic diberi penanda yang jelas.
