# Development Workflow

## Perubahan kecil dan dapat dibuktikan

Satu perubahan idealnya menyelesaikan satu contract atau behavior dengan test dan dokumentasi yang relevan. Hindari menggabungkan schema migration, projection behavior, query contract, worker retry, dan Infra deployment dalam satu perubahan besar.

## Isi perubahan

- Requirement dan acceptance criteria.
- File dan module in-scope.
- Shared/event/schema/query version impact.
- Migration/rebuild/rollback impact.
- Failure/retry/idempotency behavior.
- Unit/contract/integration test dan evidence.
- Health/log/metric/alert impact.
- Security/data-boundary review.

## Schema/query change

Breaking label, relationship, property, index, or result field membutuhkan ADR, migration, compatibility window, consumer test, and rebuild/rollback plan.

## Review evidence

Command, test result, coverage, migration verify, graph diff, query output, metrics/log sample sanitized, image digest, and known limitation.
