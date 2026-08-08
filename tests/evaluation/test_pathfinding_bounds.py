"""Seeded route paths are simple, bounded, and deterministically ordered by cost."""

import os

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.queries.pathfinding import route_paths

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_SEEDED_INTEGRATION") != "1",
    reason="requires curated seeded graph dataset",
)


def test_path_hops_cycles_and_distance_order() -> None:
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            anchor = session.run(
                "MATCH (a:Port)-[:TERHUBUNG_DENGAN]->(b:Port) "
                "RETURN a.id AS origin, b.id AS destination ORDER BY a.id, b.id LIMIT 1"
            ).single(strict=True)
            paths = route_paths(
                session,
                origin_port_id=anchor["origin"],
                destination_port_id=anchor["destination"],
                max_hops=4,
                limit=20,
            ).rows
        assert paths
        assert all(1 <= path.hop_count <= 4 for path in paths)
        assert all(len(path.port_ids) == len(set(path.port_ids)) for path in paths)
        assert [path.distance_nm for path in paths] == sorted(path.distance_nm for path in paths)
    finally:
        driver.close()
