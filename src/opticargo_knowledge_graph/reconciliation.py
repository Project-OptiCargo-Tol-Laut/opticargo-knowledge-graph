"""PostgreSQL-to-Neo4j drift detection and safe repair."""

from __future__ import annotations

import socket
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from opticargo_knowledge_graph.clients.postgres import PostgresProjectionSource
from opticargo_knowledge_graph.projections import (
    ProjectionService,
    default_projection_registry,
)
from opticargo_knowledge_graph.projections.entity_builders import source_checksum

ENTITY_ORDER = (
    "user",
    "port",
    "ship",
    "commodity",
    "route",
    "supplier",
    "voyage",
    "cargo_capacity",
)
ALL_ENTITY_ORDER = (
    *ENTITY_ORDER,
    "cargo_listing",
    "recommendation",
    "booking",
    "payment",
    "document",
    "review",
)
GRAPH_SNAPSHOT_QUERIES = {
    "user": "MATCH (n:User) RETURN n.id AS id, n._source_checksum AS checksum",
    "port": "MATCH (n:Port) RETURN n.id AS id, n._source_checksum AS checksum",
    "ship": "MATCH (n:Ship) RETURN n.id AS id, n._source_checksum AS checksum",
    "commodity": "MATCH (n:Commodity) RETURN n.id AS id, n._source_checksum AS checksum",
    "supplier": "MATCH (n:Supplier) RETURN n.id AS id, n._source_checksum AS checksum",
    "voyage": "MATCH (n:Voyage) RETURN n.id AS id, n._source_checksum AS checksum",
    "route": "MATCH (n:Route) RETURN n.id AS id, n._source_checksum AS checksum",
    "cargo_capacity": (
        "MATCH (n:CargoCapacity) RETURN n.id AS id, n._source_checksum AS checksum"
    ),
    "cargo_listing": (
        "MATCH (n:CargoListing) RETURN n.id AS id, n._source_checksum AS checksum"
    ),
    "recommendation": (
        "MATCH (n:Recommendation) RETURN n.id AS id, n._source_checksum AS checksum"
    ),
    "booking": "MATCH (n:Booking) RETURN n.id AS id, n._source_checksum AS checksum",
    "payment": "MATCH (n:Payment) RETURN n.id AS id, n._source_checksum AS checksum",
    "document": "MATCH (n:Document) RETURN n.id AS id, n._source_checksum AS checksum",
    "review": "MATCH (n:Review) RETURN n.id AS id, n._source_checksum AS checksum",
}


class ReconciliationLockError(RuntimeError):
    """Raised when another reconciliation owns the graph lock."""


@dataclass(frozen=True)
class EntityReconciliation:
    entity_type: str
    source_count: int
    graph_count: int
    missing: int = 0
    mismatched: int = 0
    stale: int = 0
    projected: int = 0
    deleted: int = 0
    failed: int = 0


