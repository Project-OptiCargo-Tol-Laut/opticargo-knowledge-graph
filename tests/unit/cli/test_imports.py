"""CLI modules import without executing runtime dependencies."""

from opticargo_knowledge_graph.cli import doctor, factory, migrate, schema


def test_cli_modules_expose_callable_entrypoints() -> None:
    assert callable(doctor.main)
    assert callable(factory.build_driver_from_env)
    assert callable(migrate.main)
    assert callable(schema.main)
