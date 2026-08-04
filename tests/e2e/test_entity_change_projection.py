"""Canonical create, update, and delete events are visible atomically in Neo4j."""

import os
from uuid import uuid4

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.projections import ProjectionService, default_projection_registry
from tests.e2e.helpers import DictSource, cleanup_entities, project

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_E2E") != "1",
    reason="requires explicit disposable Neo4j E2E runtime",
)


def test_entity_create_update_delete_journey() -> None:
    identifier = str(uuid4())
    source = DictSource()
    source.put(
        "port",
        {
            "id": identifier,
            "name": "Synthetic Port v1",
            "city": "Test",
            "province": "Test",
            "latitude": 0.0,
            "longitude": 100.0,
            "max_vessel_tonnage": 1000.0,
        },
    )
    service = ProjectionService(default_projection_registry(), source)
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            assert project(session, service, "port", identifier).status == "projected"
            source.records[("port", identifier)]["name"] = "Synthetic Port v2"
            assert project(session, service, "port", identifier, "updated").status == "projected"
            name = session.run(
                "MATCH (p:Port {id: $id}) RETURN p.name AS name", id=identifier
            ).single(strict=True)["name"]
            assert name == "Synthetic Port v2"
            assert project(session, service, "port", identifier, "deleted").status == "deleted"
            count = session.run(
                "MATCH (p:Port {id: $id}) RETURN count(p) AS count", id=identifier
            ).single(strict=True)["count"]
            assert count == 0
            cleanup_entities(session, [identifier])
    finally:
        driver.close()
