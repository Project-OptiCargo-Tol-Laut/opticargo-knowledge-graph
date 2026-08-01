# Graph Query Evaluation

## Tujuan

Menilai validitas domain typed query dan analytics pada curated graph dataset, bukan hanya correctness syntax.

## Kondisi eksekusi

Dataset fixture harus versioned, mencakup match, no-match, edge, duplicate, disconnected, dan synthetic provenance.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_backhaul_query_validity.py` | Curated voyage/listing cases hanya mengembalikan candidate lokasi/waktu/status/capacity valid. |
| `test_matching_constraint_validity.py` | Hard constraint weight, volume, cargo type, certification, route, dan time window tidak dilanggar. |
| `test_pathfinding_bounds.py` | Path menggunakan canonical route, tidak melampaui max hops, dan cost/order dapat dijelaskan. |
| `test_network_analytics_sanity.py` | Overview/corridor metric konsisten dengan graph fixture dan tidak double count relationship. |
| `test_underserved_supplier_insight.py` | Definisi underserved yang disetujui menghasilkan insight masuk akal pada synthetic dataset dan mencatat limitation. |

## Evidence minimum

- Dataset/version/provenance
- Expected entity/path/metric
- Constraint violation count
- Regression summary

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
