from opticargo_knowledge_graph.projections.registry import ProjectionRegistry


def test_projection_registry_is_case_insensitive() -> None:
    registry = ProjectionRegistry()
    handler = lambda session, payload: None

    registry.register("Supplier", handler)

    assert registry.get("supplier") is handler
