"""Capacity-aware supplier and voyage matching queries."""

from __future__ import annotations

from opticargo_knowledge_graph.queries.executor import execute_read_query
from opticargo_knowledge_graph.queries.models import QueryResult, SupplierMatch


def candidate_suppliers(
    session,
    *,
    commodity: str | None = None,
    port_id: str | None = None,
    limit: int = 20,
) -> QueryResult[SupplierMatch]:
    normalized_limit = max(1, min(int(limit), 100))
    normalized_commodity = commodity.strip() if commodity and commodity.strip() else None
    return execute_read_query(
        session,
        "candidate_suppliers",
        """
        MATCH (s:Supplier)-[:BERLOKASI_DI]->(p:Port)
        MATCH (s)-[:MENYUPLAI]->(c:Commodity)
        WHERE ($commodity IS NULL OR toLower(c.name) CONTAINS toLower($commodity))
          AND ($port_id IS NULL OR p.id = $port_id)
          AND coalesce(s.avg_monthly_volume_ton, 0) > 0
        RETURN s.id AS supplier_id, s.business_name AS supplier_name,
               c.id AS commodity_id, c.name AS commodity_name,
               p.id AS port_id, p.name AS port_name,
               s.avg_monthly_volume_ton AS available_weight_ton,
               s.rating AS rating, s.verified AS verified,
               true AS capacity_compatible, true AS schedule_compatible
        ORDER BY coalesce(s.verified, false) DESC,
                 coalesce(s.rating, 0) DESC, s.id ASC, c.id ASC
        LIMIT $limit
        """,
        row_factory=SupplierMatch,
        commodity=normalized_commodity,
        port_id=port_id,
        limit=normalized_limit,
    )


def voyage_cargo_matches(
    session,
    *,
    voyage_id: str,
    commodity: str | None = None,
    limit: int = 20,
) -> QueryResult[SupplierMatch]:
    if not voyage_id.strip():
        raise ValueError("voyage_id cannot be empty")
    normalized_limit = max(1, min(int(limit), 100))
    normalized_commodity = commodity.strip() if commodity and commodity.strip() else None
    return execute_read_query(
        session,
        "voyage_cargo_matches",
        """
        MATCH (v:Voyage {id: $voyage_id})
        MATCH (v)-[:SINGGAH_DI {role: 'destination'}]->(p:Port)
        MATCH (s:Supplier)-[:BERLOKASI_DI]->(p)
        MATCH (s)-[:MENYUPLAI]->(c:Commodity)
        WHERE v.status IN ['scheduled', 'in_transit']
          AND coalesce(v.remaining_capacity_ton, 0) > 0
          AND coalesce(s.avg_monthly_volume_ton, 0) > 0
          AND ($commodity IS NULL OR toLower(c.name) CONTAINS toLower($commodity))
        WITH v, p, s, c,
             CASE WHEN s.avg_monthly_volume_ton > v.remaining_capacity_ton
                  THEN v.remaining_capacity_ton ELSE s.avg_monthly_volume_ton END AS offered
        RETURN s.id AS supplier_id, s.business_name AS supplier_name,
               c.id AS commodity_id, c.name AS commodity_name,
               p.id AS port_id, p.name AS port_name, v.id AS voyage_id,
               offered AS available_weight_ton,
               v.remaining_capacity_ton AS remaining_capacity_ton,
               s.rating AS rating, s.verified AS verified,
               offered > 0 AND offered <= v.remaining_capacity_ton AS capacity_compatible,
               v.departure_date IS NOT NULL AS schedule_compatible
        ORDER BY capacity_compatible DESC, schedule_compatible DESC,
                 coalesce(s.verified, false) DESC, coalesce(s.rating, 0) DESC,
                 s.id ASC, c.id ASC
        LIMIT $limit
        """,
        row_factory=SupplierMatch,
        voyage_id=voyage_id,
        commodity=normalized_commodity,
        limit=normalized_limit,
    )


__all__ = ["candidate_suppliers", "voyage_cargo_matches"]
