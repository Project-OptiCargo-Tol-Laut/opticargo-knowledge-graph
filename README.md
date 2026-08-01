# OptiCargo Knowledge Graph

Repository ini menyediakan **struktur awal implementasi** untuk Knowledge Graph OptiCargo. Seluruh file source, test, script, build configuration, Cypher migration, dan workflow masih kosong. Penjelasan fungsi, contract, dependency, alur runtime, dan pengujian disimpan pada README di setiap folder serta dokumen pada `docs/`.

## Peran repository

Knowledge Graph menghasilkan tiga artifact utama:

1. **Python typed query package** untuk discovery, cargo matching, bounded pathfinding, spatial query, dan analytics yang digunakan oleh `opticargo-agents` serta graph context pada `opticargo-rag-pipeline`.
2. **Graph synchronization worker** yang membaca domain event dari Redis Streams, mengambil data canonical dari PostgreSQL, lalu membuat projection idempotent ke Neo4j.
3. **Scheduled reconciliation job** yang membandingkan PostgreSQL dengan Neo4j dan memperbaiki node/relationship yang missing, mismatched, atau stale sesuai policy.

Repository ini bukan public HTTP service. PostgreSQL tetap menjadi source of truth. Neo4j adalah derived read model yang harus dapat dibangun ulang melalui event replay atau reconciliation.

## Alur utama

```text
Gateway transaction + transactional outbox
                  │
                  ▼
        Redis Stream opticargo:events
                  │
                  ▼
          graph synchronization worker
                  │
       validate event contract/version
                  │
       read canonical row from PostgreSQL
                  │
       build deterministic projection plan
                  │
                  ▼
              Neo4j projection

scheduled/manual reconciliation
        PostgreSQL canonical rows
                  │
      compare stable projection state
                  │
     repair missing/mismatched projection
                  │
      optional stale projection cleanup
                  ▼
                 Neo4j

Agents/RAG → typed query package → Neo4j read queries → typed results
```

## Canonical graph scope

Node projection yang terlihat pada rancangan dan implementasi referensi:

```text
User, Port, Ship, Route, Voyage, CargoCapacity, Commodity, Supplier,
CargoListing, Recommendation, Booking, Payment, Document, Review
```

Entity high-volume atau sensitif seperti `RagChunk`, `Notification`, dan `AuditLog` tidak menjadi node graph. `RagChunk` tetap berada pada Qdrant, sedangkan Notification/AuditLog tetap menjadi data PostgreSQL.

## Struktur repository

| Path | Kegunaan |
|---|---|
| `src/opticargo_knowledge_graph/` | Package query, projection, schema migration, worker, reconciliation, client dependency, CLI, health, logging, dan metrics. |
| `tests/` | Architecture, contract, unit, smoke, integration, E2E, resilience, evaluation, performance, dan security tests. |
| `docs/` | Graph schema, projection model, event processing, reconciliation, query contract, implementation flow, operations, testing, Infra, Shared wheel, ADR, dan Definition of Done. |
| `config/` | Acuan environment Infra serta daftar konfigurasi khusus Knowledge Graph. |
| `scripts/` | Placeholder bootstrap, validation, smoke, migration, worker, reconciliation, dan graph inspection. |
| `.github/` | Template issue/PR, CODEOWNERS template, dan workflow yang masih dinonaktifkan. |
| `vendor/` | Lokasi opsional wheel `opticargo-shared` untuk mode offline. |

## Status struktur awal

- Semua file Python pada `src/` dan `tests/` belum berisi kode.
- Semua script, Cypher migration, `pyproject.toml`, requirements, Dockerfile, Makefile, Compose overlay, dan workflow belum berisi konfigurasi aktif.
- Tidak ada test runtime yang diklaim lulus.
- Tidak ada wheel, image, atau generated artifact yang dibundel.
- Port metrics graph worker belum diputuskan oleh Infra; jangan membuat host mapping sepihak.

## Dokumen awal yang perlu dibaca

1. [`docs/00_START_HERE.md`](docs/00_START_HERE.md)
2. [`docs/EXISTING_IMPLEMENTATION_REVIEW.md`](docs/EXISTING_IMPLEMENTATION_REVIEW.md)
3. [`docs/GRAPH_SCHEMA_SPECIFICATION.md`](docs/GRAPH_SCHEMA_SPECIFICATION.md)
4. [`docs/PROJECTION_MODEL.md`](docs/PROJECTION_MODEL.md)
5. [`docs/INTERFACE_CONTRACTS.md`](docs/INTERFACE_CONTRACTS.md)
6. [`docs/IMPLEMENTATION_FLOW.md`](docs/IMPLEMENTATION_FLOW.md)
7. [`docs/QUERY_LIBRARY.md`](docs/QUERY_LIBRARY.md)
8. [`docs/TESTING_STRATEGY.md`](docs/TESTING_STRATEGY.md)
9. [`docs/SMOKE_TEST_SPECIFICATION.md`](docs/SMOKE_TEST_SPECIFICATION.md)
10. [`docs/DEFINITION_OF_DONE.md`](docs/DEFINITION_OF_DONE.md)

## Prinsip implementasi

- Gunakan model entity dan event dari `opticargo-shared`; jangan membuat contract lintas repository versi lokal.
- Event hanya menjadi trigger. Projection final dibangun dari data canonical PostgreSQL, bukan mempercayai snapshot event sebagai otoritas.
- Gunakan stable entity ID dari PostgreSQL dan deterministic projection hash.
- Mutation Neo4j harus idempotent; duplicate event tidak boleh membuat node atau relationship ganda.
- Query package bersifat read-only terhadap transaksi dan tidak boleh menjalankan mutation PostgreSQL.
- Relationship lama yang dimiliki suatu entity harus dapat diganti secara aman saat foreign key berubah.
- Data sensitif, secret, raw payment provider data, document object key, dan document content tidak boleh diproyeksikan.
- Metrics, health, correlation ID, retry, pending reclaim, DLQ, reconciliation, dan recovery wajib dirancang sejak awal.

## Referensi file

- [`docs/SOURCE_FILE_CATALOG.md`](docs/SOURCE_FILE_CATALOG.md): tanggung jawab seluruh file source.
- [`docs/TEST_FILE_CATALOG.md`](docs/TEST_FILE_CATALOG.md): tujuan seluruh file test.
- [`FILE_MANIFEST.md`](FILE_MANIFEST.md): daftar file struktur awal.
- [`REPOSITORY_INITIALIZATION_POLICY.md`](REPOSITORY_INITIALIZATION_POLICY.md): batas perubahan sebelum implementasi dimulai.
