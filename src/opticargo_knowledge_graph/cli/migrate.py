from __future__ import annotations

import json

from ..config import get_settings
from ..schema import GraphMigrator
from .factory import build_driver_from_env, clients, close_all
from ..config import GraphSettings
from ..schema.migrator import apply_migrations


def run() -> None:
    settings = get_settings()
    postgres, neo4j, redis = clients(settings)
    try:
        applied = GraphMigrator(
            neo4j,
            schema_name=settings.graph_schema_name,
            target_version=settings.graph_schema_target_version,
        ).migrate()
        print(json.dumps({"status": "ok", "applied_versions": applied}))
    finally:
        close_all(postgres, neo4j, redis)


if __name__ == "__main__":
    run()


def main() -> int:
    driver = build_driver_from_env()
    settings = GraphSettings.from_environment()
    try:
        with driver.session(database=settings.neo4j_database) as session:
            count = apply_migrations(session)
    finally:
        driver.close()
    print(f"Applied {count} graph schema migrations")
    return 0
