# Unit Tests — queries

## Tujuan

Memverifikasi behavior module `queries` secara terisolasi.

## Kondisi eksekusi

Tidak menggunakan dependency eksternal; SDK diganti fake atau stub protocol yang memeriksa parameter dan urutan call.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_imports.py` | Public query exports. |
| `test_models.py` | Request/result validation, unit, time window, bounds. |
| `test_executor.py` | Session/driver support, metrics, timeout, error normalization. |
| `test_backhaul_discovery.py` | Radius, schedule tolerance, status, capacity, deterministic ranking/limit. |
| `test_cargo_matching.py` | Origin/destination/category, weight/volume, compatibility/certification, time window. |
| `test_pathfinding.py` | Bounded hops, canonical relation, no path, invalid input. |
| `test_spatial_queries.py` | Coordinates, radius bound, distance ordering, missing location. |
| `test_analytics.py` | Overview/corridor/lifecycle/underserved metrics with stable semantics. |

## Evidence minimum

- Fixture minimal
- Expected call/result/error
- Boundary dan invalid input
- Tidak ada network call

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
