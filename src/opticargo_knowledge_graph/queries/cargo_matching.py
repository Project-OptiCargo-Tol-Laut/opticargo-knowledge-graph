from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from .executor import execute_query, execute_read_query
from .models import QueryResult, SupplierMatch


def find_matching_ships_for_cargo(
    session: Any,
    origin_port_id: str,
    destination_port_id: str,
    commodity_category: str,
    volume_needed: float | Decimal,
    time_window_start: str | datetime | None = None,
    time_window_end: str | datetime | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    if Decimal(str(volume_needed)) <= 0:
        raise ValueError("volume_needed must be positive")
    if not commodity_category.strip():
        raise ValueError("commodity_category is required")
    if limit < 1 or limit > 100:
        raise ValueError("limit must be within 1..100")

    query = """
    MATCH (voyage:Voyage)-[:DEPARTS_FROM]->(origin:Port {id: $origin_id})
    MATCH (voyage)-[:ARRIVES_AT]->(destination:Port {id: $destination_id})
    MATCH (voyage)-[:USES_SHIP]->(ship:Ship)
    OPTIONAL MATCH (voyage)-[:HAS_CAPACITY]->(capacity:CargoCapacity)
    WITH voyage, ship, capacity,
         coalesce(toFloat(capacity.available_weight_ton), toFloat(voyage.remaining_capacity_ton)) AS available
    WHERE voyage.status IN ['scheduled', 'in_transit', 'delayed']
      AND ship.status = 'active'
      AND available >= $volume_needed
      AND ($time_start IS NULL OR datetime(voyage.departure_date) >= datetime($time_start))
      AND ($time_end IS NULL OR datetime(voyage.departure_date) <= datetime($time_end))
      AND (
        capacity.cargo_type_allowed IS NULL
        OR size(capacity.cargo_type_allowed) = 0
        OR any(category IN capacity.cargo_type_allowed
               WHERE toLower(category) = toLower($commodity_category))
      )
    RETURN ship.id AS ship_id,
           ship.name AS ship_name,
           voyage.id AS voyage_id,
           available AS remaining_capacity_ton,
           toString(voyage.departure_date) AS departure_date,
           toString(voyage.arrival_date) AS arrival_date,
           voyage.route_id AS route_id
    ORDER BY datetime(voyage.departure_date) ASC, available DESC
    LIMIT $limit
    """
    def iso(value: str | datetime | None) -> str | None:
        return value.isoformat() if isinstance(value, datetime) else value

    return execute_query(
        session,
        query,
        {
            "origin_id": origin_port_id,
            "destination_id": destination_port_id,
            "commodity_category": commodity_category,
            "volume_needed": float(volume_needed),
            "time_start": iso(time_window_start),
            "time_end": iso(time_window_end),
            "limit": limit,
        },
        query_name="cargo_matching",
    )


def candidate_suppliers(
    session: Any, *, commodity: str | None = None, port_id: str | None = None, limit: int = 20
) -> QueryResult[SupplierMatch]:
    normalized_limit = max(1, min(int(limit), 100))
    normalized_commodity = commodity.strip() if commodity and commodity.strip() else None
    return execute_read_query(
        session, "candidate_suppliers",
        """
        MATCH (s:Supplier)-[:LOCATED_AT]->(p:Port)
        MATCH (s)-[:SUPPLIES]->(c:Commodity)
        WHERE ($commodity IS NULL OR toLower(c.name) CONTAINS toLower($commodity))
          AND ($port_id IS NULL OR p.id = $port_id)
          AND toFloat(coalesce(s.avg_monthly_volume_ton, 0)) > 0
        RETURN s.id AS supplier_id, s.business_name AS supplier_name,
               c.id AS commodity_id, c.name AS commodity_name,
               p.id AS port_id, p.name AS port_name,
               toFloat(s.avg_monthly_volume_ton) AS available_weight_ton,
               s.rating AS rating, s.verified AS verified,
               true AS capacity_compatible, true AS schedule_compatible
        ORDER BY coalesce(s.verified, false) DESC, coalesce(s.rating, 0) DESC, s.id ASC
        LIMIT $limit
        """,
        row_factory=SupplierMatch, commodity=normalized_commodity, port_id=port_id, limit=normalized_limit,
    )

def voyage_cargo_matches(
    session: Any, *, voyage_id: str, commodity: str | None = None, limit: int = 20
) -> QueryResult[SupplierMatch]:
    if not voyage_id.strip():
        raise ValueError("voyage_id cannot be empty")
    normalized_limit = max(1, min(int(limit), 100))
    normalized_commodity = commodity.strip() if commodity and commodity.strip() else None
    return execute_read_query(
        session, "voyage_cargo_matches",
        """
        MATCH (v:Voyage {id: $voyage_id})-[:ARRIVES_AT]->(p:Port)
        MATCH (s:Supplier)-[:LOCATED_AT]->(p)
        MATCH (s)-[:SUPPLIES]->(c:Commodity)
        OPTIONAL MATCH (v)-[:HAS_CAPACITY]->(capacity:CargoCapacity)
        WITH v, p, s, c, coalesce(toFloat(capacity.available_weight_ton),
                                  toFloat(v.remaining_capacity_ton), 0.0) AS remaining
        WHERE v.status IN ['scheduled', 'in_transit', 'delayed']
          AND remaining > 0
          AND toFloat(coalesce(s.avg_monthly_volume_ton, 0)) > 0
          AND ($commodity IS NULL OR toLower(c.name) CONTAINS toLower($commodity))
        WITH v, p, s, c, remaining,
             CASE WHEN toFloat(s.avg_monthly_volume_ton) > remaining
                  THEN remaining ELSE toFloat(s.avg_monthly_volume_ton) END AS offered
        RETURN s.id AS supplier_id, s.business_name AS supplier_name,
               c.id AS commodity_id, c.name AS commodity_name, p.id AS port_id,
               p.name AS port_name, v.id AS voyage_id, offered AS available_weight_ton,
               remaining AS remaining_capacity_ton, s.rating AS rating, s.verified AS verified,
               offered > 0 AND offered <= remaining AS capacity_compatible,
               v.departure_date IS NOT NULL AS schedule_compatible
        ORDER BY capacity_compatible DESC, schedule_compatible DESC,
                 coalesce(s.verified, false) DESC, coalesce(s.rating, 0) DESC, s.id ASC
        LIMIT $limit
        """,
        row_factory=SupplierMatch, voyage_id=voyage_id, commodity=normalized_commodity, limit=normalized_limit,
    )
