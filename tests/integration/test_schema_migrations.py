import os

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.schema import SchemaMigrator

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_INTEGRATION") != "1",
    reason="requires the OptiCargo Docker runtime",
)


def test_live_migrations_are_idempotent() -> None:
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            first = SchemaMigrator(session, owner="integration").apply()
            second = SchemaMigrator(session, owner="integration").apply()
        assert first.current_version == first.discovered
        assert second.applied == 0
        assert second.skipped == first.discovered
    finally:
        driver.close()
