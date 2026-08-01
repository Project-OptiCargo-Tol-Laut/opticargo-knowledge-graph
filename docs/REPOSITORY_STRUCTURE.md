# Repository Structure

## Artifact

| Artifact | Runtime | Ingress | Consumer |
|---|---|---|---|
| Python wheel | Installed dependency | Tidak ada | Agents dan RAG |
| Graph worker image/process | Long-running internal worker | Tidak ada | Redis Streams event |
| Reconciliation image/process | Scheduled/manual job | Tidak ada | Infra scheduler/operator |
| Migration command | Pre-deploy/startup operation | Tidak ada | Infra deployment |
| Diagnostic commands | One-shot internal tooling | Tidak ada | Developer/operator |

## Dependency direction

```text
contracts / models / protocols / serialization
              ↑
     projections / queries / schema
              ↑
 worker / reconciliation / CLI composition
              ↑
 PostgreSQL / Redis / Neo4j adapters
```

Domain module menerima protocol/adapter melalui dependency injection. SDK connection tidak dibuat saat package import.
