from opticargo_knowledge_graph.config import GraphSettings


def test_graph_settings_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")

    assert GraphSettings.from_environment().neo4j_uri == "bolt://localhost:7687"
