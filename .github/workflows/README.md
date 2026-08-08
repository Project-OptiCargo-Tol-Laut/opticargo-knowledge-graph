# Workflow Delivery Gates

| File | Status | Gate minimum |
|---|---|---|
| `ci.yml` | Aktif untuk PR/push | lint, unit/contract/architecture, migration resource, dan clean package import |
| `integration.yml` | Aktif untuk PR/manual | Neo4j service nyata, migration idempotent, query/projection integration |
| `release.yml.disabled` | Sudah diimplementasikan, belum diaktifkan | wheel/image, SBOM, vulnerability scan, immutable artifact, provenance |

Release workflow tidak boleh diaktifkan sebelum protected environment, registry
permission, tag policy, dan penanggung jawab release disetujui pemilik organisasi.
