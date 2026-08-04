"""Seeded voyage-to-destination-to-supplier journey returns typed candidates."""

import os
from uuid import uuid4

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.queries.graph_context import find_backhaul_graph_context

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_E2E") != "1",
    reason="requires seeded disposable Neo4j E2E runtime",
)


def test_backhaul_discovery_journey_has_capacity_and_candidates() -> None:
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            voyage_id = session.run(
                "MATCH (v:Voyage)-[:SINGGAH_DI {role: 'destination'}]->(p:Port) "
                "WHERE EXISTS { MATCH (:Supplier)-[:BERLOKASI_DI]->(p) } "
                "RETURN v.id AS id LIMIT 1"
            ).single(strict=True)["id"]
            context = find_backhaul_graph_context(
                session, correlation_id=uuid4(), voyage_id=voyage_id
            )
        assert context.ship_capacity and context.ship_capacity.remaining_weight_ton >= 0
        assert context.active_leg and context.active_leg.distance_nm > 0
        assert context.candidates
    finally:
        driver.close()
