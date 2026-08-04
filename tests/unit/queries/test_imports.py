"""Typed public query surface imports without database side effects."""

from opticargo_knowledge_graph import queries


def test_query_exports_are_callable() -> None:
    expected = {
        "candidate_suppliers",
        "direct_routes",
        "find_backhaul_graph_context",
        "nearby_ports",
        "port_supplier_counts",
        "ports_by_name",
        "route_paths",
        "voyage_cargo_matches",
    }
    assert all(callable(getattr(queries, name)) for name in expected)
