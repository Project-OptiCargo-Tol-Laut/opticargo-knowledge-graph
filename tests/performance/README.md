# Performance Tests

## Tujuan

Membuktikan latency, sync lag, throughput, backlog, dan reconciliation scale dengan profile yang dapat diulang.

## Kondisi eksekusi

Test menyatakan hardware/container resource, dataset size, warmup, concurrency, duration, dan threshold environment. Hasil lokal tidak otomatis menjadi SLO production.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_graph_query_latency.py` | Mengukur p50/p95/p99 typed query pada seed dan concurrency yang ditentukan. |
| `test_projection_throughput.py` | Mengukur event projection throughput dan Neo4j transaction latency. |
| `test_sync_lag.py` | Mengukur occurred_at sampai projection completion; target PRD dan alert threshold dapat dibuktikan. |
| `test_worker_backlog.py` | Mengukur drain rate, pending, retry, dan recovery di bawah burst. |
| `test_reconciliation_duration.py` | Mengukur check/repair full scan per entity family dan lock TTL safety. |

## Evidence minimum

- Commit/image/dependency version
- Dataset and resource profile
- Raw measurement and percentile
- Threshold decision and regression delta

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
