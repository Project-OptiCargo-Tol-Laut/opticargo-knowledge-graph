"""Backward-compatible Neo4j client entry point."""

from .clients.neo4j import Neo4jClient

__all__ = ["Neo4jClient"]

from contextlib import contextmanager as _contextmanager
from dataclasses import dataclass as _dataclass
from typing import Any as _Any
from uuid import UUID as _UUID, uuid4 as _uuid4

@_contextmanager
def get_session(settings=None):
    from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
    from opticargo_knowledge_graph.config import GraphSettings
    active = settings or GraphSettings.from_environment()
    driver = create_neo4j_driver(active)
    try:
        with driver.session(database=active.neo4j_database) as session:
            yield session
    finally:
        driver.close()

@_dataclass(frozen=True)
class KnowledgeGraphClient:
    driver: _Any
    database: str = "neo4j"
    def graph_context(self, *, correlation_id: _UUID | None = None, voyage_id: _UUID | None = None, origin_port: str | None = None, commodity: str | None = None, limit: int = 20):
        from opticargo_knowledge_graph.queries.graph_context import find_backhaul_graph_context
        with self.driver.session(database=self.database) as session:
            return find_backhaul_graph_context(session, correlation_id=correlation_id or _uuid4(), voyage_id=voyage_id, origin_port=origin_port, commodity=commodity, limit=limit)
