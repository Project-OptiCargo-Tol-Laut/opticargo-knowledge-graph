from __future__ import annotations

import json

from ..config import get_settings
from ..schema import GraphMigrator
from .factory import build_driver_from_env, clients, close_all
from ..health import liveness_report, readiness_report


def run() -> None:
    settings = get_settings()
    postgres, neo4j, redis = clients(settings)
    try:
        dependencies = {
            "postgres": postgres.ping(),
            "neo4j": neo4j.ping(),
            "redis": redis.ping(),
        }
        schema_version = GraphMigrator(
            neo4j,
            schema_name=settings.graph_schema_name,
            target_version=settings.graph_schema_target_version,
        ).current_version()
        payload = {
            "status": "ready" if all(dependencies.values()) else "degraded",
            "dependencies": dependencies,
            "schema_version": schema_version,
            "schema_target_version": settings.graph_schema_target_version,
            "consumer_group": settings.graph_consumer_group,
        }
        print(json.dumps(payload, indent=2))
        if payload["status"] != "ready" or schema_version < settings.graph_schema_target_version:
            raise SystemExit(1)
    finally:
        close_all(postgres, neo4j, redis)


if __name__ == "__main__":
    run()


def main() -> int:
    driver = build_driver_from_env()
    try:
        readiness = readiness_report(driver)
    finally:
        driver.close()
    payload = {
        "service": "opticargo-knowledge-graph",
        "liveness": liveness_report(),
        "readiness": readiness.to_dict(),
    }
    print(json.dumps(payload, default=str))
    return 0 if readiness.status == "ready" else 1
