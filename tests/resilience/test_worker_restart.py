"""Restarted worker reclaims pending messages before reading new entries."""

from opticargo_knowledge_graph.projections import ProjectionRegistry, ProjectionService
from opticargo_knowledge_graph.worker import run_once
from tests.unit.test_worker import _event


class Redis:
    def __init__(self):
        self.acked = []

    def xautoclaim(self, *args, **kwargs):
        return ("0-0", [("1-0", {"event": _event("report.requested")})], [])

    def xreadgroup(self, *args, **kwargs):
        return []

    def xack(self, *args):
        self.acked.append(args)


def test_restart_reclaims_and_acks_existing_pending_entry() -> None:
    redis = Redis()
    outcomes = run_once(
        redis,
        stream="events",
        group="graph",
        consumer="worker-restarted",
        dlq_stream="dlq",
        projection_service=ProjectionService(ProjectionRegistry()),
        session_factory=lambda: None,
        block_ms=1,
        count=10,
        pending_idle_ms=1,
        max_attempts=3,
    )
    assert outcomes == {"ignored": 1}
    assert redis.acked == [("events", "graph", "1-0")]
