"""Check PostgreSQL, Redis, and Neo4j connectivity without exposing secrets."""

from __future__ import annotations

import json

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.clients.postgres import create_postgres_connection
from opticargo_knowledge_graph.clients.redis_stream import create_redis_client
from opticargo_knowledge_graph.config import GraphSettings


def main() -> int:
    settings = GraphSettings.from_environment()
    checks: dict[str, str] = {}
    failures: dict[str, str] = {}

    try:
        connection = create_postgres_connection()
        try:
            connection.set_session(readonly=True, autocommit=True)
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            checks["postgres"] = "ready"
        finally:
            connection.close()
    except Exception as exc:  # noqa: BLE001 - smoke boundary normalizes dependency errors
        failures["postgres"] = exc.__class__.__name__

    try:
        redis_client = create_redis_client(settings)
        try:
            if redis_client.ping() is not True:
                raise RuntimeError("Redis PING did not return true")
            checks["redis"] = "ready"
        finally:
            redis_client.close()
    except Exception as exc:  # noqa: BLE001
        failures["redis"] = exc.__class__.__name__

    try:
        driver = create_neo4j_driver(settings)
        try:
            driver.verify_connectivity()
            with driver.session(database=settings.neo4j_database) as session:
                session.run("RETURN 1 AS ready").consume()
            checks["neo4j"] = "ready"
        finally:
            driver.close()
    except Exception as exc:  # noqa: BLE001
        failures["neo4j"] = exc.__class__.__name__

    report = {
        "status": "ready" if not failures else "degraded",
        "checks": checks,
        "failures": failures,
    }
    print(json.dumps(report, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
