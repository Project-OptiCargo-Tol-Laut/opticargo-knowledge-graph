from __future__ import annotations

from typing import Any

from .executor import execute_query, execute_read_query
from .models import PortResult, QueryResult


def find_suppliers_in_radius(
    session: Any,
    port_id: str,
    radius_km: float = 50.0,
    limit: int = 100,
) -> list[dict[str, Any]]:
    if radius_km <= 0 or radius_km > 2000:
        raise ValueError("radius_km must be within 0..2000")
    if limit < 1 or limit > 500:
        raise ValueError("limit must be within 1..500")
    query = """
    MATCH (anchor:Port {id: $port_id})
    MATCH (supplier:Supplier)-[:LOCATED_AT]->(supplier_port:Port)
    WITH anchor, supplier, supplier_port,
         point.distance(
           point({latitude: anchor.latitude, longitude: anchor.longitude}),
           point({latitude: supplier_port.latitude, longitude: supplier_port.longitude})
         ) / 1000.0 AS distance_km
    WHERE anchor.latitude IS NOT NULL AND anchor.longitude IS NOT NULL
      AND supplier_port.latitude IS NOT NULL AND supplier_port.longitude IS NOT NULL
      AND distance_km <= $radius_km
    RETURN supplier.id AS supplier_id,
           supplier.business_name AS supplier_name,
           supplier_port.id AS supplier_port_id,
           supplier_port.name AS supplier_port_name,
           distance_km
    ORDER BY distance_km ASC, supplier.rating DESC
    LIMIT $limit
    """
    return execute_query(
        session,
        query,
        {"port_id": port_id, "radius_km": radius_km, "limit": limit},
        query_name="suppliers_in_radius",
    )


def ports_by_name(session: Any, name: str, limit: int = 10) -> QueryResult[PortResult]:
    normalized=name.strip()
    if not normalized: raise ValueError("name cannot be empty")
    return execute_read_query(session,"ports_by_name","""
        MATCH (p:Port) WHERE toLower(p.name) CONTAINS toLower($name)
        RETURN p.id AS port_id,p.name AS port_name,p.city AS city,p.province AS province,
               p.latitude AS latitude,p.longitude AS longitude
        ORDER BY size(p.name) ASC,p.name ASC,p.id ASC LIMIT $limit
    """,row_factory=PortResult,name=normalized,limit=max(1,min(int(limit),50)))

def nearby_ports(session: Any, *, latitude: float, longitude: float, radius_km: float=250.0, limit:int=20) -> QueryResult[PortResult]:
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180: raise ValueError("Invalid latitude/longitude")
    radius=max(1.0,min(float(radius_km),5000.0))
    return execute_read_query(session,"nearby_ports","""
        MATCH (p:Port) WHERE p.latitude IS NOT NULL AND p.longitude IS NOT NULL
        WITH p, point.distance(point({latitude:p.latitude,longitude:p.longitude}),
                               point({latitude:$latitude,longitude:$longitude}))/1000.0 AS distance_km
        WHERE distance_km <= $radius_km
        RETURN p.id AS port_id,p.name AS port_name,p.city AS city,p.province AS province,
               p.latitude AS latitude,p.longitude AS longitude,distance_km
        ORDER BY distance_km ASC,p.id ASC LIMIT $limit
    """,row_factory=PortResult,latitude=float(latitude),longitude=float(longitude),radius_km=radius,limit=max(1,min(int(limit),100)))
