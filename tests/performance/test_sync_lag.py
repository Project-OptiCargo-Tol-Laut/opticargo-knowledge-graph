"""Observed event-to-projection lag stays inside the configured alert threshold."""

import os
from datetime import UTC, datetime
from time import perf_counter
from uuid import uuid4

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.contracts import EntityChangedEvent
from opticargo_knowledge_graph.projections import ProjectionService, default_projection_registry
from tests.e2e.helpers import DictSource, cleanup_entities

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_PERFORMANCE") != "1",
    reason="requires explicit disposable Neo4j performance runtime",
)


def test_event_to_projection_sync_lag() -> None:
    identifier = str(uuid4())
    source = DictSource()
    source.put(
        "port",
        {
            "id": identifier,
            "name": "Sync Lag Port",
            "city": "Synthetic",
            "province": "Synthetic",
            "latitude": 0.0,
            "longitude": 110.0,
            "max_vessel_tonnage": 1000.0,
        },
    )
    event = EntityChangedEvent(
        str(uuid4()),
        "port",
        identifier,
        "created",
        occurred_at=datetime.now(UTC),
    )
    alert_seconds = float(os.getenv("GRAPH_PERF_SYNC_LAG_SECONDS", "5"))
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            started = perf_counter()
            result = ProjectionService(default_projection_registry(), source).project(
                session,
                event,
            )
            elapsed = perf_counter() - started
            projected_at = session.run(
                "MATCH (p:Port {id: $id}) RETURN p._projected_at AS projected_at",
                id=identifier,
            ).single(strict=True)["projected_at"]
            assert result.status == "projected"
            assert projected_at is not None
            assert elapsed <= alert_seconds, {
                "elapsed_seconds": elapsed,
                "alert_seconds": alert_seconds,
            }
            cleanup_entities(session, [identifier])
    finally:
        driver.close()
