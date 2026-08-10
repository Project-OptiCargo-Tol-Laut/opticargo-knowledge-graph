"""Installed typed query package imports without creating a database driver."""

import opticargo_knowledge_graph.queries as queries


def test_query_package_public_surface_is_available() -> None:
    """Develop API stays available while final may add backward-compatible API."""
    public = set(queries.__all__)

    develop_surface = {
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
    final_surface = {
        "enrich_cargo_listing",
        "find_backhaul_candidates",
        "get_voyage_context",
        "graph_overview",
    }

    assert develop_surface <= public
    assert final_surface <= public
