from opticargo_knowledge_graph.clients.postgres import (
    SOURCE_QUERIES,
    normalize_postgres_dsn,
)


def test_sqlalchemy_driver_dsn_is_normalized_for_psycopg3() -> None:
    assert normalize_postgres_dsn("postgresql+psycopg://u:p@db/x") == ("postgresql://u:p@db/x")


def test_projection_source_queries_are_whitelisted_and_read_only() -> None:
    assert len(SOURCE_QUERIES) == 14
    assert {"user", "booking", "payment", "document", "review"}.issubset(SOURCE_QUERIES)
    assert all(query.lstrip().upper().startswith("SELECT") for query in SOURCE_QUERIES.values())
    assert all("password" not in query.casefold() for query in SOURCE_QUERIES.values())

from contextlib import contextmanager

from opticargo_knowledge_graph.clients.postgres import PostgresClient


class _BatchResult:
    def mappings(self):
        return self

    def all(self):
        return []


class _RecordingConnection:
    def __init__(self) -> None:
        self.statement = None
        self.params = None

    def execute(self, statement, params=None):
        self.statement = statement
        self.params = params
        return _BatchResult()


class _RecordingPostgresClient(PostgresClient):
    def __init__(self) -> None:
        super().__init__("postgresql://unused")
        self.connection = _RecordingConnection()

    @contextmanager
    def connect(self):
        yield self.connection


def test_fetch_batch_first_page_does_not_bind_untyped_null_cursor() -> None:
    client = _RecordingPostgresClient()

    assert client.fetch_batch("SELECT id FROM users", after_id=None, limit=500) == []

    rendered = str(client.connection.statement)
    assert ":after_id" not in rendered
    assert "WHERE" not in rendered
    assert client.connection.params == {"limit": 500}


def test_fetch_batch_next_page_uses_typed_uuid_cursor() -> None:
    client = _RecordingPostgresClient()
    cursor = "778db6b1-696e-5254-9280-97d321213520"

    assert client.fetch_batch("SELECT id FROM users", after_id=cursor, limit=25) == []

    rendered = str(client.connection.statement)
    assert "WHERE id > CAST(:after_id AS uuid)" in rendered
    assert client.connection.params == {"after_id": cursor, "limit": 25}
