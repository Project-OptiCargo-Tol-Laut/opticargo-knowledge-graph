# Infra Ports and Endpoints

## Acuan host port yang diberikan

| Komponen | Host port |
|---|---:|
| Public HTTP/Nginx | 8080 |
| Grafana | 3001 |
| Prometheus | 9090 |
| Alertmanager | 9093 |
| Neo4j HTTP browser/management | 7474 |
| PostgreSQL | 5433 |
| Gateway | 8000 |

## Internal container endpoints

| Dependency | Endpoint internal |
|---|---|
| PostgreSQL | `postgres:5432` |
| Redis | `redis:6379` |
| Neo4j Bolt | `neo4j:7687` |
| Neo4j HTTP | `neo4j:7474` |

Graph worker dan reconciliation tidak mempunyai public ingress. Port metrics internal belum ditentukan pada acuan Infra. Code referensi menggunakan default `9100`; angka tersebut harus dikonfirmasi dan tidak boleh dipublish ke host secara otomatis.

## Command Infra yang diberikan

```text
GRAPH_WORKER_COMMAND=python -m opticargo_knowledge_graph.worker
GRAPH_RECONCILIATION_COMMAND=python -m opticargo_knowledge_graph.reconcile
```

Command final harus memiliki contract test terhadap package entrypoint dan container working directory.
