"""CLI factory passes validated settings to the Neo4j adapter."""

from opticargo_knowledge_graph.cli import factory
from opticargo_knowledge_graph.config import GraphSettings


def test_factory_uses_environment_settings(monkeypatch) -> None:
    settings = GraphSettings(neo4j_uri="bolt://graph:7687", neo4j_password="secret")
    captured = []
    sentinel = object()
    monkeypatch.setattr(GraphSettings, "from_environment", classmethod(lambda cls: settings))
    monkeypatch.setattr(
        factory,
        "create_neo4j_driver",
        lambda value: captured.append(value) or sentinel,
    )

    assert factory.build_driver_from_env() is sentinel
    assert captured == [settings]
