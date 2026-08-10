"""Only ordered KG migrations may own executable Neo4j schema statements."""

from __future__ import annotations

import pytest

from opticargo_knowledge_graph.schema.migrator import migration_files
from tests.helpers import SOURCE_ROOT, WORKSPACE_ROOT


def test_versioned_migrations_are_the_single_schema_source() -> None:
    migrations = migration_files()
    assert [int(path.name[:3]) for path in migrations] == list(range(1, len(migrations) + 1))
    for legacy in ("constraints.cypher", "indexes.cypher"):
        text = (SOURCE_ROOT / "schema" / legacy).read_text(encoding="utf-8")
        assert "CREATE CONSTRAINT" not in text.upper()
        assert "CREATE INDEX" not in text.upper()


def test_data_repo_does_not_own_neo4j_schema_or_driver() -> None:
    """Enforce the cross-repository boundary without depending on a legacy filename.

    ``opticargo-data`` may seed PostgreSQL and stage documents, but executable
    Neo4j schema/driver ownership belongs to ``opticargo-knowledge-graph``.
    The test scans the current data package/scripts when the sibling repo exists,
    and remains runnable in a standalone KG checkout.
    """
    data_repo = WORKSPACE_ROOT / "opticargo-data"
    if not data_repo.is_dir():
        pytest.skip("opticargo-data is not present in this standalone KG checkout")

    roots = (data_repo / "opticargo_data", data_repo / "scripts")
    forbidden = (
        "CREATE CONSTRAINT",
        "DROP CONSTRAINT",
        "CREATE INDEX",
        "DROP INDEX",
        "FROM NEO4J IMPORT",
        "IMPORT NEO4J",
        "GRAPHDATABASE",
    )
    violations: list[str] = []

    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            source = path.read_text(encoding="utf-8", errors="replace").upper()
            for pattern in forbidden:
                if pattern in source:
                    violations.append(f"{path.relative_to(data_repo).as_posix()}: {pattern}")

    assert violations == [], (
        "opticargo-data must not own Neo4j schema or driver logic; "
        f"violations={violations}"
    )
