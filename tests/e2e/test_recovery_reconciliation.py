"""A deliberately drifted seeded projection is recovered without duplicate nodes."""

import os

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.clients.postgres import PostgresProjectionSource
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.reconciliation import Reconciler

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_E2E") != "1",
    reason="requires seeded PostgreSQL and Neo4j E2E runtime",
)


def test_missed_projection_recovery_keeps_one_stable_node() -> None:
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            port_id = session.run("MATCH (p:Port) RETURN p.id AS id ORDER BY p.id LIMIT 1").single(
                strict=True
            )["id"]
            session.run(
                "MATCH (p:Port {id: $id}) REMOVE p._source_checksum",
                id=port_id,
            ).consume()
            report = Reconciler(
                session,
                PostgresProjectionSource(),
                owner="e2e-recovery",
                entity_order=("port",),
            ).run(repair=True)
            assert report.entities[0].mismatched == report.entities[0].projected == 1
            count = session.run(
                "MATCH (p:Port {id: $id}) RETURN count(p) AS count",
                id=port_id,
            ).single(strict=True)["count"]
            assert count == 1
    finally:
        driver.close()
