# Contributing

Setiap perubahan harus memiliki scope terbatas, requirement/acceptance, file in-scope, contract version, migration impact, test plan, failure behavior, observability impact, dan evidence.

## Minimum change quality

- Tidak mendefinisikan ulang contract `opticargo-shared`.
- PostgreSQL tetap source of truth dan Neo4j tetap reconstructable projection.
- Query package tidak memutasi transaksi.
- Perubahan schema mempunyai migration versioned, verification, dan rollback/rebuild plan.
- Test relevan ditambahkan pada layer yang benar.
- Secret, production PII, raw payment provider data, dan document content tidak masuk graph, repository, log, metric label, atau fixture.
- README folder, catalog, traceability, dan ADR diperbarui bila keputusan berubah.

Gunakan template issue dan pull request pada `.github/`.
