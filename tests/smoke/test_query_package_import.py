"""Installed typed query package imports without creating a database driver."""

import opticargo_knowledge_graph.queries as queries


def test_query_package_public_surface_is_available() -> None:
    assert set(queries.__all__) == {
        "booking_lifecycle",
        "candidate_suppliers",
        "corridor_metrics",
        "direct_routes",
        "find_backhaul_graph_context",
        "nearby_ports",
        "network_overview",
        "port_supplier_counts",
        "ports_by_name",
        "route_paths",
        "underserved_ports",
        "voyage_cargo_matches",
    }
