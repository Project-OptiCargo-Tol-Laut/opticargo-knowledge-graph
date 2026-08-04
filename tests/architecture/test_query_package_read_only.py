from pathlib import Path

from opticargo_knowledge_graph.queries.executor import validate_read_only


def test_all_owned_query_modules_contain_only_read_cypher() -> None:
    query_dir = Path(__file__).parents[2] / "src" / "opticargo_knowledge_graph" / "queries"
    for path in query_dir.glob("*.py"):
        if path.name in {"executor.py", "models.py", "__init__.py"}:
            continue
        source = path.read_text(encoding="utf-8")
        # Static smoke: mutation keywords are absent from the owned query library.
        for keyword in (" DETACH DELETE ", " MERGE (", " CREATE ("):
            assert keyword not in source.upper(), path

    validate_read_only("MATCH (n) RETURN n")
