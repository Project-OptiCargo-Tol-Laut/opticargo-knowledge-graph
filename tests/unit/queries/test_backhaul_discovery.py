"""Regression coverage for canonical backhaul discovery query semantics."""

from opticargo_knowledge_graph.queries.backhaul_discovery import (
    find_backhaul_candidates,
    find_backhaul_graph_context,
)
from opticargo_knowledge_graph.queries.graph_context import (
    find_backhaul_graph_context as canonical_query,
)


class CaptureClient:
    def __init__(self, rows=None):
        self.rows = list(rows or [])
        self.query = ""
        self.parameters = {}

    def run(self, query, parameters=None, **kwargs):
        self.query = str(query)
        self.parameters = dict(parameters or kwargs)
        return self.rows


def test_backhaul_discovery_is_a_stable_facade() -> None:
    assert find_backhaul_graph_context is canonical_query


def test_voyage_anchor_does_not_cartesian_expand_all_ports() -> None:
    client = CaptureClient()

    find_backhaul_candidates(client, voyage_id="voyage-1")

    assert "candidate_port = voyage_port" in client.query
    assert client.parameters["voyage_id"] == "voyage-1"
    assert client.parameters["origin_port"] is None


def test_listing_availability_strings_are_cast_to_dates_before_comparison() -> None:
    client = CaptureClient()

    find_backhaul_candidates(client, voyage_id="voyage-1", tolerance_days=5)

    assert "date(listing.available_from)" in client.query
    assert "date(listing.available_until)" in client.query
    assert "listing.available_from <=" not in client.query
    assert "listing.available_until >=" not in client.query


def test_backhaul_rows_are_returned_without_query_layer_mutation() -> None:
    row = {
        "cargo_listing_id": "listing-1",
        "supplier_id": "supplier-1",
        "supplier_name": "Supplier",
        "commodity_id": "commodity-1",
        "commodity_name": "Kopra",
        "commodity_category": "food",
        "available_volume_ton": 35.6,
        "origin_port_id": "port-1",
        "origin_port_name": "Marore",
        "distance_km": 0.0,
        "available_from": "2026-08-12",
        "available_until": "2026-08-17",
    }
    client = CaptureClient([row])

    result = find_backhaul_candidates(client, voyage_id="voyage-1", limit=20)

    assert result == [row]
    assert client.parameters["limit"] == 20
