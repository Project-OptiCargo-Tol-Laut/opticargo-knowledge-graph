"""Neo4j adapter passes URI and auth without logging or rewriting credentials."""

import neo4j

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings


def test_neo4j_factory_uses_explicit_settings(monkeypatch) -> None:
    calls = []
    sentinel = object()
    monkeypatch.setattr(
        neo4j.GraphDatabase,
        "driver",
        lambda uri, auth: calls.append((uri, auth)) or sentinel,
    )
    settings = GraphSettings(
        neo4j_uri="bolt://graph:7687",
        neo4j_user="runtime",
        neo4j_password="secret",
    )

    assert create_neo4j_driver(settings) is sentinel
    assert calls == [("bolt://graph:7687", ("runtime", "secret"))]
