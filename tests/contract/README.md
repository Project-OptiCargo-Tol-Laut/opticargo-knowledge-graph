# Contract Tests

## Tujuan

Membuktikan compatibility lintas Shared, Gateway, Agents, RAG, Infra, dan package artifact.

## Kondisi eksekusi

Sebagian besar memakai fixture/schema snapshot. Consumer test dapat berjalan pada pipeline repository terkait setelah artifact tersedia.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_shared_version.py` | Memverifikasi package hanya menerima versi Shared yang disepakati dan incompatibility menghasilkan error jelas. |
| `test_event_envelope_contract.py` | Memverifikasi seluruh field event envelope, timestamp UTC, payload decoding, correlation/idempotency, dan unsupported version. |
| `test_entity_changed_contract.py` | Memverifikasi `entity.changed` untuk create/update/delete serta alias entity type. |
| `test_transaction_event_contracts.py` | Memverifikasi booking, payment, recommendation, document, dan review event dipetakan ke target projection yang benar. |
| `test_projection_schema_contract.py` | Memverifikasi 14 canonical label, relationship type, property allowlist, stable ID, ownership metadata, dan projection metadata. |
| `test_query_result_contracts.py` | Memverifikasi request/result schema, unit, nullable field, order, pagination/limit, dan error envelope typed query. |
| `test_agents_query_contract.py` | Memverifikasi import/signature/model yang dipakai Agents untuk discovery, matching, pathfinding, dan analytics. |
| `test_rag_graph_context_contract.py` | Memverifikasi graph context interface yang dipakai RAG tanpa runtime callback circular. |
| `test_infra_command_contract.py` | Memverifikasi command worker/reconciliation, env key, healthcheck, image entrypoint, dan internal endpoint sesuai Infra. |
| `test_health_metrics_contract.py` | Memverifikasi heartbeat payload dan nama/type metric yang di-scrape Infra. |
| `test_packaging_contract.py` | Memverifikasi wheel memuat py.typed, Cypher migration, metadata version, dan tidak memuat secret/generated test data. |

## Evidence minimum

- Contract version dan fixture ID
- Serialized request/event/result aktual
- Compatibility pass/fail reason
- Wheel/resource inspection

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
