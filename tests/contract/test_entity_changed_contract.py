"""entity.changed validates create/update/delete and canonical aliases."""

from uuid import uuid4

from opticargo_shared.events.payloads import EntityChangedPayload, EntityChangeType

from opticargo_knowledge_graph.projections.registry import normalize_entity_type


def test_entity_change_operations_and_aliases_are_canonical() -> None:
    for operation in EntityChangeType:
        payload = EntityChangedPayload(
            entity_type="cargo-listing",
            entity_id=uuid4(),
            change_type=operation,
            entity_version="1.0",
        )
        assert payload.change_type == operation
    assert normalize_entity_type("cargo-listing") == "cargo_listing"
    assert normalize_entity_type("Bookings") == "booking"
