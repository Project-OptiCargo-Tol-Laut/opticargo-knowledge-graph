"""Explicit integration mode proves all three runtime dependencies are reachable."""

import os

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.clients.postgres import create_postgres_connection
from opticargo_knowledge_graph.clients.redis_stream import create_redis_client
from opticargo_knowledge_graph.config import GraphSettings

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_FULL_INTEGRATION") != "1",
    reason="requires explicit disposable PostgreSQL, Redis, and Neo4j runtime",
)


def test_runtime_dependencies_respond_to_readiness_queries() -> None:
    settings = GraphSettings.from_environment()
    connection = create_postgres_connection()
    redis_client = create_redis_client(settings)
    driver = create_neo4j_driver(settings)
    try:
        connection.set_session(readonly=True, autocommit=True)
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            assert cursor.fetchone()[0] == 1
        assert redis_client.ping()
        driver.verify_connectivity()
    finally:
        connection.close()
        redis_client.close()
        driver.close()
