"""Canonical PostgreSQL adapter opens read-only sessions and SELECT-only queries."""

import inspect

from opticargo_knowledge_graph.clients.postgres import SOURCE_QUERIES, PostgresProjectionSource


def test_postgres_projection_access_is_structurally_read_only() -> None:
    source = inspect.getsource(PostgresProjectionSource._cursor)
    assert "readonly=True" in source
    assert "autocommit=True" in source
    assert all(query.lstrip().upper().startswith("SELECT") for query in SOURCE_QUERIES.values())
    forbidden = ("INSERT ", "UPDATE ", "DELETE ", "ALTER ", "DROP ")
    assert all(
        not any(word in query.upper() for word in forbidden)
        for query in SOURCE_QUERIES.values()
    )
