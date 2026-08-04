"""Only ordered migrations may own executable Neo4j schema statements."""

from opticargo_knowledge_graph.schema.migrator import migration_files
from tests.helpers import SOURCE_ROOT, WORKSPACE_ROOT


def test_versioned_migrations_are_the_single_schema_source() -> None:
    migrations = migration_files()
    assert [int(path.name[:3]) for path in migrations] == list(range(1, len(migrations) + 1))
    for legacy in ("constraints.cypher", "indexes.cypher"):
        text = (SOURCE_ROOT / "schema" / legacy).read_text(encoding="utf-8")
        assert "CREATE CONSTRAINT" not in text.upper()
        assert "CREATE INDEX" not in text.upper()


def test_data_seeder_does_not_own_neo4j_schema() -> None:
    seeder = (WORKSPACE_ROOT / "opticargo-data" / "seed" / "seed_indexes.py").read_text(
        encoding="utf-8"
    )
    assert "CREATE CONSTRAINT" not in seeder.upper()
    assert "GraphDatabase" not in seeder
    assert ".session(" not in seeder
