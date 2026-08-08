"""Deterministic direct and bounded multi-hop route queries."""

from __future__ import annotations

from opticargo_knowledge_graph.queries.executor import execute_read_query
from opticargo_knowledge_graph.queries.models import QueryResult, RouteResult


def route_paths(
    session,
    *,
    origin_port_id: str,
    destination_port_id: str,
    max_hops: int = 4,
    limit: int = 10,
) -> QueryResult[RouteResult]:
    if not origin_port_id.strip() or not destination_port_id.strip():
        raise ValueError("origin_port_id and destination_port_id are required")
    if origin_port_id == destination_port_id:
        raise ValueError("origin and destination must be different")
    hops = max(1, min(int(max_hops), 6))
    normalized_limit = max(1, min(int(limit), 50))
    cypher = f"""
        MATCH path = (origin:Port {{id: $origin_port_id}})
                     -[:TERHUBUNG_DENGAN*1..{hops}]->
                     (destination:Port {{id: $destination_port_id}})
        WHERE all(route IN relationships(path) WHERE coalesce(route.is_active, true))
          AND all(node IN nodes(path) WHERE single(x IN nodes(path) WHERE x = node))
        WITH origin, destination, path, relationships(path) AS routes
        RETURN origin.id AS origin_port_id,
               destination.id AS destination_port_id,
               [node IN nodes(path) | node.id] AS port_ids,
               [route IN routes | route.id] AS route_ids,
               size(routes) AS hop_count,
               reduce(total = 0.0, route IN routes |
                      total + coalesce(route.distance_nm, 0.0)) AS distance_nm,
               reduce(total = 0, route IN routes |
                      total + coalesce(route.estimated_days, 0)) AS estimated_days
        ORDER BY distance_nm ASC, estimated_days ASC, hop_count ASC, route_ids ASC
        LIMIT $limit
    """
    return execute_read_query(
        session,
        "route_paths",
        cypher,
        row_factory=RouteResult,
        origin_port_id=origin_port_id,
        destination_port_id=destination_port_id,
        limit=normalized_limit,
    )


def direct_routes(
    session,
    *,
    origin_port_id: str,
    destination_port_id: str,
    limit: int = 20,
) -> QueryResult[RouteResult]:
    return route_paths(
        session,
        origin_port_id=origin_port_id,
        destination_port_id=destination_port_id,
        max_hops=1,
        limit=limit,
    )


__all__ = ["direct_routes", "route_paths"]
