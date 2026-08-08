"""Projection service creates and deletes one canonical node transactionally."""

import os
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.contracts import EntityChangedEvent
from opticargo_knowledge_graph.projections import ProjectionService, default_projection_registry

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_INTEGRATION") != "1",
    reason="requires disposable Neo4j runtime",
)


def test_port_projection_create_delete_roundtrip() -> None:
    identifier = str(uuid4())

    class Source:
        def fetch(self, entity_type, entity_id):
            return {
                "id": entity_id,
                "name": "Synthetic Integration Port",
                "city": "Test City",
                "province": "Test Province",
                "latitude": 0.0,
                "longitude": 100.0,
                "max_vessel_tonnage": 1000.0,
            }

    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    service = ProjectionService(default_projection_registry(), Source())
    try:
        with driver.session(database=settings.neo4j_database) as session:
            created = EntityChangedEvent(
                str(uuid4()), "port", identifier, "created", occurred_at=datetime.now(UTC)
            )
            assert service.project(session, created).status == "projected"
            node = session.run(
                "MATCH (p:Port {id: $id}) RETURN p.name AS name, p._source_checksum AS checksum",
                id=identifier,
            ).single(strict=True)
            assert node["name"] == "Synthetic Integration Port"
            assert node["checksum"].startswith("sha256:")

            deleted = EntityChangedEvent(
                str(uuid4()), "port", identifier, "deleted", occurred_at=datetime.now(UTC)
            )
            assert service.project(session, deleted).status == "deleted"
            assert session.run(
                "MATCH (p:Port {id: $id}) RETURN count(p) AS count", id=identifier
            ).single(strict=True)["count"] == 0
    finally:
        driver.close()
