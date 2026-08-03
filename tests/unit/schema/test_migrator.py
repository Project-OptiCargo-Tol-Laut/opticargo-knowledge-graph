from pathlib import Path

from opticargo_knowledge_graph.schema.migrator import migration_files


def test_migration_files_are_sorted(tmp_path: Path) -> None:
    (tmp_path / "002_indexes.cypher").write_text("RETURN 2", encoding="utf-8")
    (tmp_path / "001_constraints.cypher").write_text("RETURN 1", encoding="utf-8")

    assert [path.name for path in migration_files(tmp_path)] == ["001_constraints.cypher", "002_indexes.cypher"]
