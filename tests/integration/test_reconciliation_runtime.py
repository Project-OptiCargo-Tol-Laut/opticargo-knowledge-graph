"""Seeded runtime detects one controlled mismatch, repairs it, and returns clean."""

import os

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.clients.postgres import PostgresProjectionSource
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.reconciliation import Reconciler

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_SEEDED_INTEGRATION") != "1",
    reason="requires seeded PostgreSQL and Neo4j runtime",
)


def test_runtime_reconciliation_detects_and_repairs_checksum_drift() -> None:
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            port_id = session.run("MATCH (p:Port) RETURN p.id AS id ORDER BY p.id LIMIT 1").single(
                strict=True
            )["id"]
            session.run(
                "MATCH (p:Port {id: $id}) REMOVE p._source_checksum", id=port_id
            ).consume()
            detected = Reconciler(
                session,
                PostgresProjectionSource(),
                owner="integration-detect",
                entity_order=("port",),
            ).run()
            assert detected.entities[0].mismatched == 1
            repaired = Reconciler(
                session,
                PostgresProjectionSource(),
                owner="integration-repair",
                entity_order=("port",),
            ).run(repair=True)
            assert repaired.projected == 1
            clean = Reconciler(
                session,
                PostgresProjectionSource(),
                owner="integration-verify",
                entity_order=("port",),
            ).run()
            assert clean.drift == 0
    finally:
        driver.close()
