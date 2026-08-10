"""Seeded backhaul context returns destination-local, verified domain evidence."""

import os
from uuid import uuid4

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.queries.graph_context import find_backhaul_graph_context

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_SEEDED_INTEGRATION") != "1",
    reason="requires curated seeded graph dataset",
)


def test_backhaul_candidates_belong_to_voyage_destination() -> None:
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            voyage_id = session.run(
                "MATCH (v:Voyage)-[:SINGGAH_DI {role: 'destination'}]->(p:Port) "
                "WHERE EXISTS { MATCH (:Supplier)-[:BERLOKASI_DI]->(p) } "
                "RETURN v.id AS id ORDER BY v.id LIMIT 1"
            ).single(strict=True)["id"]
            context = find_backhaul_graph_context(
                session,
                correlation_id=uuid4(),
                voyage_id=voyage_id,
                limit=20,
            )
        assert context.active_leg is not None
        destination_port = context.active_leg.destination_port
        assert context.candidates
        assert all(
            candidate.origin_port.port_id == destination_port.port_id
            for candidate in context.candidates
        )
    finally:
        driver.close()
