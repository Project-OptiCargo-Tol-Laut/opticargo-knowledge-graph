"""In-process Knowledge Graph client facade."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4

from opticargo_knowledge_graph.queries.graph_context import find_backhaul_graph_context


@dataclass(frozen=True)
class KnowledgeGraphClient:
    driver: Any

    def graph_context(
        self,
        *,
        correlation_id: UUID | None = None,
        voyage_id: UUID | None = None,
        origin_port: str | None = None,
        commodity: str | None = None,
        limit: int = 20,
    ):
        with self.driver.session() as session:
            return find_backhaul_graph_context(
                session,
                correlation_id=correlation_id or uuid4(),
                voyage_id=voyage_id,
                origin_port=origin_port,
                commodity=commodity,
                limit=limit,
            )


__all__ = ["KnowledgeGraphClient"]
