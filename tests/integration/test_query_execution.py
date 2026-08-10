import os

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.queries.analytics import port_supplier_counts

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_INTEGRATION") != "1",
    reason="requires the OptiCargo Docker runtime",
)


def test_live_graph_executes_typed_analytics_query() -> None:
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            session.run(
                "MERGE (p:Port {id: 'integration-port'}) SET p.name = 'Integration Port'"
            ).consume()
            try:
                result = port_supplier_counts(session, limit=5)
            finally:
                session.run("MATCH (p:Port {id: 'integration-port'}) DETACH DELETE p").consume()
        assert result.rows
        assert result.rows[0].port_id
    finally:
        driver.close()
