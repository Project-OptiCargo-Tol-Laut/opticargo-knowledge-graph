from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from .errors import LockUnavailableError
from .metrics import (
    GRAPH_RECONCILIATION_DURATION,
    GRAPH_RECONCILIATION_MISMATCH,
    GRAPH_RECONCILIATION_TOTAL,
)
from .projections.registry import ENTITY_ORDER, get_projection_spec
from .schema import GraphMigrator


@dataclass
class EntityReconciliation:
    entity_type: str
    source_count: int = 0
    graph_count: int = 0
    missing: int = 0
    mismatched: int = 0
    stale: int = 0
    repaired: int = 0
    deleted: int = 0


@dataclass
class ReconciliationReport:
    mode: str
    started_at: float
    finished_at: float = 0
    entities: list[EntityReconciliation] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        end = self.finished_at or time.time()
        return max(0.0, end - self.started_at)

    @property
    def mismatch_count(self) -> int:
        return sum(item.missing + item.mismatched + item.stale for item in self.entities)

    def as_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "duration_seconds": self.duration_seconds,
            "mismatch_count": self.mismatch_count,
            "entities": [item.__dict__ for item in self.entities],
        }


class ReconciliationService:
    def __init__(self, settings: Any, postgres: Any, neo4j: Any, redis: Any) -> None:
        self._settings = settings
        self._postgres = postgres
        self._neo4j = neo4j
        self._redis = redis

    def run(self, *, check_only: bool = False, delete_stale: bool | None = None) -> ReconciliationReport:
        mode = "check" if check_only else "repair"
        delete_stale = self._settings.graph_delete_stale if delete_stale is None else delete_stale
        token = str(uuid.uuid4())
        if not self._redis.acquire_lock(
            self._settings.scheduler_lock_key,
            token,
            self._settings.graph_reconciliation_lock_ttl_seconds,
        ):
            raise LockUnavailableError("graph reconciliation is already running")

        report = ReconciliationReport(mode=mode, started_at=time.time())
        try:
            GraphMigrator(
                self._neo4j,
                schema_name=self._settings.graph_schema_name,
                target_version=self._settings.graph_schema_target_version,
            ).migrate()
            for entity_type in ENTITY_ORDER:
                report.entities.append(
                    self._reconcile_entity(
                        entity_type,
                        check_only=check_only,
                        delete_stale=delete_stale,
                    )
                )
                self._redis.refresh_lock(
                    self._settings.scheduler_lock_key,
                    token,
                    self._settings.graph_reconciliation_lock_ttl_seconds,
                )
            report.finished_at = time.time()
            GRAPH_RECONCILIATION_TOTAL.labels(mode=mode, result="success").inc()
            return report
        except Exception:
            GRAPH_RECONCILIATION_TOTAL.labels(mode=mode, result="error").inc()
            raise
        finally:
            report.finished_at = report.finished_at or time.time()
            GRAPH_RECONCILIATION_DURATION.labels(mode=mode).observe(report.duration_seconds)
            self._redis.release_lock(self._settings.scheduler_lock_key, token)

    def _reconcile_entity(
        self,
        entity_type: str,
        *,
        check_only: bool,
        delete_stale: bool,
    ) -> EntityReconciliation:
        spec = get_projection_spec(entity_type)
        graph_state = self._neo4j.projection_state(spec.entity_type, spec.label)
        source_ids: set[str] = set()
        result = EntityReconciliation(
            entity_type=entity_type,
            graph_count=len(graph_state),
        )
        for row in self._postgres.iter_rows(
            spec.select_sql,
            batch_size=self._settings.graph_reconciliation_batch_size,
        ):
            plan = spec.builder(row)
            source_ids.add(plan.entity_id)
            result.source_count += 1
            existing_hash = graph_state.get(plan.entity_id)
            if existing_hash is None:
                result.missing += 1
                if not check_only:
                    self._neo4j.apply_projection(plan)
                    result.repaired += 1
            elif existing_hash != plan.source_hash:
                result.mismatched += 1
                if not check_only:
                    self._neo4j.apply_projection(plan)
                    result.repaired += 1

        stale_ids = set(graph_state).difference(source_ids)
        result.stale = len(stale_ids)
        if not check_only and delete_stale:
            for entity_id in sorted(stale_ids):
                self._neo4j.delete_projection(spec.entity_type, entity_id, spec.label)
                result.deleted += 1

        for kind, count in (
            ("missing", result.missing),
            ("mismatched", result.mismatched),
            ("stale", result.stale),
        ):
            GRAPH_RECONCILIATION_MISMATCH.labels(entity_type=entity_type, kind=kind).set(count)
        return result

from opticargo_knowledge_graph.compat.reconciliation import Reconciler, ReconciliationLockError
