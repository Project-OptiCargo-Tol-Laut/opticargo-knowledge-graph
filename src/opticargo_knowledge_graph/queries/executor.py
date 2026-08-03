"""Read-only Cypher execution guard."""

from __future__ import annotations

from opticargo_knowledge_graph.queries.models import QueryResult

FORBIDDEN_KEYWORDS = (" create ", " merge ", " delete ", " detach ", " set ", " remove ", " drop ")


def execute_read_query(session, name: str, cypher: str, **parameters) -> QueryResult:
    normalized = f" {cypher.casefold()} "
    if any(keyword in normalized for keyword in FORBIDDEN_KEYWORDS):
        raise ValueError("Only read-only graph queries are allowed")
    rows = [dict(record) for record in session.run(cypher, **parameters)]
    return QueryResult(name=name, rows=rows)


__all__ = ["FORBIDDEN_KEYWORDS", "execute_read_query"]
