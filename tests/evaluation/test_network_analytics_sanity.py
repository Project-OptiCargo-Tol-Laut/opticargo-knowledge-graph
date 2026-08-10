"""Network overview counts canonical entities without relationship multiplication."""

import os

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.queries.analytics import network_overview

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_SEEDED_INTEGRATION") != "1",
    reason="requires curated seeded graph dataset",
)


def test_network_overview_matches_direct_distinct_counts() -> None:
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            overview = network_overview(session).rows[0]
            direct = session.run(
                "MATCH (p:Port) WITH count(p) AS ports "
                "MATCH (r:Route) WITH ports, count(r) AS routes "
                "MATCH (s:Supplier) RETURN ports, routes, count(s) AS suppliers"
            ).single(strict=True)
        assert overview.port_count == direct["ports"]
        assert overview.route_count == direct["routes"]
        assert overview.supplier_count == direct["suppliers"]
        assert overview.remaining_capacity_ton >= 0
    finally:
        driver.close()
