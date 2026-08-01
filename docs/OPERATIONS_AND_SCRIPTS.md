# Operations and Commands

Runtime command yang terlihat pada acuan Infra:

```text
python -m opticargo_knowledge_graph.worker
python -m opticargo_knowledge_graph.reconcile
```

Command tambahan yang perlu disediakan melalui package entrypoint atau script thin wrapper:

- schema migrate/verify;
- dependency doctor;
- schema/query contract inspection;
- reconciliation check/repair/stale policy;
- graph count/hash/mismatch inspection;
- structure/Shared/Infra smoke;
- validation gate.

## Runbook minimum

Startup failure, migration failure, pending backlog, high sync lag, DLQ growth, PostgreSQL unavailable, Neo4j unavailable, mismatch, lock contention, stale heartbeat, query latency, rebuild, and rollback.
