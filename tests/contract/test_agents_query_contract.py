"""Agents-facing discovery, matching, pathfinding, and analytics signatures stay stable."""

import inspect

from opticargo_knowledge_graph.queries import (
    candidate_suppliers,
    find_backhaul_graph_context,
    port_supplier_counts,
    route_paths,
    voyage_cargo_matches,
)


def test_agents_query_signatures_have_explicit_bounds_and_identifiers() -> None:
    assert "voyage_id" in inspect.signature(voyage_cargo_matches).parameters
    assert "origin_port_id" in inspect.signature(route_paths).parameters
    assert "max_hops" in inspect.signature(route_paths).parameters
    assert "limit" in inspect.signature(candidate_suppliers).parameters
    assert "limit" in inspect.signature(port_supplier_counts).parameters
    assert "correlation_id" in inspect.signature(find_backhaul_graph_context).parameters
