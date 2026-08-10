from __future__ import annotations

from typing import Any

from .executor import execute_query


def find_backhaul_candidates(
    session: Any,
    voyage_id: str | None = None,
    origin_port: str | None = None,
    search_radius_km: float = 100.0,
    tolerance_days: int = 5,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Find active listings close to a voyage destination or named origin port."""
    if not voyage_id and not origin_port:
        raise ValueError("voyage_id or origin_port is required")
    if search_radius_km <= 0 or search_radius_km > 2000:
        raise ValueError("search_radius_km must be within 0..2000")
    if tolerance_days < 0 or tolerance_days > 90:
        raise ValueError("tolerance_days must be within 0..90")
    if limit < 1 or limit > 200:
        raise ValueError("limit must be within 1..200")

    query = """
    OPTIONAL MATCH (voyage:Voyage {id: $voyage_id})-[:ARRIVES_AT]->(voyage_port:Port)
    WITH voyage, voyage_port
    MATCH (candidate_port:Port)
    WHERE ($origin_port IS NULL AND voyage_port IS NOT NULL AND candidate_port = voyage_port)
       OR ($origin_port IS NOT NULL AND toLower(candidate_port.name) CONTAINS toLower($origin_port))
    WITH voyage, voyage_port,
         CASE WHEN $origin_port IS NOT NULL THEN candidate_port ELSE voyage_port END AS anchor_port
    MATCH (listing:CargoListing)-[:ORIGINATES_AT]->(listing_port:Port)
    MATCH (listing)-[:LISTED_BY]->(supplier:Supplier)
    MATCH (listing)-[:OF_COMMODITY]->(commodity:Commodity)
    WITH voyage, anchor_port, listing, listing_port, supplier, commodity,
         point.distance(
           point({latitude: anchor_port.latitude, longitude: anchor_port.longitude}),
           point({latitude: listing_port.latitude, longitude: listing_port.longitude})
         ) / 1000.0 AS distance_km
    WHERE listing.status = 'open'
      AND anchor_port.latitude IS NOT NULL AND anchor_port.longitude IS NOT NULL
      AND listing_port.latitude IS NOT NULL AND listing_port.longitude IS NOT NULL
      AND distance_km <= $search_radius_km
      AND (voyage IS NULL OR date(listing.available_from) <=
           date(datetime(voyage.departure_date)) + duration({days: $tolerance_days}))
      AND (voyage IS NULL OR date(listing.available_until) >=
           date(datetime(voyage.departure_date)) - duration({days: $tolerance_days}))
      AND (voyage IS NULL OR toFloat(listing.volume_ton) <= toFloat(voyage.remaining_capacity_ton))
    RETURN listing.id AS cargo_listing_id,
           supplier.id AS supplier_id,
           supplier.business_name AS supplier_name,
           commodity.id AS commodity_id,
           commodity.name AS commodity_name,
           commodity.category AS commodity_category,
           listing.volume_ton AS available_volume_ton,
           listing_port.id AS origin_port_id,
           listing_port.name AS origin_port_name,
           distance_km,
           toString(listing.available_from) AS available_from,
           toString(listing.available_until) AS available_until
    ORDER BY distance_km ASC, toFloat(listing.volume_ton) DESC
    LIMIT $limit
    """
    return execute_query(
        session,
        query,
        {
            "voyage_id": voyage_id,
            "origin_port": origin_port,
            "search_radius_km": search_radius_km,
            "tolerance_days": tolerance_days,
            "limit": limit,
        },
        query_name="backhaul_discovery",
    )

# Backward-compatible develop facade: keep the canonical context query public
# while the final candidate discovery API remains available above.
from .graph_context import find_backhaul_graph_context

try:
    __all__
except NameError:
    __all__ = []
if "find_backhaul_candidates" not in __all__:
    __all__.append("find_backhaul_candidates")
if "find_backhaul_graph_context" not in __all__:
    __all__.append("find_backhaul_graph_context")
