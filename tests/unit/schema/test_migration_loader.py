from pathlib import Path

import pytest

from opticargo_knowledge_graph.schema.migrator import MigrationError, load_migrations


def test_loader_builds_contiguous_checksummed_migrations(tmp_path: Path) -> None:
    (tmp_path / "001_constraints.cypher").write_text(
        "// comment\nRETURN 1;\nRETURN 2;", encoding="utf-8"
    )

    migrations = load_migrations(tmp_path)

    assert migrations[0].version == 1
    assert migrations[0].statements == ("RETURN 1", "RETURN 2")
    assert migrations[0].checksum.startswith("sha256:")


def test_loader_rejects_version_gaps_and_empty_files(tmp_path: Path) -> None:
    (tmp_path / "002_indexes.cypher").write_text("RETURN 2", encoding="utf-8")
    with pytest.raises(MigrationError, match="contiguous"):
        load_migrations(tmp_path)

    (tmp_path / "001_constraints.cypher").write_text("// only comment", encoding="utf-8")
    with pytest.raises(MigrationError, match="empty"):
        load_migrations(tmp_path)
