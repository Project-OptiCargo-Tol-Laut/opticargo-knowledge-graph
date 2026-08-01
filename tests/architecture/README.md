# Architecture Tests

## Tujuan

Menjaga keputusan arsitektur repository dan mencegah coupling atau data-boundary regression.

## Kondisi eksekusi

Tidak membutuhkan dependency eksternal. Dijalankan pada setiap perubahan source, packaging, atau dependency.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_no_public_http_service.py` | Memastikan package tidak menyediakan FastAPI/public ingress dan artifact runtime hanya worker/job/package. |
| `test_dependency_direction.py` | Memastikan query/projection/domain tidak bergantung pada CLI, concrete adapter, atau application repository lain. |
| `test_postgres_source_of_truth.py` | Memastikan projection/reconciliation membaca canonical PostgreSQL dan tidak memakai Neo4j untuk memulihkan transaksi. |
| `test_query_package_read_only.py` | Memastikan public query surface tidak berisi write Cypher atau PostgreSQL mutation. |
| `test_no_sensitive_graph_properties.py` | Memastikan allowlist projection mengecualikan secret, password hash, email/PII yang tidak diperlukan, raw payment reference, object key, dan document content. |
| `test_cypher_resource_ownership.py` | Memastikan domain Cypher dimiliki package ini dan consumer tidak perlu menyusun query schema sendiri. |
| `test_no_duplicate_shared_models.py` | Memastikan entity/event lintas repository diimpor dari Shared dan tidak didefinisikan ulang. |
| `test_single_schema_source.py` | Memastikan versioned migrations menjadi source schema resmi dan resource legacy tidak drift. |

## Evidence minimum

- Import/dependency graph
- Daftar public symbol dan migration resources
- Property allowlist/schema scan
- Failure menunjuk boundary yang dilanggar

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
