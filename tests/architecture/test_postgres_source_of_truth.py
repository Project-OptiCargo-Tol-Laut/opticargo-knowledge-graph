"""Projection state must be resolved from canonical PostgreSQL rows."""

import inspect

from opticargo_knowledge_graph.projections.service import ProjectionService


def test_projection_service_fetches_canonical_record_before_building_graph() -> None:
    source = inspect.getsource(ProjectionService.project)
    assert "self._source.fetch" in source
    assert "event.entity_id" in source
    assert "event.payload" not in source
