from __future__ import annotations

from typing import Any

from .executor import execute_query, execute_read_query
from .models import (BookingLifecycleMetric, CorridorMetric, NetworkOverview, PortSupplierMetric, QueryResult)


def graph_overview(session: Any) -> dict[str, dict[str, int]]:
    nodes = execute_query(
        session,
        "MATCH (node) UNWIND labels(node) AS label RETURN label, count(*) AS count ORDER BY label",
        {},
        query_name="graph_overview_nodes",
    )
    relationships = execute_query(
        session,
        "MATCH ()-[rel]->() RETURN type(rel) AS relationship, count(*) AS count ORDER BY relationship",
        {},
        query_name="graph_overview_relationships",
    )
    return {
        "labels": {str(row["label"]): int(row["count"]) for row in nodes},
        "relationships": {
            str(row["relationship"]): int(row["count"]) for row in relationships
        },
    }


def corridor_load(session: Any, *, limit: int = 20) -> list[dict[str, Any]]:
    if limit < 1 or limit > 100:
        raise ValueError("limit must be within 1..100")
    query = """
    MATCH (voyage:Voyage)-[:DEPARTS_FROM]->(origin:Port)
    MATCH (voyage)-[:ARRIVES_AT]->(destination:Port)
    RETURN origin.id AS origin_port_id,
           origin.name AS origin_port_name,
           destination.id AS destination_port_id,
           destination.name AS destination_port_name,
           count(voyage) AS voyage_count,
           sum(coalesce(toFloat(voyage.used_capacity_ton), 0.0)) AS used_capacity_ton,
           sum(coalesce(toFloat(voyage.total_capacity_ton), 0.0)) AS total_capacity_ton
    ORDER BY voyage_count DESC
    LIMIT $limit
    """
    return execute_query(
        session,
        query,
        {"limit": limit},
        query_name="corridor_load",
    )


def port_supplier_counts(session: Any, limit: int = 20) -> QueryResult[PortSupplierMetric]:
    return execute_read_query(session, "port_supplier_counts", """
        MATCH (p:Port)
        OPTIONAL MATCH (s:Supplier)-[:LOCATED_AT]->(p)
        OPTIONAL MATCH (s)-[:SUPPLIES]->(commodity:Commodity)
        OPTIONAL MATCH (voyage:Voyage)-[:ARRIVES_AT]->(p)
        WITH p, collect(DISTINCT s) AS suppliers, count(DISTINCT commodity) AS commodity_count,
             collect(DISTINCT voyage) AS voyages
        RETURN p.id AS port_id, p.name AS port_name, size(suppliers) AS supplier_count,
               size([supplier IN suppliers WHERE coalesce(supplier.verified, false)]) AS verified_supplier_count,
               commodity_count,
               size([v IN voyages WHERE v.status IN ['scheduled','in_transit','delayed']]) AS active_voyage_count,
               reduce(total=0.0, v IN voyages | total + coalesce(v.remaining_capacity_ton,0.0)) AS remaining_capacity_ton
        ORDER BY supplier_count DESC, remaining_capacity_ton DESC, p.id ASC LIMIT $limit
    """, row_factory=PortSupplierMetric, limit=max(1,min(int(limit),100)))

def network_overview(session: Any) -> QueryResult[NetworkOverview]:
    return execute_read_query(session, "network_overview", """
        MATCH (port:Port) WITH count(DISTINCT port) AS port_count
        OPTIONAL MATCH (route:Route) WHERE coalesce(route.is_active,true)
        WITH port_count, count(DISTINCT route) AS route_count
        OPTIONAL MATCH (voyage:Voyage) WHERE voyage.status IN ['scheduled','in_transit','delayed']
        WITH port_count, route_count, collect(DISTINCT voyage) AS voyages
        OPTIONAL MATCH (supplier:Supplier)
        WITH port_count, route_count, voyages, count(DISTINCT supplier) AS supplier_count
        OPTIONAL MATCH (commodity:Commodity)
        RETURN port_count, route_count, size(voyages) AS active_voyage_count, supplier_count,
               count(DISTINCT commodity) AS commodity_count,
               reduce(total=0.0, voyage IN voyages | total + coalesce(voyage.remaining_capacity_ton,0.0)) AS remaining_capacity_ton
    """, row_factory=NetworkOverview)

def corridor_metrics(session: Any, limit: int = 50) -> QueryResult[CorridorMetric]:
    return execute_read_query(session, "corridor_metrics", """
        MATCH (route:Route)-[:ORIGIN_PORT]->(origin:Port)
        MATCH (route)-[:DESTINATION_PORT]->(destination:Port)
        OPTIONAL MATCH (voyage:Voyage)-[:FOLLOWS_ROUTE]->(route)
        WITH route, origin, destination, [v IN collect(DISTINCT voyage) WHERE v IS NULL OR v.status IN ['scheduled','in_transit','delayed']] AS voyages
        RETURN route.id AS route_id, origin.id AS origin_port_id, destination.id AS destination_port_id,
               coalesce(route.distance_nm,0.0) AS distance_nm,
               size([v IN voyages WHERE v IS NOT NULL]) AS active_voyage_count,
               reduce(total=0.0, v IN voyages | total + coalesce(v.remaining_capacity_ton,0.0)) AS remaining_capacity_ton
        ORDER BY active_voyage_count DESC, remaining_capacity_ton DESC, route.id ASC LIMIT $limit
    """, row_factory=CorridorMetric, limit=max(1,min(int(limit),200)))

def booking_lifecycle(session: Any, limit: int = 50) -> QueryResult[BookingLifecycleMetric]:
    return execute_read_query(session, "booking_lifecycle", """
        MATCH (booking:Booking)
        OPTIONAL MATCH (payment:Payment)-[:PAYS_FOR]->(booking)
        OPTIONAL MATCH (review:Review)-[:FOR_BOOKING]->(booking)
        RETURN booking.id AS booking_id, booking.status AS booking_status,
               count(DISTINCT payment) AS payment_count, coalesce(sum(DISTINCT payment.amount),0.0) AS paid_amount,
               count(DISTINCT review) AS review_count, avg(DISTINCT review.rating) AS average_rating
        ORDER BY booking.id ASC LIMIT $limit
    """, row_factory=BookingLifecycleMetric, limit=max(1,min(int(limit),200)))

def underserved_ports(session: Any, *, maximum_suppliers: int = 1, limit: int = 20) -> QueryResult[PortSupplierMetric]:
    base = port_supplier_counts(session, limit=max(limit,100))
    rows=[row for row in base.rows if row.supplier_count <= max(0,int(maximum_suppliers)) and row.active_voyage_count > 0]
    return QueryResult(name="underserved_ports", rows=rows[:max(1,min(int(limit),100))])
