"""Apply Neo4j schema migrations."""

from __future__ import annotations

from opticargo_knowledge_graph.cli.factory import build_driver_from_env
from opticargo_knowledge_graph.schema.migrator import apply_migrations


def main() -> int:
    driver = build_driver_from_env()
    with driver.session() as session:
        count = apply_migrations(session)
    print(f"Applied {count} graph schema migrations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["main"]
