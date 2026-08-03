"""Cargo matching read model helpers."""

from opticargo_knowledge_graph.queries.executor import execute_read_query


def candidate_suppliers(session, *, commodity: str | None = None, limit: int = 20):
    return execute_read_query(
        session,
        "candidate_suppliers",
        """
        MATCH (s:Supplier)-[:MENYUPLAI]->(c:Commodity)
        WHERE $commodity IS NULL OR toLower(c.name) CONTAINS toLower($commodity)
        RETURN s.id AS supplier_id, s.business_name AS supplier_name, c.id AS commodity_id, c.name AS commodity_name
        ORDER BY coalesce(s.verified, false) DESC, coalesce(s.rating, 0) DESC
        LIMIT $limit
        """,
        commodity=commodity,
        limit=limit,
    )


__all__ = ["candidate_suppliers"]
