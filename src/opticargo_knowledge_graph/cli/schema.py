"""Print schema migration files."""

from __future__ import annotations

from opticargo_knowledge_graph.schema.migrator import migration_files


def main() -> int:
    for path in migration_files():
        print(path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["main"]
