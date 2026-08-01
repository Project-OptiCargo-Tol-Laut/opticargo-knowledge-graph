# End-to-End Tests

## Tujuan

Memverifikasi critical graph journey dari canonical transaction/event sampai projection dan typed query result.

## Kondisi eksekusi

Menjalankan stack integration dengan reproducible seed. Setiap journey dimulai dari clean/reset state dan menyimpan evidence graph/query.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_entity_change_projection.py` | Gateway/outbox-equivalent event untuk create/update/delete entity menghasilkan projection canonical dan query visibility. |
| `test_booking_payment_review_lifecycle.py` | Booking, payment, review event membentuk lifecycle relationship yang dapat ditelusuri tanpa sensitive payment data. |
| `test_document_supersession_projection.py` | Document active/superseded metadata dan SUPERSEDES relation berubah konsisten tanpa object key/content. |
| `test_backhaul_discovery_flow.py` | Voyage/listing/capacity/supplier/port seed menghasilkan candidate valid dari typed discovery/matching query. |
| `test_recovery_reconciliation.py` | Event yang sengaja dilewatkan menghasilkan mismatch dan dipulihkan oleh reconciliation tanpa duplicate. |

## Evidence minimum

- Correlation/event/entity ID
- PostgreSQL canonical state
- Redis event/ACK state
- Neo4j node/relationship/hash
- Typed query result dan cleanup

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
