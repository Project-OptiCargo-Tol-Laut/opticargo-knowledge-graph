"""Migration resources form an executable contiguous target before database apply."""

from opticargo_knowledge_graph.schema import load_migrations


def test_schema_migration_target_is_complete() -> None:
    migrations = load_migrations()
    assert [migration.version for migration in migrations] == list(range(1, 7))
    assert all(migration.statements for migration in migrations)
    assert all(migration.checksum.startswith("sha256:") for migration in migrations)
