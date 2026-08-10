"""PostgreSQL runtime enforces read-only canonical access."""

import os

import psycopg
import pytest

from opticargo_knowledge_graph.clients.postgres import create_postgres_connection

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_FULL_INTEGRATION") != "1",
    reason="requires explicit disposable PostgreSQL runtime",
)


def test_postgres_readonly_session_selects_and_denies_write() -> None:
    connection = create_postgres_connection()
    try:
        # Keep this aligned with the production psycopg 3 dependency.  UPDATE
        # ... WHERE false is side-effect-free but still a write command, so a
        # read-only transaction must reject it.
        connection.read_only = True
        with connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM ports")
            assert cursor.fetchone()[0] >= 1
            with pytest.raises(psycopg.Error):
                cursor.execute("UPDATE ports SET name = name WHERE false")
        connection.rollback()
    finally:
        connection.close()
