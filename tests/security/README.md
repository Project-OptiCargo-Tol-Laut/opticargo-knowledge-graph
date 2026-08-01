# Security Tests

## Tujuan

Memverifikasi secret handling, data minimization, injection safety, read-only source access, dan internal-only deployment.

## Kondisi eksekusi

Gunakan synthetic secret dan data. Jangan memakai credential atau PII nyata pada fixture/evidence.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_secret_handling.py` | Secret hanya berasal dari environment/secret manager, tidak masuk repr/error/doctor/schema output. |
| `test_log_redaction.py` | Password/token/URI credential/sensitive field di-redact pada structured log dan exception. |
| `test_event_payload_no_secret.py` | Event dan DLQ payload tidak memuat credential, raw card data, atau secret token. |
| `test_projection_excludes_sensitive_fields.py` | Graph property allowlist menolak password hash, email/PII yang tidak diperlukan, raw payment provider data, object key, document content. |
| `test_cypher_injection_safety.py` | Value diparameterkan dan dynamic label/relation/index hanya berasal dari allowlist. |
| `test_read_only_postgres_access.py` | Runtime credential/query path tidak dapat menulis canonical table. |
| `test_internal_only_runtime.py` | Image/compose/manifests tidak memberi public ingress pada worker, reconciliation, atau Neo4j Bolt. |

## Evidence minimum

- Synthetic sensitive marker
- Redacted output
- Denied mutation/injection result
- Image/network configuration evidence

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
