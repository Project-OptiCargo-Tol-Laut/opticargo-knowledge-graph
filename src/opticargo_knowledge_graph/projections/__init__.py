"""Projection exports."""

from opticargo_knowledge_graph.projections.registry import (
    ProjectionRegistry,
    default_projection_registry,
)
from opticargo_knowledge_graph.projections.service import ProjectionService

__all__ = ["ProjectionRegistry", "ProjectionService", "default_projection_registry"]
