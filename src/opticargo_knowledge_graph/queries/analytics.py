"""Read-only network capacity and supplier analytics."""

from __future__ import annotations

from opticargo_knowledge_graph.queries.executor import execute_read_query
from opticargo_knowledge_graph.queries.models import (
    BookingLifecycleMetric,
    CorridorMetric,
    NetworkOverview,
    PortSupplierMetric,
    QueryResult,
)


def port_supplier_counts(session, limit: int = 20) -> QueryResult[PortSupplierMetric]:
    normalized_limit = max(1, min(int(limit), 100))
    return execute_read_query(
        session,
        "port_supplier_counts",
        """
        MATCH (p:Port)
        OPTIONAL MATCH (s:Supplier)-[:BERLOKASI_DI]->(p)
        OPTIONAL MATCH (s)-[:MENYUPLAI]->(commodity:Commodity)
        OPTIONAL MATCH (voyage:Voyage)-[:SINGGAH_DI {role: 'destination'}]->(p)
        WITH p, collect(DISTINCT s) AS suppliers,
             count(DISTINCT commodity) AS commodity_count,
             collect(DISTINCT voyage) AS voyages
        RETURN p.id AS port_id, p.name AS port_name,
               size(suppliers) AS supplier_count,
               size([supplier IN suppliers WHERE coalesce(supplier.verified, false)])
                   AS verified_supplier_count,
               commodity_count,
               size([v IN voyages WHERE v.status IN ['scheduled', 'in_transit']])
                   AS active_voyage_count,
               reduce(total = 0.0, v IN voyages |
                      total + coalesce(v.remaining_capacity_ton, 0.0))
                   AS remaining_capacity_ton
        ORDER BY supplier_count DESC, remaining_capacity_ton DESC, p.id ASC
        LIMIT $limit
        """,
        row_factory=PortSupplierMetric,
        limit=normalized_limit,
    )


def network_overview(session) -> QueryResult[NetworkOverview]:
    return execute_read_query(
        session,
        "network_overview",
        """
        MATCH (port:Port)
        WITH count(DISTINCT port) AS port_count
        OPTIONAL MATCH (route:Route {is_active: true})
        WITH port_count, count(DISTINCT route) AS route_count
        OPTIONAL MATCH (voyage:Voyage)
        WHERE voyage.status IN ['scheduled', 'in_transit']
        WITH port_count, route_count, collect(DISTINCT voyage) AS voyages
        OPTIONAL MATCH (supplier:Supplier)
        WITH port_count, route_count, voyages,
             count(DISTINCT supplier) AS supplier_count
        OPTIONAL MATCH (commodity:Commodity)
        RETURN port_count, route_count, size(voyages) AS active_voyage_count,
               supplier_count, count(DISTINCT commodity) AS commodity_count,
               reduce(total = 0.0, voyage IN voyages |
                   total + coalesce(voyage.remaining_capacity_ton, 0.0))
                   AS remaining_capacity_ton
        """,
        row_factory=NetworkOverview,
    )


def corridor_metrics(session, limit: int = 50) -> QueryResult[CorridorMetric]:
    normalized_limit = max(1, min(int(limit), 200))
    return execute_read_query(
        session,
        "corridor_metrics",
        """
        MATCH (route:Route)-[:ORIGIN_PORT]->(origin:Port)
        MATCH (route)-[:DESTINATION_PORT]->(destination:Port)
        OPTIONAL MATCH (voyage:Voyage)-[:FOLLOWS_ROUTE]->(route)
        WHERE voyage IS NULL OR voyage.status IN ['scheduled', 'in_transit']
        WITH route, origin, destination, collect(DISTINCT voyage) AS voyages
        RETURN route.id AS route_id, origin.id AS origin_port_id,
               destination.id AS destination_port_id,
               coalesce(route.distance_nm, 0.0) AS distance_nm,
               size([voyage IN voyages WHERE voyage IS NOT NULL]) AS active_voyage_count,
               reduce(total = 0.0, voyage IN voyages |
                   total + coalesce(voyage.remaining_capacity_ton, 0.0))
                   AS remaining_capacity_ton
        ORDER BY active_voyage_count DESC, remaining_capacity_ton DESC, route.id ASC
        LIMIT $limit
        """,
        row_factory=CorridorMetric,
        limit=normalized_limit,
    )


def booking_lifecycle(session, limit: int = 50) -> QueryResult[BookingLifecycleMetric]:
    normalized_limit = max(1, min(int(limit), 200))
    return execute_read_query(
        session,
        "booking_lifecycle",
        """
        MATCH (booking:Booking)
        OPTIONAL MATCH (payment:Payment)-[:PAYS_FOR]->(booking)
        OPTIONAL MATCH (review:Review)-[:FOR_BOOKING]->(booking)
        RETURN booking.id AS booking_id, booking.status AS booking_status,
               count(DISTINCT payment) AS payment_count,
               coalesce(sum(DISTINCT payment.amount), 0.0) AS paid_amount,
               count(DISTINCT review) AS review_count,
               avg(DISTINCT review.rating) AS average_rating
        ORDER BY booking.id ASC
        LIMIT $limit
        """,
        row_factory=BookingLifecycleMetric,
        limit=normalized_limit,
    )


def underserved_ports(
    session,
    *,
    maximum_suppliers: int = 1,
    limit: int = 20,
) -> QueryResult[PortSupplierMetric]:
    normalized_maximum = max(0, min(int(maximum_suppliers), 100))
    normalized_limit = max(1, min(int(limit), 100))
    return execute_read_query(
        session,
        "underserved_ports",
        """
        MATCH (p:Port)
        OPTIONAL MATCH (s:Supplier)-[:BERLOKASI_DI]->(p)
        OPTIONAL MATCH (s)-[:MENYUPLAI]->(commodity:Commodity)
        OPTIONAL MATCH (voyage:Voyage)-[:SINGGAH_DI {role: 'destination'}]->(p)
        WITH p, collect(DISTINCT s) AS suppliers,
             count(DISTINCT commodity) AS commodity_count,
             collect(DISTINCT voyage) AS voyages
        WITH p, suppliers, commodity_count, voyages,
             size([v IN voyages WHERE v.status IN ['scheduled', 'in_transit']])
                 AS active_voyage_count
        WHERE size(suppliers) <= $maximum_suppliers AND active_voyage_count > 0
        RETURN p.id AS port_id, p.name AS port_name,
               size(suppliers) AS supplier_count,
               size([s IN suppliers WHERE coalesce(s.verified, false)])
                   AS verified_supplier_count,
               commodity_count, active_voyage_count,
               reduce(total = 0.0, voyage IN voyages |
                   total + coalesce(voyage.remaining_capacity_ton, 0.0))
                   AS remaining_capacity_ton
        ORDER BY supplier_count ASC, active_voyage_count DESC, p.id ASC
        LIMIT $limit
        """,
        row_factory=PortSupplierMetric,
        maximum_suppliers=normalized_maximum,
        limit=normalized_limit,
    )


__all__ = [
    "booking_lifecycle",
    "corridor_metrics",
    "network_overview",
    "port_supplier_counts",
    "underserved_ports",
]
