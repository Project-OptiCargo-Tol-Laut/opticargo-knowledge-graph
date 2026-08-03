"""Route pathfinding query helpers."""

from opticargo_knowledge_graph.queries.executor import execute_read_query


def direct_routes(session, *, origin_port_id: str | None = None, destination_port_id: str | None = None, limit: int = 20):
    return execute_read_query(
        session,
        "direct_routes",
        """
        MATCH (origin:Port)-[route:TERHUBUNG_DENGAN]->(destination:Port)
        WHERE ($origin_port_id IS NULL OR origin.id = $origin_port_id)
          AND ($destination_port_id IS NULL OR destination.id = $destination_port_id)
        RETURN origin.id AS origin_port_id, destination.id AS destination_port_id,
               route.id AS route_id, route.distance_nm AS distance_nm, route.estimated_days AS estimated_days
        ORDER BY coalesce(route.distance_nm, 999999) ASC
        LIMIT $limit
        """,
        origin_port_id=origin_port_id,
        destination_port_id=destination_port_id,
        limit=limit,
    )


__all__ = ["direct_routes"]
