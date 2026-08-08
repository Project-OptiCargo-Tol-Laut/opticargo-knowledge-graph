"""PostgreSQL runtime enforces read-only canonical access."""

import os

import psycopg2
import pytest

from opticargo_knowledge_graph.clients.postgres import create_postgres_connection

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_FULL_INTEGRATION") != "1",
    reason="requires explicit disposable PostgreSQL runtime",
)


def test_postgres_readonly_session_selects_and_denies_write() -> None:
    connection = create_postgres_connection()
    try:
        connection.set_session(readonly=True)
        with connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM ports")
            assert cursor.fetchone()[0] >= 1
            with pytest.raises(psycopg2.Error):
                cursor.execute("CREATE TEMP TABLE graph_write_probe(id integer)")
        connection.rollback()
    finally:
        connection.close()
