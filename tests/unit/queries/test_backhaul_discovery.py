"""Backhaul facade must delegate to the one GraphContext implementation."""

from opticargo_knowledge_graph.queries.backhaul_discovery import find_backhaul_graph_context
from opticargo_knowledge_graph.queries.graph_context import (
    find_backhaul_graph_context as canonical_query,
)


def test_backhaul_discovery_is_a_stable_facade() -> None:
    assert find_backhaul_graph_context is canonical_query
