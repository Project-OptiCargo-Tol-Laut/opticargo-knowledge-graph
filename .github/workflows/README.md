# Workflow Placeholders

| File | Tujuan setelah diaktifkan | Gate minimum |
|---|---|---|
| `ci.yml.disabled` | lint, format, type-check, unit, contract, architecture, migration resource, coverage, package build | command nyata tersedia dan tidak menggunakan permanent skip |
| `integration.yml.disabled` | PostgreSQL, Redis Streams, Neo4j, worker, reconciliation, query integration | service dependency, seed, readiness, timeout, cleanup, dan artifact log tersedia |
| `release.yml.disabled` | wheel/image build, SBOM/provenance, immutable tag, release evidence | seluruh release gate, smoke, migration, rollback/rebuild, dan security scan lulus |

Jangan mengubah ekstensi menjadi `.yml` sebelum workflow tersebut dapat dijalankan dari clean checkout.
