"""Schema package exports migrations and the canonical schema model."""

from opticargo_knowledge_graph import schema


def test_schema_public_exports_are_complete() -> None:
    assert len(schema.CANONICAL_LABELS) == 14
    assert schema.SCHEMA_VERSION == "1.0"
    assert callable(schema.load_migrations)
    assert callable(schema.apply_migrations)
