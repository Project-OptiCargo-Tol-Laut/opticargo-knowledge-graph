# Migration, Compatibility, and Rollback

## Migration

- Version unik, ordered, packaged, immutable setelah release.
- Verify current/target sebelum runtime menerima event/query.
- Apply idempotent atau gagal dengan diagnosa jelas.
- Constraint/index creation dan query compatibility diuji.

## Compatibility

Projection/query dapat membutuhkan dual-read/dual-property window untuk breaking schema. Consumer version dan image deployment order harus ditulis.

## Rollback

Neo4j adalah derived store. Rollback dapat berupa image rollback plus schema compatibility, atau rebuild/cutover graph dari PostgreSQL. Down migration destructive tidak dipaksakan bila rebuild lebih aman.

## Evidence

Migration list, schema inspection, before/after query, package resource, snapshot/rebuild, rollback rehearsal, known limitation.
