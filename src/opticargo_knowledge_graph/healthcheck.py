"""CLI healthcheck entrypoint for dependency or heartbeat readiness."""

from __future__ import annotations

import os
from pathlib import Path

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.health import heartbeat_report, readiness_report


def main() -> None:
    heartbeat_path = os.getenv("GRAPH_HEARTBEAT_PATH")
    if heartbeat_path:
        report = heartbeat_report(
            Path(heartbeat_path),
            max_age_seconds=int(os.getenv("GRAPH_HEARTBEAT_MAX_AGE_SECONDS", "90")),
        )
    else:
        settings = GraphSettings.from_environment()
        driver = create_neo4j_driver(settings)
        try:
            report = readiness_report(driver)
        finally:
            driver.close()
    if report.status != "ready":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
