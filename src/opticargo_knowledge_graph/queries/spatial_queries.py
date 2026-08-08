"""Port name and bounded geospatial lookup queries."""

from __future__ import annotations

from opticargo_knowledge_graph.queries.executor import execute_read_query
from opticargo_knowledge_graph.queries.models import PortResult, QueryResult


def ports_by_name(session, name: str, limit: int = 10) -> QueryResult[PortResult]:
    normalized_name = name.strip()
    if not normalized_name:
        raise ValueError("name cannot be empty")
    return execute_read_query(
        session,
        "ports_by_name",
        """
        MATCH (p:Port)
        WHERE toLower(p.name) CONTAINS toLower($name)
        RETURN p.id AS port_id, p.name AS port_name,
               p.city AS city, p.province AS province,
               p.latitude AS latitude, p.longitude AS longitude
        ORDER BY size(p.name) ASC, p.name ASC, p.id ASC
        LIMIT $limit
        """,
        row_factory=PortResult,
        name=normalized_name,
        limit=max(1, min(int(limit), 50)),
    )


def nearby_ports(
    session,
    *,
    latitude: float,
    longitude: float,
    radius_km: float = 250.0,
    limit: int = 20,
) -> QueryResult[PortResult]:
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError("Invalid latitude/longitude")
    radius = max(1.0, min(float(radius_km), 5000.0))
    return execute_read_query(
        session,
        "nearby_ports",
        """
        MATCH (p:Port)
        WHERE p.latitude IS NOT NULL AND p.longitude IS NOT NULL
        WITH p, point.distance(
            point({latitude: p.latitude, longitude: p.longitude}),
            point({latitude: $latitude, longitude: $longitude})
        ) / 1000.0 AS distance_km
        WHERE distance_km <= $radius_km
        RETURN p.id AS port_id, p.name AS port_name,
               p.city AS city, p.province AS province,
               p.latitude AS latitude, p.longitude AS longitude,
               distance_km
        ORDER BY distance_km ASC, p.id ASC
        LIMIT $limit
        """,
        row_factory=PortResult,
        latitude=float(latitude),
        longitude=float(longitude),
        radius_km=radius,
        limit=max(1, min(int(limit), 100)),
    )


__all__ = ["nearby_ports", "ports_by_name"]
