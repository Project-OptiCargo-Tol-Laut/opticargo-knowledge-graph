"""Projection throughput and transaction latency for canonical port events."""

import os
from statistics import median
from time import perf_counter
from uuid import uuid4

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.projections import ProjectionService, default_projection_registry
from tests.e2e.helpers import DictSource, cleanup_entities, project

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_PERFORMANCE") != "1",
    reason="requires explicit disposable Neo4j performance runtime",
)


def test_projection_throughput_and_transaction_latency() -> None:
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    count = int(os.getenv("GRAPH_PERF_PROJECTION_EVENTS", "30"))
    minimum_rate = float(os.getenv("GRAPH_PERF_PROJECTION_PER_SECOND", "8"))
    identifiers = [str(uuid4()) for _ in range(count)]
    source = DictSource()
    for index, identifier in enumerate(identifiers):
        source.put(
            "port",
            {
                "id": identifier,
                "name": f"Performance Port {index}",
                "city": "Synthetic",
                "province": "Synthetic",
                "latitude": -6.0,
                "longitude": 106.0,
                "max_vessel_tonnage": 1000.0,
            },
        )
    service = ProjectionService(default_projection_registry(), source)
    samples: list[float] = []
    try:
        with driver.session(database=settings.neo4j_database) as session:
            total_started = perf_counter()
            for identifier in identifiers:
                started = perf_counter()
                assert project(session, service, "port", identifier).status == "projected"
                samples.append((perf_counter() - started) * 1000)
            duration = perf_counter() - total_started
            projected = session.run(
                "MATCH (p:Port) WHERE p.id IN $ids RETURN count(p) AS count",
                ids=identifiers,
            ).single(strict=True)["count"]
            assert projected == count
            evidence = {
                "events": count,
                "duration_seconds": duration,
                "events_per_second": count / duration,
                "median_transaction_ms": median(samples),
                "minimum_rate": minimum_rate,
            }
            assert evidence["events_per_second"] >= minimum_rate, evidence
            cleanup_entities(session, identifiers)
    finally:
        driver.close()
