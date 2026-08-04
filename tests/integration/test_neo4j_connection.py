"""Neo4j runtime selects the configured database and supports owned cleanup."""

import os
from uuid import uuid4

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_INTEGRATION") != "1",
    reason="requires disposable Neo4j runtime",
)


def test_neo4j_database_roundtrip_and_cleanup() -> None:
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    identifier = str(uuid4())
    try:
        driver.verify_connectivity()
        with driver.session(database=settings.neo4j_database) as session:
            created = session.run(
                "CREATE (n:_OptiCargoIntegrationProbe {id: $id}) RETURN n.id AS id",
                id=identifier,
            ).single(strict=True)
            assert created["id"] == identifier
            session.run(
                "MATCH (n:_OptiCargoIntegrationProbe {id: $id}) DELETE n",
                id=identifier,
            ).consume()
    finally:
        driver.close()
