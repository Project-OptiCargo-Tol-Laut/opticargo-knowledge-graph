from opticargo_knowledge_graph.schema import load_migrations


def test_repository_migrations_are_contiguous_and_versioned() -> None:
    migrations = load_migrations()

    assert [item.version for item in migrations] == list(range(1, 7))
    assert all(item.checksum.startswith("sha256:") for item in migrations)
    assert all(item.statements for item in migrations)
