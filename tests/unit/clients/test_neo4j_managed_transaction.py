from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest

from opticargo_knowledge_graph.clients.neo4j import Neo4jClient


class _Query:
    """Sentinel matching the API shape that caused the production regression."""

    def __init__(self, text: str, *, timeout: float | None = None) -> None:
        self.text = text
        self.timeout = timeout


class _Result:
    def __iter__(self):
        return iter(({"value": 7},))


class _Transaction:
    def __init__(self) -> None:
        self.calls: list[tuple[object, dict[str, object]]] = []

    def run(self, statement, parameters):
        # Real Neo4j ManagedTransaction.run() rejects neo4j.Query objects.
        if isinstance(statement, _Query):
            raise ValueError("Query object is only supported for session.run")
        self.calls.append((statement, parameters))
        return _Result()


class _Session:
    def __init__(self, transaction: _Transaction) -> None:
        self.transaction = transaction
        self.mode: str | None = None
        self.timeout: float | None = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None

    def execute_read(self, callback):
        self.mode = "read"
        self.timeout = getattr(callback, "_test_timeout", None)
        return callback(self.transaction)

    def execute_write(self, callback):
        self.mode = "write"
        self.timeout = getattr(callback, "_test_timeout", None)
        return callback(self.transaction)


class _Driver:
    def __init__(self, session: _Session) -> None:
        self._session = session

    def session(self, *, database: str):
        assert database == "neo4j"
        return self._session


def _unit_of_work(*, timeout=None, metadata=None):
    del metadata

    def decorate(callback):
        callback._test_timeout = timeout
        return callback

    return decorate


@pytest.mark.parametrize(
    ("readonly", "expected_mode"),
    [(True, "read"), (False, "write")],
)
def test_managed_transaction_receives_plain_cypher_text(
    monkeypatch,
    readonly: bool,
    expected_mode: str,
) -> None:
    # Simulate the relevant Neo4j driver API. The old implementation imported
    # Query here and passed it to transaction.run(), reproducing the container crash.
    monkeypatch.setitem(
        sys.modules,
        "neo4j",
        SimpleNamespace(Query=_Query, unit_of_work=_unit_of_work),
    )

    transaction = _Transaction()
    session = _Session(transaction)
    client = Neo4jClient(
        "bolt://neo4j:7687",
        "neo4j",
        "secret",
        query_timeout_seconds=3.0,
        driver=_Driver(session),
    )

    rows = client.run(
        "RETURN $value AS value",
        {"value": 7},
        readonly=readonly,
    )

    assert rows == [{"value": 7}]
    assert session.mode == expected_mode
    assert session.timeout == 3.0
    assert transaction.calls == [
        ("RETURN $value AS value", {"value": 7}),
    ]
    assert isinstance(transaction.calls[0][0], str)
