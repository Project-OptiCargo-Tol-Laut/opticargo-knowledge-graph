from opticargo_knowledge_graph.projections.entity_builders import (
    DEFAULT_BUILDERS,
    source_checksum,
)


def test_source_checksum_is_deterministic_and_order_independent() -> None:
    assert source_checksum({"id": "1", "name": "A"}) == source_checksum({"name": "A", "id": "1"})
    assert source_checksum({"id": "1"}) != source_checksum({"id": "2"})


def test_default_registry_covers_all_source_entities() -> None:
    assert len(DEFAULT_BUILDERS) == 14
    assert {"user", "cargo_listing", "booking", "payment", "document", "review"}.issubset(
        DEFAULT_BUILDERS
    )
