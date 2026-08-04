"""Underserved insight means an active destination with at most one supplier."""

import os

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.queries.analytics import underserved_ports

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_SEEDED_INTEGRATION") != "1",
    reason="requires curated seeded graph dataset",
)


def test_underserved_definition_is_explainable_on_seeded_graph() -> None:
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            insights = underserved_ports(session, maximum_suppliers=1, limit=100).rows
        assert insights
        assert all(item.supplier_count <= 1 for item in insights)
        assert all(item.active_voyage_count > 0 for item in insights)
    finally:
        driver.close()
