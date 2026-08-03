"""Projection service coordinator."""

from __future__ import annotations

from opticargo_knowledge_graph.contracts import EntityChangedEvent, ProjectionResult
from opticargo_knowledge_graph.projections.registry import ProjectionRegistry


class ProjectionService:
    def __init__(self, registry: ProjectionRegistry) -> None:
        self._registry = registry

    def project(self, session, event: EntityChangedEvent) -> ProjectionResult:
        handler = self._registry.get(event.entity_type)
        if handler is None:
            return ProjectionResult(event.entity_type, event.entity_id, "skipped", "No projection handler registered")
        handler(session, event.payload)
        return ProjectionResult(event.entity_type, event.entity_id, "projected")


__all__ = ["ProjectionService"]
