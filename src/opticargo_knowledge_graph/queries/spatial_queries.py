"""Port spatial lookup helpers."""

from opticargo_knowledge_graph.queries.executor import execute_read_query


def ports_by_name(session, name: str, limit: int = 10):
    return execute_read_query(
        session,
        "ports_by_name",
        """
        MATCH (p:Port)
        WHERE toLower(p.name) CONTAINS toLower($name)
        RETURN p.id AS port_id, p.name AS port_name, p.city AS city, p.province AS province,
               p.latitude AS latitude, p.longitude AS longitude
        ORDER BY size(p.name) ASC
        LIMIT $limit
        """,
        name=name,
        limit=limit,
    )


__all__ = ["ports_by_name"]
