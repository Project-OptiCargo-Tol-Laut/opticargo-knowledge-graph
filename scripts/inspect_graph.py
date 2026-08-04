"""Print a read-only, secret-free diagnostic summary of the current graph."""

from __future__ import annotations

import json

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings


def main() -> int:
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            labels = {
                row["label"]: row["count"]
                for row in session.run(
                    "MATCH (n) UNWIND labels(n) AS label "
                    "RETURN label, count(*) AS count ORDER BY label"
                )
            }
            relationships = {
                row["type"]: row["count"]
                for row in session.run(
                    "MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS count ORDER BY type"
                )
            }
            migration = session.run(
                "MATCH (m:_OptiCargoSchemaMigration {status: 'applied'}) "
                "RETURN coalesce(max(m.version), 0) AS version, count(m) AS count"
            ).single(strict=True)
        print(
            json.dumps(
                {
                    "database": settings.neo4j_database,
                    "schema_version": migration["version"],
                    "applied_migrations": migration["count"],
                    "labels": labels,
                    "relationships": relationships,
                },
                sort_keys=True,
            )
        )
        return 0
    finally:
        driver.close()


if __name__ == "__main__":
    raise SystemExit(main())
