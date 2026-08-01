# Unit Tests

## Tujuan

Memverifikasi behavior deterministik tanpa service eksternal.

## Kondisi eksekusi

Menggunakan fake/protocol, clock/sleeper terkendali, dan fixture kecil. Tidak melakukan network call.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_public_imports.py` | Public export stabil dan import tanpa side effect. |
| `test_client.py` | Convenience client/export tidak menggandakan logic adapter. |
| `test_config.py` | Required setting, type/range, secret, URI scheme, Shared/event/schema version, dan environment validation. |
| `test_contracts.py` | Redis field decode, JSON payload, Shared model validation, timestamp normalization, typed error. |
| `test_errors.py` | Exception hierarchy dan mapping retryable/permanent bila digunakan. |
| `test_health.py` | Heartbeat create/read/atomic write/freshness/dependency/pending state. |
| `test_healthcheck_entrypoint.py` | Exit code ready, stale, missing, dan malformed heartbeat. |
| `test_logging.py` | Structured output, correlation, exception, redaction, dan no sensitive data. |
| `test_metrics.py` | Metric definition, label cardinality, update behavior, dan duplicate registration safety. |
| `test_protocols.py` | Protocol signatures cukup untuk domain service dan tidak mengikat concrete SDK. |
| `test_serialization.py` | Graph-safe values, drop None, Decimal/UUID/datetime/Enum, deterministic order/hash. |
| `test_worker.py` | Startup, group, pending reclaim, duplicate, retry, DLQ, ACK ordering, concurrency, heartbeat, shutdown. |
| `test_reconcile_entrypoint.py` | CLI arguments check/repair/stale, composition cleanup, exit code, report. |
| `test_reconciliation.py` | Diff missing/mismatch/stale, dependency order, lock token, check-only, repair, report, metrics. |
| `test_version.py` | Version source selaras dengan package metadata. |

## Evidence minimum

- Input dan expected output/error
- Call/order pada protocol fake
- Tidak ada hidden network/clock dependency
- Coverage branch pada failure path

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
