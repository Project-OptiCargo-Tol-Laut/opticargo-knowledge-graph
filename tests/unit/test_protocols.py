"""Domain protocols contain only the SDK operations required by services."""

import inspect

from opticargo_knowledge_graph.protocols import (
    Neo4jDriver,
    Neo4jSession,
    ProjectionHandler,
    ProjectionSource,
)


def test_protocol_signatures_remain_narrow() -> None:
    assert set(Neo4jSession.__dict__).intersection({"run"}) == {"run"}
    assert set(Neo4jDriver.__dict__).intersection({"session"}) == {"session"}
    assert list(inspect.signature(ProjectionSource.fetch).parameters) == [
        "self",
        "entity_type",
        "entity_id",
    ]
    assert "project" in ProjectionHandler.__dict__
