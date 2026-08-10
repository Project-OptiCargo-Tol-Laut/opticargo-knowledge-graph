"""Projection package exports the registry and transactional service."""

from opticargo_knowledge_graph import projections


def test_projection_exports_and_default_registry() -> None:
    registry = projections.default_projection_registry()
    assert set(registry.entity_types) == {
        "booking",
        "cargo_capacity",
        "cargo_listing",
        "commodity",
        "document",
        "payment",
        "port",
        "recommendation",
        "review",
        "route",
        "ship",
        "supplier",
        "user",
        "voyage",
    }
