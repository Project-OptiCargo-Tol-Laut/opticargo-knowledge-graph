from opticargo_knowledge_graph.clients.postgres import (
    SOURCE_QUERIES,
    normalize_postgres_dsn,
)


def test_sqlalchemy_driver_dsn_is_normalized_for_psycopg2() -> None:
    assert normalize_postgres_dsn("postgresql+psycopg://u:p@db/x") == ("postgresql://u:p@db/x")


def test_projection_source_queries_are_whitelisted_and_read_only() -> None:
    assert len(SOURCE_QUERIES) == 14
    assert {"user", "booking", "payment", "document", "review"}.issubset(SOURCE_QUERIES)
    assert all(query.lstrip().upper().startswith("SELECT") for query in SOURCE_QUERIES.values())
    assert all("password" not in query.casefold() for query in SOURCE_QUERIES.values())
