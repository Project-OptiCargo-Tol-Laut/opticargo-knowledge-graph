from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine


class PostgresClient:
    """Read-only access to canonical application data in PostgreSQL."""

    def __init__(self, database_url: str, *, engine: Engine | None = None) -> None:
        self._database_url = database_url
        self._engine = engine

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            self._engine = create_engine(
                self._database_url,
                pool_pre_ping=True,
                pool_recycle=300,
                future=True,
            )
        return self._engine

    @contextmanager
    def connect(self) -> Iterator[Connection]:
        with self.engine.connect() as connection:
            # Neo4j is a derived read model: KG may read canonical PostgreSQL data
            # but must never mutate it. Make that invariant true at the session level.
            connection.exec_driver_sql("SET TRANSACTION READ ONLY")
            yield connection

    def ping(self) -> bool:
        with self.connect() as connection:
            return connection.execute(text("SELECT 1")).scalar_one() == 1

    def fetch_one(self, sql: str, *, entity_id: str) -> dict[str, Any] | None:
        statement = text(f"SELECT * FROM ({sql}) AS projection_source WHERE id = :entity_id")
        with self.connect() as connection:
            row = connection.execute(statement, {"entity_id": entity_id}).mappings().first()
        return dict(row) if row is not None else None

    def fetch_batch(
        self,
        sql: str,
        *,
        after_id: str | None = None,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        # Do not bind a NULL pagination cursor into an ``IS NULL`` predicate.
        # With psycopg3/PostgreSQL a query such as
        # ``(:after_id IS NULL OR id > CAST(:after_id AS uuid))`` leaves the
        # first occurrence of a NULL bind parameter untyped and PostgreSQL can
        # raise ``AmbiguousParameter``. The first page needs no cursor
        # predicate at all; subsequent pages use a typed UUID comparison.
        if after_id is None:
            statement = text(
                f"SELECT * FROM ({sql}) AS projection_source "
                "ORDER BY id LIMIT :limit"
            )
            params = {"limit": limit}
        else:
            statement = text(
                f"SELECT * FROM ({sql}) AS projection_source "
                "WHERE id > CAST(:after_id AS uuid) "
                "ORDER BY id LIMIT :limit"
            )
            params = {"after_id": after_id, "limit": limit}
        with self.connect() as connection:
            rows = connection.execute(statement, params).mappings().all()
        return [dict(row) for row in rows]

    def iter_rows(self, sql: str, *, batch_size: int = 500) -> Iterator[dict[str, Any]]:
        after_id: str | None = None
        while True:
            rows = self.fetch_batch(sql, after_id=after_id, limit=batch_size)
            if not rows:
                return
            yield from rows
            after_id = str(rows[-1]["id"])

    def count(self, sql: str) -> int:
        statement = text(f"SELECT COUNT(*) FROM ({sql}) AS projection_source")
        with self.connect() as connection:
            return int(connection.execute(statement).scalar_one())

    def close(self) -> None:
        if self._engine is not None:
            self._engine.dispose()


def as_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    return dict(value)


# Compatibility/read-audit surface derived from the canonical projection registry.
# This deliberately avoids maintaining a second copy of PostgreSQL projection SQL.
from ..projections.registry import PROJECTION_SPECS
SOURCE_QUERIES = {spec.entity_type: spec.select_sql for spec in PROJECTION_SPECS}

__all__ = ["PostgresClient", "SOURCE_QUERIES", "as_mapping"]

import os as _os
import re as _re
from contextlib import contextmanager as _contextmanager
from collections.abc import Callable as _Callable, Iterator as _Iterator
_SQLALCHEMY_DRIVER = _re.compile(r"^(postgres(?:ql)?)(?:\+[a-zA-Z0-9_]+)://")

def normalize_postgres_dsn(dsn: str) -> str:
    return _SQLALCHEMY_DRIVER.sub(r"\1://", dsn)

def create_postgres_connection(dsn: str | None = None):
    import psycopg
    active_dsn = dsn or _os.environ["DATABASE_URL"]
    return psycopg.connect(normalize_postgres_dsn(active_dsn))

class PostgresProjectionSource:
    def __init__(self, connection_factory: _Callable[[], Any] = create_postgres_connection) -> None:
        self._connection_factory = connection_factory

    @_contextmanager
    def _cursor(self) -> _Iterator[Any]:
        connection = self._connection_factory()
        cursor = None
        try:
            # psycopg3 exposes a connection-level read_only flag. This is the
            # compatibility source used by legacy projection/reconciliation APIs.
            if hasattr(connection, "read_only"):
                connection.read_only = True
            if hasattr(connection, "autocommit"):
                connection.autocommit=True
            cursor = connection.cursor()
            yield cursor
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def fetch(self, entity_type: str, entity_id: str) -> dict[str, Any] | None:
        query = SOURCE_QUERIES.get(entity_type.casefold())
        if query is None:
            return None
        with self._cursor() as cursor:
            cursor.execute(f"SELECT * FROM ({query}) AS canonical_source WHERE id = %s::text", (entity_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            if isinstance(row, dict):
                return dict(row)
            columns = [item.name if hasattr(item, "name") else item[0] for item in cursor.description]
            return dict(zip(columns, row, strict=False))

    def fetch_all(self, entity_type: str) -> list[dict[str, Any]]:
        query = SOURCE_QUERIES.get(entity_type.casefold())
        if query is None:
            raise ValueError(f"Unsupported projection entity: {entity_type}")
        with self._cursor() as cursor:
            cursor.execute(f"SELECT * FROM ({query}) AS canonical_source ORDER BY id")
            rows = cursor.fetchall()
            if not rows:
                return []
            if isinstance(rows[0], dict):
                return [dict(row) for row in rows]
            columns = [item.name if hasattr(item, "name") else item[0] for item in cursor.description]
            return [dict(zip(columns, row, strict=False)) for row in rows]
