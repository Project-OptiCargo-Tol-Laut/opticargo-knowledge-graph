"""Canonical schema has 14 labels, owned relationships, metadata, and safe sources."""

from opticargo_knowledge_graph.clients.postgres import SOURCE_QUERIES
from opticargo_knowledge_graph.projections.entity_builders import DEFAULT_BUILDERS
from opticargo_knowledge_graph.projections.registry import PROJECTION_SPECS
from opticargo_knowledge_graph.schema import (
    CANONICAL_LABELS,
    CANONICAL_RELATIONSHIPS,
    PROJECTION_METADATA_PROPERTIES,
    SENSITIVE_PROPERTIES,
)


def test_projection_schema_is_complete_and_safe() -> None:
    assert len(CANONICAL_LABELS) == len(set(CANONICAL_LABELS)) == 14
    assert len(PROJECTION_SPECS) == len(DEFAULT_BUILDERS) == len(SOURCE_QUERIES) == 14
    assert {spec.label for spec in PROJECTION_SPECS} == set(CANONICAL_LABELS)
    assert {"PAYS_FOR", "SUPERSEDES", "ROUTE_TO", "HAS_CAPACITY"}.issubset(
        CANONICAL_RELATIONSHIPS
    )
    assert set(PROJECTION_METADATA_PROPERTIES) == {
        "_entity_type",
        "_schema_version",
        "_source_checksum",
        "_projected_at",
    }
    query_text = "\n".join(SOURCE_QUERIES.values()).casefold()
    assert all(property_name not in query_text for property_name in SENSITIVE_PROPERTIES)
