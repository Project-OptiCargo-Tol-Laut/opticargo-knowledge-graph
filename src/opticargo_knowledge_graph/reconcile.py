"""Nightly reconciliation command entrypoint."""

from __future__ import annotations

import argparse
import json

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.clients.postgres import PostgresProjectionSource
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.reconciliation import Reconciler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repair", action="store_true")
    parser.add_argument("--cleanup-stale", action="store_true")
    args = parser.parse_args(argv)
    if args.cleanup_stale and not args.repair:
        parser.error("--cleanup-stale requires --repair")

    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            report = Reconciler(session, PostgresProjectionSource()).run(
                repair=args.repair,
                cleanup_stale=args.cleanup_stale,
            )
        print(json.dumps(report.to_dict(), default=str, sort_keys=True))
        return 0 if report.ok else 2
    finally:
        driver.close()


if __name__ == "__main__":
    raise SystemExit(main())
