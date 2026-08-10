"""Schema CLI prints ordered versioned migration resource names."""

from pathlib import Path

from opticargo_knowledge_graph.cli import schema


def test_schema_cli_prints_ordered_files(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        schema,
        "migration_files",
        lambda: (Path("001_constraints.cypher"), Path("002_indexes.cypher")),
    )
    assert schema.main() == 0
    assert capsys.readouterr().out.splitlines() == [
        "001_constraints.cypher",
        "002_indexes.cypher",
    ]
