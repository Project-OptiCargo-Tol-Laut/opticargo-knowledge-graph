"""Read-only graph analytics queries."""

from opticargo_knowledge_graph.queries.executor import execute_read_query


def port_supplier_counts(session, limit: int = 20):
    return execute_read_query(
        session,
        "port_supplier_counts",
        """
        MATCH (s:Supplier)-[:BERLOKASI_DI]->(p:Port)
        RETURN p.id AS port_id, p.name AS port_name, count(s) AS supplier_count
        ORDER BY supplier_count DESC
        LIMIT $limit
        """,
        limit=limit,
    )


__all__ = ["port_supplier_counts"]
