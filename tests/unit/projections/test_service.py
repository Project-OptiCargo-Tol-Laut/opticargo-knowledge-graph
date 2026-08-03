from opticargo_knowledge_graph.contracts import EntityChangedEvent
from opticargo_knowledge_graph.projections.registry import ProjectionRegistry
from opticargo_knowledge_graph.projections.service import ProjectionService


def test_projection_service_skips_unknown_entity() -> None:
    event = EntityChangedEvent("evt-1", "Unknown", "id-1", "updated")

    result = ProjectionService(ProjectionRegistry()).project(None, event)

    assert result.status == "skipped"
