"""Schema/domain Cypher is owned by KG, not reconstructed by Agents or RAG."""

from tests.helpers import SOURCE_ROOT, WORKSPACE_ROOT


def test_schema_mutation_exists_only_in_knowledge_graph_repository() -> None:
    assert list((SOURCE_ROOT / "schema" / "migrations").glob("*.cypher"))
    forbidden = ("CREATE CONSTRAINT", "CREATE INDEX", "MERGE (", "DETACH DELETE")
    violations: list[str] = []
    repositories = (
        WORKSPACE_ROOT / "opticargo-agents",
        WORKSPACE_ROOT / "opticargo-rag-pipeline",
    )
    for repository in repositories:
        for path in (repository / "src").rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore").upper()
            if any(token in text for token in forbidden):
                violations.append(str(path.relative_to(WORKSPACE_ROOT)))
    assert violations == []
