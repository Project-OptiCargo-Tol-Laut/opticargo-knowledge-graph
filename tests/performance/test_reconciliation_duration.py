"""Full canonical reconciliation must complete inside its configured safety budget."""

import os

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.clients.postgres import PostgresProjectionSource
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.reconciliation import ENTITY_ORDER, Reconciler

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_PERFORMANCE") != "1",
    reason="requires explicit seeded PostgreSQL and Neo4j performance runtime",
)


def test_full_reconciliation_duration_and_lock_ttl_safety() -> None:
    settings = GraphSettings.from_environment()
    budget_seconds = float(os.getenv("GRAPH_PERF_RECONCILIATION_SECONDS", "30"))
    lock_ttl_seconds = int(os.getenv("GRAPH_RECONCILIATION_LOCK_TTL_SECONDS", "300"))
    driver = create_neo4j_driver(settings)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            report = Reconciler(
                session,
                PostgresProjectionSource(),
                owner="performance-reconciliation",
                lock_ttl_seconds=lock_ttl_seconds,
                entity_order=ENTITY_ORDER,
            ).run(repair=False)
        evidence = {
            "entities": ENTITY_ORDER,
            "scanned": report.scanned,
            "drift": report.drift,
            "duration_seconds": report.duration_seconds,
            "budget_seconds": budget_seconds,
            "lock_ttl_seconds": lock_ttl_seconds,
        }
        assert report.failed == 0, evidence
        assert report.duration_seconds <= budget_seconds, evidence
        assert report.duration_seconds < lock_ttl_seconds, evidence
    finally:
        driver.close()
