import os
from uuid import uuid4

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.queries.cargo_matching import voyage_cargo_matches
from opticargo_knowledge_graph.queries.graph_context import find_backhaul_graph_context
from opticargo_knowledge_graph.queries.pathfinding import route_paths

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_SEEDED_INTEGRATION") != "1",
    reason="requires the seeded OptiCargo Docker runtime",
)


def test_seeded_graph_supports_matching_context_and_pathfinding() -> None:
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            anchor = session.run(
                """
                MATCH (v:Voyage)-[:SINGGAH_DI {role: 'origin'}]->(origin:Port)
                MATCH (v)-[:SINGGAH_DI {role: 'destination'}]->(destination:Port)
                MATCH (:Supplier)-[:BERLOKASI_DI]->(destination)
                RETURN v.id AS voyage_id, origin.id AS origin_id,
                       destination.id AS destination_id
                ORDER BY v.id ASC LIMIT 1
                """
            ).single(strict=True)
            assert anchor is not None

            matches = voyage_cargo_matches(session, voyage_id=anchor["voyage_id"], limit=10)
            context = find_backhaul_graph_context(
                session,
                correlation_id=uuid4(),
                voyage_id=anchor["voyage_id"],
                limit=10,
            )
            paths = route_paths(
                session,
                origin_port_id=anchor["origin_id"],
                destination_port_id=anchor["destination_id"],
                max_hops=4,
            )

        assert matches.rows
        assert all(item.capacity_compatible for item in matches.rows)
        assert all(
            item.available_weight_ton <= item.remaining_capacity_ton
            for item in matches.rows
        )
        assert context.active_leg is not None
        assert context.ship_capacity is not None
        assert context.candidates
        assert paths.rows
        assert paths.rows[0].hop_count <= 4
    finally:
        driver.close()
