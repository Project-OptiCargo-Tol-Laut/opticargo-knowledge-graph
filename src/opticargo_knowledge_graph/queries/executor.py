from __future__ import annotations

import re
import time
from collections.abc import Callable, Mapping
from typing import Any, TypeVar

from ..metrics import GRAPH_QUERY_DURATION, GRAPH_QUERY_TOTAL
from .models import QueryResult

T = TypeVar("T")

FORBIDDEN_PATTERN = re.compile(
    r"\b(?:CREATE|MERGE|DELETE|DETACH|SET|REMOVE|DROP|FOREACH|CALL)\b|\bLOAD\s+CSV\b",
    re.IGNORECASE,
)


def validate_read_only(cypher: str) -> None:
    without_comments = re.sub(r"//.*?$|/\*.*?\*/", " ", cypher, flags=re.MULTILINE | re.DOTALL)
    stripped = without_comments.strip()
    if ";" in stripped.rstrip(";") or FORBIDDEN_PATTERN.search(stripped):
        raise ValueError("Only one read-only graph query is allowed")


def execute_query(
    client_or_session: Any,
    query: str,
    parameters: Mapping[str, Any],
    *,
    query_name: str,
) -> list[dict[str, Any]]:
    validate_read_only(query)
    started = time.perf_counter()
    try:
        if hasattr(client_or_session, "run"):
            try:
                result = client_or_session.run(query, parameters)
            except TypeError:
                result = client_or_session.run(query, **dict(parameters))
        else:
            raise TypeError("graph query executor requires a Neo4j client or session")
        rows = result if isinstance(result, list) else [dict(record) for record in result]
        GRAPH_QUERY_TOTAL.labels(query_name=query_name, result="success").inc()
        return [dict(row) for row in rows]
    except Exception:
        GRAPH_QUERY_TOTAL.labels(query_name=query_name, result="error").inc()
        raise
    finally:
        GRAPH_QUERY_DURATION.labels(query_name=query_name).observe(time.perf_counter() - started)


__all__ = ["execute_query", "validate_read_only"]


def execute_read_query(
    client_or_session: Any,
    query_name: str,
    cypher: str,
    *,
    row_factory: Callable[..., T] | None = None,
    timeout_seconds: float = 5.0,
    **parameters: Any,
) -> QueryResult[T | dict[str, Any]]:
    """Develop-compatible typed query wrapper using the final safe executor."""
    validate_read_only(cypher)
    # Use a transaction timeout when a raw Neo4j session is supplied. The final
    # Neo4jClient already wraps queries with its configured timeout.
    if hasattr(client_or_session, "run") and client_or_session.__class__.__name__ != "Neo4jClient":
        try:
            from neo4j import Query
            query_obj: Any = Query(cypher, timeout=max(0.1, min(float(timeout_seconds), 30.0)))
            started = time.perf_counter()
            try:
                try:
                    result = client_or_session.run(query_obj, **parameters)
                except TypeError:
                    result = client_or_session.run(query_obj, parameters)
                raw_rows = [dict(record) for record in result]
                GRAPH_QUERY_TOTAL.labels(query_name=query_name, result="success").inc()
            except Exception:
                GRAPH_QUERY_TOTAL.labels(query_name=query_name, result="error").inc()
                raise
            finally:
                GRAPH_QUERY_DURATION.labels(query_name=query_name).observe(time.perf_counter() - started)
        except ImportError:
            class _CompatQuery:
                def __init__(self, text: str, timeout: float) -> None:
                    self.text = text
                    self.timeout = timeout
                def __str__(self) -> str:
                    return self.text
            query_obj = _CompatQuery(cypher, max(0.1, min(float(timeout_seconds), 30.0)))
            started = time.perf_counter()
            try:
                try:
                    result = client_or_session.run(query_obj, **parameters)
                except TypeError:
                    result = client_or_session.run(query_obj, parameters)
                raw_rows = [dict(record) for record in result]
                GRAPH_QUERY_TOTAL.labels(query_name=query_name, result="success").inc()
            except Exception:
                GRAPH_QUERY_TOTAL.labels(query_name=query_name, result="error").inc()
                raise
            finally:
                GRAPH_QUERY_DURATION.labels(query_name=query_name).observe(time.perf_counter() - started)
    else:
        raw_rows = execute_query(client_or_session, cypher, parameters, query_name=query_name)
    rows = [row_factory(**row) for row in raw_rows] if row_factory else raw_rows
    return QueryResult(name=query_name, rows=rows)

__all__ = ["execute_query", "execute_read_query", "validate_read_only"]
