# Ownership and Dependencies

| Data/runtime | Owner | Knowledge Graph access |
|---|---|---|
| Transaction/entity canonical | Gateway/PostgreSQL | Read-only |
| Domain event/outbox | Gateway + Infra Redis Streams | Consume |
| Graph schema/projection/query | Repository ini | Read/write Neo4j sesuai runtime role |
| Vector chunk/document content | RAG/Qdrant/MinIO | Bukan owner; hanya graph context interface bila perlu |
| Query orchestration/recommendation | Agents | Mengonsumsi typed query package |
| Deployment/secret/monitoring/backup | Infra | Mengikuti contract image/command/health/metrics |
| Shared models/event | Shared | Installed dependency |

## Coupling rules

- Registry/query/schema tidak mengimpor application source Gateway.
- Agents/RAG tidak menyusun domain Cypher yang menduplikasi package.
- Query path tidak memutasi source data.
- Reconciliation membaca source dan menulis projection; tidak sebaliknya.
- Infra tidak menggandakan graph business schema.
