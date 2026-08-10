"""Canonical read-only context queries consumed by Agent/RAG packages.

Cypher ownership stays inside opticargo-knowledge-graph.  Callers receive plain
serializable dictionaries and never need to know projection labels or
relationship names.
"""
from __future__ import annotations

from typing import Any

from .executor import execute_query


def get_voyage_context(client_or_session: Any, *, voyage_id: str) -> dict[str, Any]:
    if not voyage_id.strip():
        raise ValueError("voyage_id cannot be empty")
    rows = execute_query(
        client_or_session,
        """
        MATCH (voyage:Voyage {id: $voyage_id})-[:USES_SHIP]->(ship:Ship)
        MATCH (voyage)-[:DEPARTS_FROM]->(origin:Port)
        MATCH (voyage)-[:ARRIVES_AT]->(destination:Port)
        OPTIONAL MATCH (voyage)-[:FOLLOWS_ROUTE]->(route:Route)
        OPTIONAL MATCH (voyage)-[:HAS_CAPACITY]->(capacity:CargoCapacity)
        RETURN voyage.id AS voyage_id,
               voyage.departure_date AS departure_date,
               voyage.arrival_date AS arrival_date,
               voyage.status AS status,
               coalesce(capacity.available_weight_ton, voyage.remaining_capacity_ton, 0)
                 AS remaining_weight_ton,
               coalesce(capacity.available_volume_m3, 0) AS remaining_volume_m3,
               ship.id AS ship_id,
               ship.name AS ship_name,
               route.id AS route_id,
               coalesce(route.distance_nm, 0) * 1.852 AS route_distance_km,
               origin.id AS origin_port_id,
               origin.name AS origin_port_name,
               destination.id AS destination_port_id,
               destination.name AS destination_port_name
        """,
        {"voyage_id": voyage_id},
        query_name="voyage_context",
    )
    return dict(rows[0]) if rows else {}


def enrich_cargo_listing(client_or_session: Any, *, cargo_listing_id: str) -> dict[str, Any]:
    if not cargo_listing_id.strip():
        raise ValueError("cargo_listing_id cannot be empty")
    rows = execute_query(
        client_or_session,
        """
        MATCH (listing:CargoListing {id: $listing_id})-[:LISTED_BY]->(supplier:Supplier)
        OPTIONAL MATCH (listing)-[:OF_COMMODITY]->(commodity:Commodity)
        RETURN listing.asking_price_per_ton AS asking_price_per_ton_idr,
               listing.destination_port_id AS destination_port_id,
               supplier.rating AS supplier_rating,
               supplier.success_rate AS supplier_success_rate,
               supplier.cancellation_rate AS supplier_cancellation_rate,
               commodity.certifications_required AS certifications_required,
               commodity.is_perishable AS is_perishable
        """,
        {"listing_id": cargo_listing_id},
        query_name="cargo_listing_enrichment",
    )
    return dict(rows[0]) if rows else {}


__all__ = ["enrich_cargo_listing", "get_voyage_context"]
