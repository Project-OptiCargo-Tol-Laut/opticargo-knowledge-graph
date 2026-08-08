"""Seeded cargo matches never exceed remaining voyage weight capacity."""

import os

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.queries.cargo_matching import voyage_cargo_matches

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_SEEDED_INTEGRATION") != "1",
    reason="requires curated seeded graph dataset",
)


def test_weight_schedule_and_verification_constraints_hold() -> None:
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            voyage_id = session.run(
                "MATCH (v:Voyage)<-[:BEROPERASI_DI]-(:Ship) "
                "WHERE EXISTS { "
                "MATCH (v)-[:SINGGAH_DI {role: 'destination'}]->(p)"
                "<-[:BERLOKASI_DI]-(:Supplier) } "
                "RETURN v.id AS id ORDER BY v.id LIMIT 1"
            ).single(strict=True)["id"]
            matches = voyage_cargo_matches(session, voyage_id=voyage_id, limit=50)
        assert matches.rows
        assert all(row.capacity_compatible and row.schedule_compatible for row in matches.rows)
        assert all(
            row.available_weight_ton <= row.remaining_capacity_ton for row in matches.rows
        )
    finally:
        driver.close()
