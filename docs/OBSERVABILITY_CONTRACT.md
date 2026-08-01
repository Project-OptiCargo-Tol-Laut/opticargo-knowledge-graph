# Observability Contract

## Health

Heartbeat minimal memuat state, timestamp UTC, release/git SHA, dependency status, pending count, last event reference, dan sanitized last error. Healthcheck membedakan missing, stale, degraded, dan ready.

## Logs

Structured, UTC, correlation/event/entity/message ID, operation/outcome/duration/retry. Secret, URI credential, full row, document content, and sensitive payment data di-redact.

## Metrics minimum

- Event total/duration by safe event/outcome.
- Graph sync lag.
- Pending backlog and retry/DLQ count.
- Query total/duration/error by query name.
- Reconciliation execution/duration/mismatch/repair/stale.
- Dependency up and heartbeat/build info.

Label tidak boleh memakai UUID, correlation ID, raw error message, query text, port name arbitrary, atau property user.

## Alert inputs

Service/heartbeat unavailable, pending backlog, graph sync lag, repeated DLQ/worker failure, reconciliation mismatch, schema migration failure, query latency/error. Threshold final dimiliki Infra/SRE dan harus diuji alert firing.
