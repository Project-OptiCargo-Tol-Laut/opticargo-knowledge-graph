"""Read-only Cypher execution with timeout and typed row construction."""

from __future__ import annotations

import re
from collections.abc import Callable
from time import perf_counter
from typing import Any, TypeVar

from neo4j import Query

from opticargo_knowledge_graph.errors import QueryError
from opticargo_knowledge_graph.metrics import QUERY_DURATION_SECONDS
from opticargo_knowledge_graph.queries.models import QueryResult

T = TypeVar("T")
FORBIDDEN_KEYWORDS = (
    "CREATE",
    "MERGE",
    "DELETE",
    "DETACH",
    "SET",
    "REMOVE",
    "DROP",
    "LOAD CSV",
    "FOREACH",
    "CALL",
)
FORBIDDEN_PATTERN = re.compile(
    r"\b(?:CREATE|MERGE|DELETE|DETACH|SET|REMOVE|DROP|FOREACH|CALL)\b|\bLOAD\s+CSV\b",
    re.IGNORECASE,
)


def validate_read_only(cypher: str) -> None:
    without_comments = re.sub(r"//.*?$|/\*.*?\*/", " ", cypher, flags=re.MULTILINE | re.DOTALL)
    if ";" in without_comments.strip().rstrip(";") or FORBIDDEN_PATTERN.search(without_comments):
        raise ValueError("Only one read-only graph query is allowed")


def execute_read_query(
    session,
    query_name: str,
    cypher: str,
    *,
    row_factory: Callable[..., T] | None = None,
    timeout_seconds: float = 5.0,
    **parameters: Any,
) -> QueryResult[T | dict[str, Any]]:
    validate_read_only(cypher)
    timeout = max(0.1, min(float(timeout_seconds), 30.0))
    started = perf_counter()
    try:
        records = session.run(Query(cypher, timeout=timeout), **parameters)
        raw_rows = [dict(record) for record in records]
    except Exception as error:
        QUERY_DURATION_SECONDS.labels(query_name=query_name, outcome="error").observe(
            perf_counter() - started
        )
        raise QueryError(
            f"Graph query '{query_name}' failed: {error.__class__.__name__}"
        ) from error
    rows: list[T | dict[str, Any]] = (
        [row_factory(**row) for row in raw_rows] if row_factory else raw_rows
    )
    QUERY_DURATION_SECONDS.labels(query_name=query_name, outcome="success").observe(
        perf_counter() - started
    )
    return QueryResult(name=query_name, rows=rows)


__all__ = [
    "FORBIDDEN_KEYWORDS",
    "execute_read_query",
    "validate_read_only",
]
