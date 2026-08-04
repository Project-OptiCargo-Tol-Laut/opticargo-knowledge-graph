"""Structural protocols for graph runtime dependencies."""

from __future__ import annotations

from typing import Any, Protocol


class Neo4jSession(Protocol):
    def run(self, query: str, **parameters: Any) -> Any: ...


class Neo4jDriver(Protocol):
    def session(self) -> Any: ...


class ProjectionHandler(Protocol):
    def project(self, session: Neo4jSession, event: Any) -> Any: ...


class ProjectionSource(Protocol):
    def fetch(self, entity_type: str, entity_id: str) -> dict[str, Any] | None: ...


__all__ = ["Neo4jDriver", "Neo4jSession", "ProjectionHandler", "ProjectionSource"]
