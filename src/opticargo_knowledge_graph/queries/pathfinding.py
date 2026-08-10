from __future__ import annotations

from typing import Any

from .executor import execute_query, execute_read_query
from .models import QueryResult, RouteResult


def find_shortest_transit_path(
    session: Any,
    start_port_id: str,
    end_port_id: str,
    max_hops: int = 3,
) -> list[dict[str, Any]]:
    if max_hops < 1 or max_hops > 8:
        raise ValueError("max_hops must be within 1..8")
    query = f"""
    MATCH (start:Port {{id: $start_id}}), (finish:Port {{id: $end_id}})
    MATCH path = shortestPath((start)-[:ROUTE_TO*1..{max_hops}]->(finish))
    WITH path, relationships(path) AS legs
    RETURN [node IN nodes(path) | node.id] AS port_ids,
           [node IN nodes(path) | node.name] AS port_names,
           [leg IN legs | leg.route_id] AS route_ids,
           length(path) AS total_hops,
           reduce(total = 0.0, leg IN legs | total + coalesce(toFloat(leg.distance_nm), 0.0))
             AS total_distance_nm,
           reduce(total = 0.0, leg IN legs | total + coalesce(toFloat(leg.estimated_days), 0.0))
             AS estimated_days
    """
    return execute_query(
        session,
        query,
        {"start_id": start_port_id, "end_id": end_port_id},
        query_name="shortest_transit_path",
    )


def route_paths(
    session: Any, *, origin_port_id: str, destination_port_id: str, max_hops: int = 4, limit: int = 10
) -> QueryResult[RouteResult]:
    if not origin_port_id.strip() or not destination_port_id.strip():
        raise ValueError("origin_port_id and destination_port_id are required")
    if origin_port_id == destination_port_id:
        raise ValueError("origin and destination must be different")
    hops = max(1, min(int(max_hops), 6))
    normalized_limit = max(1, min(int(limit), 50))
    cypher = f"""
        MATCH path = (origin:Port {{id: $origin_port_id}})-[:ROUTE_TO*1..{hops}]->
                     (destination:Port {{id: $destination_port_id}})
        WHERE all(route IN relationships(path) WHERE coalesce(route.is_active, true))
          AND all(node IN nodes(path) WHERE single(x IN nodes(path) WHERE x = node))
        WITH origin, destination, path, relationships(path) AS routes
        RETURN origin.id AS origin_port_id, destination.id AS destination_port_id,
               [node IN nodes(path) | node.id] AS port_ids,
               [route IN routes | route.route_id] AS route_ids,
               size(routes) AS hop_count,
               reduce(total = 0.0, route IN routes | total + coalesce(route.distance_nm, 0.0)) AS distance_nm,
               toInteger(reduce(total = 0.0, route IN routes | total + coalesce(route.estimated_days, 0.0))) AS estimated_days
        ORDER BY distance_nm ASC, estimated_days ASC, hop_count ASC
        LIMIT $limit
    """
    return execute_read_query(session, "route_paths", cypher, row_factory=RouteResult,
                              origin_port_id=origin_port_id, destination_port_id=destination_port_id,
                              limit=normalized_limit)

def direct_routes(session: Any, *, origin_port_id: str, destination_port_id: str, limit: int = 20) -> QueryResult[RouteResult]:
    return route_paths(session, origin_port_id=origin_port_id, destination_port_id=destination_port_id,
                       max_hops=1, limit=limit)
