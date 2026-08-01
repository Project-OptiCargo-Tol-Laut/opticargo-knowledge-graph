# Existing Implementation Review

## Runtime yang terlihat

Implementasi referensi membentuk:

- continuous `graph-worker` dengan Redis consumer group;
- one-shot `graph-reconciliation` dengan check/repair/stale mode;
- Neo4j migration runner dengan tiga versi resource;
- typed query package untuk backhaul, cargo matching, pathfinding, spatial query, dan analytics;
- CLI doctor, migrate, dan schema inspection;
- heartbeat file, healthcheck command, JSON logging/redaction, dan Prometheus metrics.

## Projection behavior yang terlihat

- Event divalidasi menggunakan `DomainEvent` dari Shared.
- Event menjadi trigger untuk membaca row canonical PostgreSQL.
- Projection plan memakai stable UUID, graph-safe property allowlist, owned relationships, dan deterministic source hash.
- Update mengganti relationship yang dimiliki entity dalam satu graph transaction.
- Delete menghapus owned relationships lalu node target.
- Alias entity type dinormalisasi melalui registry.

## Reliability behavior yang terlihat

- Consumer group creation idempotent.
- `XREADGROUP` untuk message baru dan `XAUTOCLAIM` untuk pending recovery.
- Processed-event key, retry counter/TTL, exponential backoff, sanitized DLQ, dan ACK setelah terminal outcome.
- Reconciliation memakai distributed lock, dependency order, hash comparison, check-only/repair, dan optional stale cleanup.

## Query behavior yang terlihat

- Backhaul discovery memakai voyage/origin, radius, schedule tolerance, active listing, dan capacity filter.
- Cargo matching memakai origin/destination, commodity category, available capacity, dan time window.
- Pathfinding membatasi jumlah hop.
- Spatial query mengurutkan supplier berdasarkan jarak.
- Analytics mencakup graph overview dan corridor load; PRD juga meminta network analytics/underserved supplier sebagai scope P2.

## Hal yang perlu ditinjau ulang sebelum implementasi

- Source referensi memiliki versioned migration sekaligus `constraints.cypher`/`indexes.cypher`; perlu satu source resmi.
- Default metrics port `9100` terlihat pada code referensi, tetapi file Infra yang diberikan tidak menetapkan host mapping khusus.
- Exact PostgreSQL schema/query SQL harus diselaraskan dengan migration Gateway yang final.
- Property allowlist dan PII boundary perlu disetujui lintas owner data/security.
- Query result model perlu consumer test terhadap Agents dan RAG.
- Full-text index hanya dipertahankan bila use case dan analyzer terbukti diperlukan.