@dataclass(frozen=True)
class ReconciliationReport:
    started_at: datetime
    finished_at: datetime
    repair: bool
    cleanup_stale: bool
    entities: tuple[EntityReconciliation, ...] = field(default_factory=tuple)

    @property
    def scanned(self) -> int:
        return sum(item.source_count for item in self.entities)

    @property
    def projected(self) -> int:
        return sum(item.projected for item in self.entities)

    @property
    def failed(self) -> int:
        return sum(item.failed for item in self.entities)

    @property
    def drift(self) -> int:
        return sum(item.missing + item.mismatched + item.stale for item in self.entities)

    @property
    def ok(self) -> bool:
        return self.failed == 0 and (self.repair or self.drift == 0)

    @property
    def duration_seconds(self) -> float:
        return (self.finished_at - self.started_at).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class Reconciler:
    def __init__(
        self,
        session,
        source: PostgresProjectionSource,
        *,
        owner: str | None = None,
        lock_ttl_seconds: int = 1800,
        entity_order: tuple[str, ...] = ENTITY_ORDER,
    ) -> None:
        self._session = session
        self._source = source
        self._owner = owner or f"{socket.gethostname()}-{uuid4()}"
        self._lock_ttl_seconds = max(60, lock_ttl_seconds)
        unknown = set(entity_order).difference(GRAPH_SNAPSHOT_QUERIES)
        if unknown:
            raise ValueError(f"Unsupported reconciliation entities: {sorted(unknown)}")
        self._entity_order = entity_order
        self._service = ProjectionService(default_projection_registry())

    def _acquire_lock(self) -> None:
        expires_at = datetime.now(UTC) + timedelta(seconds=self._lock_ttl_seconds)
        record = self._session.run(
            """
            MERGE (lock:_OptiCargoReconciliationLock {name: 'postgres-projection'})
            ON CREATE SET lock.owner = $owner, lock.expires_at = $expires_at
            WITH lock
            WHERE lock.owner = $owner OR lock.expires_at < datetime()
            SET lock.owner = $owner, lock.expires_at = $expires_at,
                lock.acquired_at = datetime()
            RETURN lock.owner AS owner
            """,
            owner=self._owner,
            expires_at=expires_at,
        ).single()
        if record is None or record["owner"] != self._owner:
            raise ReconciliationLockError("Graph reconciliation lock is already held")

    def _release_lock(self) -> None:
        self._session.run(
            """
            MATCH (lock:_OptiCargoReconciliationLock {
                name: 'postgres-projection', owner: $owner
            })
            SET lock.owner = null, lock.expires_at = datetime()
            """,
            owner=self._owner,
        ).consume()

    def _source_records(self, entity_type: str) -> dict[str, dict[str, Any]]:
        records = self._source.fetch_all(entity_type)
        if entity_type == "route":
            records = [record for record in records if record.get("is_active", True)]
        if entity_type == "voyage":
            records = [
                record for record in records if record.get("status") in {"scheduled", "in_transit"}
            ]
        return {str(record["id"]): record for record in records}

    def _graph_records(self, entity_type: str) -> dict[str, str | None]:
        return {
            str(record["id"]): record.get("checksum")
            for record in self._session.run(GRAPH_SNAPSHOT_QUERIES[entity_type])
            if record.get("id")
        }

    def run(self, *, repair: bool = False, cleanup_stale: bool = False) -> ReconciliationReport:
        started = datetime.now(UTC)
        self._acquire_lock()
        reports: list[EntityReconciliation] = []
        try:
            for entity_type in self._entity_order:
                source_records = self._source_records(entity_type)
                graph_records = self._graph_records(entity_type)
                source_ids = set(source_records)
                graph_ids = set(graph_records)
                missing_ids = sorted(source_ids - graph_ids)
                stale_ids = sorted(graph_ids - source_ids)
                mismatched_ids = sorted(
                    identifier
                    for identifier in source_ids & graph_ids
                    if graph_records[identifier] != source_checksum(source_records[identifier])
                )
                projected = 0
                deleted = 0
                failed = 0
                if repair:
                    for identifier in [*missing_ids, *mismatched_ids]:
                        try:
                            result = self._service.project_record(
                                self._session,
                                entity_type=entity_type,
                                entity_id=identifier,
                                operation="updated",
                                record=source_records[identifier],
                            )
                            projected += result.status == "projected"
                        except Exception:  # noqa: BLE001 - continue and report per-record failure
                            failed += 1
                    if cleanup_stale:
                        for identifier in stale_ids:
                            try:
                                result = self._service.project_record(
                                    self._session,
                                    entity_type=entity_type,
                                    entity_id=identifier,
                                    operation="deleted",
                                    record={"id": identifier},
                                )
                                deleted += result.status == "deleted"
                            except Exception:  # noqa: BLE001 - continue and report per-record failure
                                failed += 1
                reports.append(
                    EntityReconciliation(
                        entity_type=entity_type,
                        source_count=len(source_records),
                        graph_count=len(graph_records),
                        missing=len(missing_ids),
                        mismatched=len(mismatched_ids),
                        stale=len(stale_ids),
                        projected=projected,
                        deleted=deleted,
                        failed=failed,
                    )
                )
        finally:
            self._release_lock()
        return ReconciliationReport(
            started_at=started,
            finished_at=datetime.now(UTC),
            repair=repair,
            cleanup_stale=cleanup_stale,
            entities=tuple(reports),
        )


def reconcile_once(
    *,
    session=None,
    source: PostgresProjectionSource | None = None,
    repair: bool = False,
    cleanup_stale: bool = False,
    scanned: int | None = None,
    projected: int | None = None,
    failed: int | None = None,
) -> ReconciliationReport:
    """Run real reconciliation; legacy counters remain for old import compatibility."""
    if session is None:
        now = datetime.now(UTC)
        legacy = EntityReconciliation(
            entity_type="legacy",
            source_count=scanned or 0,
            graph_count=0,
            projected=projected or 0,
            failed=failed or 0,
        )
        return ReconciliationReport(now, now, repair, cleanup_stale, (legacy,))
    return Reconciler(session, source or PostgresProjectionSource()).run(
        repair=repair,
        cleanup_stale=cleanup_stale,
    )


__all__ = [
    "ALL_ENTITY_ORDER",
    "ENTITY_ORDER",
    "EntityReconciliation",
    "Reconciler",
    "ReconciliationLockError",
    "ReconciliationReport",
    "reconcile_once",
]
