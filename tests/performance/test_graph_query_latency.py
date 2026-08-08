"""Latency budget for the primary typed GraphRAG context query."""

import os
from concurrent.futures import ThreadPoolExecutor
from statistics import median
from time import perf_counter
from uuid import uuid4

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.queries.graph_context import find_backhaul_graph_context

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_PERFORMANCE") != "1",
    reason="requires explicit seeded performance runtime",
)


def _percentile(samples: list[float], percentile: float) -> float:
    ordered = sorted(samples)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * percentile)))
    return ordered[index]


def test_graph_context_latency_percentiles() -> None:
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    iterations = int(os.getenv("GRAPH_PERF_QUERY_ITERATIONS", "24"))
    concurrency = int(os.getenv("GRAPH_PERF_QUERY_CONCURRENCY", "4"))
    p95_budget_ms = float(os.getenv("GRAPH_PERF_QUERY_P95_MS", "750"))
    try:
        with driver.session(database=settings.neo4j_database) as session:
            voyage_id = session.run(
                "MATCH (v:Voyage) RETURN v.id AS id ORDER BY v.id LIMIT 1"
            ).single(strict=True)["id"]

        def measure(_: int) -> float:
            started = perf_counter()
            with driver.session(database=settings.neo4j_database) as session:
                find_backhaul_graph_context(session, uuid4(), voyage_id=voyage_id, limit=10)
            return (perf_counter() - started) * 1000

        measure(0)  # warmup outside the reported sample
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            samples = list(pool.map(measure, range(iterations)))

        evidence = {
            "dataset": "seeded",
            "iterations": iterations,
            "concurrency": concurrency,
            "p50_ms": median(samples),
            "p95_ms": _percentile(samples, 0.95),
            "p99_ms": _percentile(samples, 0.99),
            "budget_ms": p95_budget_ms,
        }
        assert evidence["p95_ms"] <= p95_budget_ms, evidence
    finally:
        driver.close()
